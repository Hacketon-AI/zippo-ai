"""High-level semantic memory service.

Composes the embedding and Qdrant services so callers can simply
"remember" a piece of text or "recall" relevant memories. Pure
orchestration: no direct HTTP or DB calls live here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

DEFAULT_MEMORY_TYPE = "memory"


class MemoryService:
    """Store and retrieve semantic memories."""

    def __init__(
        self,
        embedding: Optional[EmbeddingService] = None,
        qdrant: Optional[QdrantService] = None,
    ) -> None:
        self._embedding = embedding or EmbeddingService()
        self._qdrant = qdrant or QdrantService()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _build_payload(
        text: str, payload_extra: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Build the Qdrant payload, letting `payload_extra` override defaults."""
        payload: dict[str, Any] = {
            "type": DEFAULT_MEMORY_TYPE,
            "text": text,
            "created_at": MemoryService._now_iso(),
        }
        if payload_extra:
            payload.update(payload_extra)
        return payload

    async def remember(
        self,
        text: str,
        payload_extra: Optional[dict[str, Any]] = None,
    ) -> str:
        """Embed `text` and store it as a memory point. Returns the point id."""
        if not text or not text.strip():
            raise ValueError("text must not be empty")

        vector = await self._embedding.embed(text)
        payload = self._build_payload(text.strip(), payload_extra)
        return await self._qdrant.upsert_memory(vector=vector, payload=payload)

    async def recall(
        self,
        query: str,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
        payload_filter: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Embed `query` and return matching memory hits.

        payload_filter: optional exact-match filter dict passed to Qdrant,
        e.g. {"type": "correction"}.
        """
        if not query or not query.strip():
            raise ValueError("query must not be empty")

        vector = await self._embedding.embed(query)
        return await self._qdrant.search(
            vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            payload_filter=payload_filter,
        )
