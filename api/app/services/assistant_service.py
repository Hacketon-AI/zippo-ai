"""Assistant orchestration layer.

Flow (Phase 6C):
1. Check correction memory (high-confidence corrections skip everything).
2. Check exact PostgreSQL cache.
3. On cache miss: optionally recall semantic memory from Qdrant.
4. Call local Ollama (with memory context as system prompt when available).
5. Save the answer to the PostgreSQL cache.
6. Store the Q/A pair into Qdrant memory for future recall.

Memory and cache failures never break the chat response.
External fallback is added in a later phase.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.cache_service import CacheService
from app.services.external_fallback_service import (
    ExternalFallbackError,
    ExternalFallbackService,
)
from app.services.memory_service import MemoryService
from app.services.ollama_service import OllamaError, OllamaService

logger = logging.getLogger(__name__)

# How many top memory hits to feed the model as context.
_MAX_MEMORY_CONTEXT = 3

# Correction recall settings.
_CORRECTION_SCORE_THRESHOLD = 0.90
_CORRECTION_LIMIT = 1
_CORRECTION_FILTER = {"type": "correction"}


class AssistantService:
    """Coordinates chat requests across the assistant's resources."""

    def __init__(
        self,
        ollama: Optional[OllamaService] = None,
        cache: Optional[CacheService] = None,
        memory: Optional[MemoryService] = None,
        fallback: Optional[ExternalFallbackService] = None,
    ) -> None:
        self._ollama = ollama or OllamaService()
        self._cache = cache or CacheService()
        self._memory = memory or MemoryService()
        self._fallback = fallback or ExternalFallbackService()

    async def handle_chat(
        self,
        request: ChatRequest,
        db: AsyncSession,
    ) -> ChatResponse:
        """Process a chat request and return a structured response."""
        session_id = request.session_id or str(uuid.uuid4())

        # 1) Correction memory — highest priority.
        correction_error = False
        if request.use_memory:
            try:
                correction_hits = await self._memory.recall(
                    request.message,
                    limit=_CORRECTION_LIMIT,
                    score_threshold=_CORRECTION_SCORE_THRESHOLD,
                    payload_filter=_CORRECTION_FILTER,
                )
            except Exception:  # noqa: BLE001
                logger.exception("Correction memory recall failed; continuing")
                correction_hits = []
                correction_error = True

            if correction_hits:
                top = correction_hits[0]
                payload = top.get("payload") or {}
                corrected_answer = (payload.get("corrected_answer") or "").strip()
                if corrected_answer:
                    return ChatResponse(
                        answer=corrected_answer,
                        source="cache",
                        session_id=session_id,
                        metadata={
                            "mode": request.mode,
                            "correction_hit": True,
                            "cache_hit": False,
                            "used_memory": True,
                            "memory_hit_count": 1,
                            "similarity_score": top["score"],
                        },
                    )

        # 2) Exact PostgreSQL cache.
        cached = await self._cache.get_cached_answer(db, request.message)
        if cached is not None:
            metadata: dict[str, Any] = {
                "mode": request.mode,
                "cache_hit": True,
                "used_memory": False,
                "memory_hit_count": 0,
                "similarity_score": None,
                "source_type": cached.source_type,
            }
            if correction_error:
                metadata["correction_error"] = True
            return ChatResponse(
                answer=cached.answer,
                source="cache",
                session_id=session_id,
                metadata=metadata,
            )

        # 3) Optional semantic memory recall.
        memory_hits: list[dict[str, Any]] = []
        memory_error = False
        if request.use_memory:
            try:
                memory_hits = await self._memory.recall(request.message)
            except Exception:  # noqa: BLE001
                logger.exception("Memory recall failed; continuing without memory")
                memory_error = True
                memory_hits = []

        system_prompt = self._build_system_prompt(memory_hits)
        used_memory = bool(memory_hits)
        top_score = memory_hits[0]["score"] if memory_hits else None

        # 4) Call Ollama.
        result: Optional[dict[str, Any]] = None
        ollama_error = False
        try:
            result = await self._ollama.generate(
                prompt=request.message,
                system=system_prompt,
            )
        except OllamaError:
            logger.exception("Ollama generation failed")
            ollama_error = True

        # 4b) External fallback — only when Ollama failed, mode allows it, and enabled.
        used_fallback = False
        if ollama_error and request.mode == "external_allowed" and self._fallback.enabled:
            try:
                fallback_answer = await self._fallback.generate(
                    message=request.message,
                    context=system_prompt,
                )
                result = {"answer": fallback_answer, "model": "external"}
                used_fallback = True
            except ExternalFallbackError:
                logger.exception("External fallback also failed")

        # If both Ollama and fallback failed, re-raise so the route returns 503.
        if result is None:
            from app.services.ollama_service import OllamaUnavailableError
            raise OllamaUnavailableError("Local model failed and no fallback available")

        metadata = {
            "model": result["model"],
            "mode": request.mode,
            "cache_hit": False,
            "used_memory": used_memory,
            "memory_hit_count": len(memory_hits),
            "similarity_score": top_score,
            "used_context": used_memory,
            "used_fallback": used_fallback,
        }
        if correction_error:
            metadata["correction_error"] = True
        if memory_error:
            metadata["memory_error"] = True

        # 5) Save to PostgreSQL exact cache.
        cache_source = "external" if used_fallback else "ollama"
        try:
            await self._cache.save_cached_answer(
                db,
                question=request.message,
                answer=result["answer"],
                source_type=cache_source,
            )
            await db.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to save chat answer to cache")
            await db.rollback()
            metadata["cache_save_error"] = True

        # 6) Store Q/A pair into Qdrant memory (best-effort).
        try:
            await self._memory.remember(
                text=f"Q: {request.message}\nA: {result['answer']}",
                payload_extra={
                    "type": "chat_qa",
                    "question": request.message,
                    "answer": result["answer"],
                    "model": result["model"],
                },
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to save chat answer to semantic memory")
            metadata["memory_save_error"] = True

        return ChatResponse(
            answer=result["answer"],
            source="external" if used_fallback else "ollama",
            session_id=session_id,
            metadata=metadata,
        )

    @staticmethod
    def _build_system_prompt(hits: list[dict[str, Any]]) -> Optional[str]:
        """Build a compact system prompt from top memory hits, if any."""
        if not hits:
            return None
        top = hits[:_MAX_MEMORY_CONTEXT]
        lines = ["Relevant memory context (most relevant first):"]
        for i, hit in enumerate(top, start=1):
            payload = hit.get("payload") or {}
            text = (payload.get("text") or "").strip()
            if not text:
                continue
            lines.append(f"[{i}] {text}")
        if len(lines) == 1:
            return None
        lines.append(
            "Use the context only if it is relevant. "
            "If it does not help, ignore it and answer from general knowledge."
        )
        return "\n".join(lines)
