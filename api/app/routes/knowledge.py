"""Knowledge upload route.

Accepts plain text / markdown files and ingests them into the
knowledge base via DocumentService. Route is thin: validates input,
delegates to the service, manages the DB transaction.
"""

from __future__ import annotations

import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.knowledge import KnowledgeUploadResponse
from app.services.document_service import DocumentIngestError, DocumentService

router = APIRouter(tags=["knowledge"])

_MAX_FILE_BYTES = 1 * 1024 * 1024  # 1 MB
_ALLOWED_CONTENT_TYPES = {"text/plain", "text/markdown"}
_ALLOWED_EXTENSIONS = {".txt", ".md"}


def _get_document_service() -> DocumentService:
    return DocumentService()


def _parse_tags(tags_raw: Optional[str]) -> Optional[list[str]]:
    """Parse an optional JSON array string into a list of strings."""
    if tags_raw is None:
        return None
    try:
        parsed = json.loads(tags_raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tags must be a valid JSON array, e.g. [\"python\",\"fastapi\"]",
        )
    if not isinstance(parsed, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tags must be a JSON array",
        )
    if not all(isinstance(t, str) for t in parsed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="all tags must be strings",
        )
    return parsed


def _validate_file_type(file: UploadFile) -> None:
    """Reject unsupported content types and extensions."""
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    filename = (file.filename or "").lower()
    extension = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""

    allowed = (
        content_type in _ALLOWED_CONTENT_TYPES
        or (
            content_type == "application/octet-stream"
            and extension in _ALLOWED_EXTENSIONS
        )
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{content_type}'. "
                "Only text/plain and text/markdown are accepted."
            ),
        )


@router.post(
    "/knowledge/upload",
    response_model=KnowledgeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_knowledge(
    title: Annotated[str, Form()],
    file: UploadFile,
    tags: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_session),
    svc: DocumentService = Depends(_get_document_service),
) -> KnowledgeUploadResponse:
    """Upload a plain text or markdown file into the knowledge base."""
    # Validate title.
    if not title or not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title must not be empty",
        )

    # Validate file name.
    if not file.filename or not file.filename.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file name must not be empty",
        )

    # Validate content type / extension.
    _validate_file_type(file)

    # Parse optional tags.
    parsed_tags = _parse_tags(tags)

    # Read and size-check.
    raw = await file.read(_MAX_FILE_BYTES + 1)
    if len(raw) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 1 MB limit",
        )
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    # Decode UTF-8.
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be valid UTF-8 encoded text",
        )

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content is empty",
        )

    # Ingest — rollback on any service error.
    try:
        result = await svc.ingest_text(
            session=db,
            title=title.strip(),
            file_name=file.filename.strip(),
            content=content,
            source_type="upload",
            tags=parsed_tags,
        )
        await db.commit()
    except DocumentIngestError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {exc}",
        ) from exc
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during ingestion",
        ) from exc

    return KnowledgeUploadResponse(
        document_id=result["document_id"],
        chunk_count=result["chunk_count"],
    )
