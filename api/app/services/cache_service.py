"""Exact-match answer cache backed by PostgreSQL (`ai_cache` table).

Pure data access for the cache. No prompt logic, no model calls.
Integration into the chat flow happens in a later phase.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import AiCache
from app.utils.text_normalizer import hash_question, normalize_question


class CacheService:
    """Read/write helpers for the exact-question cache."""

    def __init__(self, default_ttl_seconds: Optional[int] = None) -> None:
        settings = get_settings()
        self._default_ttl_seconds = (
            default_ttl_seconds
            if default_ttl_seconds is not None
            else settings.cache_ttl_seconds
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _expiry_from_ttl(self, ttl_seconds: Optional[int]) -> Optional[datetime]:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl_seconds
        if ttl is None or ttl <= 0:
            return None
        return self._now() + timedelta(seconds=ttl)

    async def get_cached_answer(
        self, session: AsyncSession, question: str
    ) -> Optional[AiCache]:
        """Return a non-expired cache row for the given question, or None."""
        if not question or not question.strip():
            return None

        q_hash = hash_question(question)
        stmt = select(AiCache).where(AiCache.question_hash == q_hash).limit(1)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None

        if row.expires_at is not None and row.expires_at <= self._now():
            return None

        return row

    async def save_cached_answer(
        self,
        session: AsyncSession,
        question: str,
        answer: str,
        source_type: str = "ollama",
        ttl_seconds: Optional[int] = None,
        confidence_score: Optional[float] = None,
        source_refs: Optional[dict] = None,
    ) -> AiCache:
        """Insert or refresh a cache entry for the given question.

        Caller is responsible for committing the session.
        """
        if not question or not question.strip():
            raise ValueError("question must not be empty")
        if not answer or not answer.strip():
            raise ValueError("answer must not be empty")

        normalized = normalize_question(question)
        q_hash = hash_question(question)
        expires_at = self._expiry_from_ttl(ttl_seconds)

        stmt = select(AiCache).where(AiCache.question_hash == q_hash).limit(1)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            row = AiCache(
                question_hash=q_hash,
                normalized_question=normalized,
                answer=answer,
                source_type=source_type,
                source_refs=source_refs,
                confidence_score=confidence_score,
                expires_at=expires_at,
            )
            session.add(row)
        else:
            row.normalized_question = normalized
            row.answer = answer
            row.source_type = source_type
            row.source_refs = source_refs
            row.confidence_score = confidence_score
            row.expires_at = expires_at

        await session.flush()
        return row
