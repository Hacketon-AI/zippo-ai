"""Knowledge document ingestion service.

Persists document metadata in PostgreSQL and pushes chunked content
into the semantic memory (Qdrant) via MemoryService.

The service flushes to obtain the document id, but the caller is
responsible for committing or rolling back the database transaction.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import KnowledgeDocument
from app.services.memory_service import MemoryService
from app.utils.chunk_text import chunk_text


class DocumentIngestError(Exception):
    """Raised when ingestion fails so the caller can rollback."""


class DocumentService:
    """Ingest plain text / markdown documents into the knowledge base."""

    def __init__(self, memory: Optional[MemoryService] = None) -> None:
        self._memory = memory or MemoryService()

    async def ingest_text(
        self,
        session: AsyncSession,
        title: str,
        file_name: str,
        content: str,
        source_type: str = "upload",
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Persist a document and embed its chunks into semantic memory."""
        if not title or not title.strip():
            raise ValueError("title must not be empty")
        if not file_name or not file_name.strip():
            raise ValueError("file_name must not be empty")
        if not content or not content.strip():
            raise ValueError("content must not be empty")

        document = KnowledgeDocument(
            title=title.strip(),
            file_name=file_name.strip(),
            file_path=file_name.strip(),
            source_type=source_type,
            tags=tags,
        )
        session.add(document)
        # Flush to obtain a server-assigned id without committing.
        await session.flush()
        document_id = document.id

        chunks = chunk_text(content)

        point_ids: list[str] = []
        try:
            for index, chunk in enumerate(chunks):
                payload_extra = {
                    "type": "knowledge",
                    "document_id": document_id,
                    "title": document.title,
                    "file_name": document.file_name,
                    "source_type": source_type,
                    "chunk_index": index,
                    "text": chunk,
                }
                if tags:
                    payload_extra["tags"] = tags
                point_id = await self._memory.remember(
                    text=chunk, payload_extra=payload_extra
                )
                point_ids.append(point_id)
        except Exception as exc:  # noqa: BLE001 - bubble up cleanly to caller
            raise DocumentIngestError(
                f"Failed to embed chunks for document {document_id}: {exc}"
            ) from exc

        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "point_ids": point_ids,
        }
