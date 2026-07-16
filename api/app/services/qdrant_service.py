"""Qdrant client wrapper.

Provides a small async-friendly interface for the assistant's semantic
memory collection. Heavy work runs in a thread via `asyncio.to_thread`
because qdrant-client's primary API is synchronous.

No collection is created or contacted at import time.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import (
    ResponseHandlingException,
    UnexpectedResponse,
)

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class QdrantError(Exception):
    """Base error for Qdrant interactions."""


class QdrantUnavailableError(QdrantError):
    """Raised when Qdrant cannot be reached or returns an unexpected response."""


class QdrantService:
    """Thin wrapper around qdrant-client for the personal AI memory."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        client: Optional[QdrantClient] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._collection = self._settings.qdrant_collection
        self._vector_size = self._settings.qdrant_vector_size
        self._default_limit = self._settings.qdrant_search_limit
        self._default_threshold = self._settings.qdrant_score_threshold
        self._client = client  # lazy-init

    def _get_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(url=self._settings.qdrant_url)
        return self._client

    @staticmethod
    def _validate_vector(vector: list[float]) -> None:
        if not isinstance(vector, list) or not vector:
            raise ValueError("vector must be a non-empty list of floats")
        if not all(isinstance(x, (int, float)) for x in vector):
            raise ValueError("vector must contain only numeric values")

    async def ensure_collection(self) -> None:
        """Create the memory collection if it does not exist."""

        def _ensure() -> None:
            client = self._get_client()
            existing = {c.name for c in client.get_collections().collections}
            if self._collection in existing:
                return
            client.create_collection(
                collection_name=self._collection,
                vectors_config=qmodels.VectorParams(
                    size=self._vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )

        try:
            await asyncio.to_thread(_ensure)
        except (UnexpectedResponse, ResponseHandlingException) as exc:
            raise QdrantUnavailableError(f"Qdrant ensure_collection failed: {exc}") from exc

    async def upsert_memory(
        self,
        vector: list[float],
        payload: dict[str, Any],
        point_id: Optional[str] = None,
    ) -> str:
        """Upsert a single point and return its id."""
        self._validate_vector(vector)
        if len(vector) != self._vector_size:
            raise ValueError(
                f"vector size {len(vector)} does not match configured "
                f"qdrant_vector_size {self._vector_size}"
            )

        pid = point_id or str(uuid.uuid4())

        def _upsert() -> None:
            client = self._get_client()
            client.upsert(
                collection_name=self._collection,
                points=[
                    qmodels.PointStruct(id=pid, vector=vector, payload=payload),
                ],
            )

        try:
            await asyncio.to_thread(_upsert)
        except (UnexpectedResponse, ResponseHandlingException) as exc:
            raise QdrantUnavailableError(f"Qdrant upsert failed: {exc}") from exc

        return pid

    async def search(
        self,
        vector: list[float],
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
        payload_filter: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search the collection and return a list of {id, score, payload}.

        payload_filter: optional dict of exact-match conditions applied to
        payload fields, e.g. {"type": "correction"}.
        """
        self._validate_vector(vector)
        if len(vector) != self._vector_size:
            raise ValueError(
                f"vector size {len(vector)} does not match configured "
                f"qdrant_vector_size {self._vector_size}"
            )

        effective_limit = limit if limit is not None else self._default_limit
        effective_threshold = (
            score_threshold if score_threshold is not None else self._default_threshold
        )

        query_filter = self._build_filter(payload_filter)

        def _search() -> list[qmodels.ScoredPoint]:
            client = self._get_client()
            return client.search(
                collection_name=self._collection,
                query_vector=vector,
                limit=effective_limit,
                score_threshold=effective_threshold,
                query_filter=query_filter,
                with_payload=True,
            )

        try:
            results = await asyncio.to_thread(_search)
        except (UnexpectedResponse, ResponseHandlingException) as exc:
            raise QdrantUnavailableError(f"Qdrant search failed: {exc}") from exc

        return [
            {"id": str(r.id), "score": float(r.score), "payload": r.payload or {}}
            for r in results
        ]

    @staticmethod
    def _build_filter(
        payload_filter: Optional[dict[str, Any]],
    ) -> Optional[qmodels.Filter]:
        """Convert a simple {key: value} dict into a Qdrant Filter with must conditions."""
        if not payload_filter:
            return None
        conditions = [
            qmodels.FieldCondition(
                key=key,
                match=qmodels.MatchValue(value=value),
            )
            for key, value in payload_filter.items()
        ]
        return qmodels.Filter(must=conditions)
