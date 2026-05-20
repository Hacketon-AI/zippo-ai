"""Feedback / correction persistence service.

Saves a user correction to PostgreSQL and stores it in Qdrant semantic
memory so it can be recalled with high priority during future chats.

The caller is responsible for committing or rolling back the session.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeedbackCorrection
from app.schemas.feedback import FeedbackRequest
from app.services.memory_service import MemoryService

_CORRECTION_PRIORITY = "high"


class FeedbackSaveError(Exception):
    """Raised when saving a correction fails so the caller can rollback."""


class FeedbackService:
    """Persist user corrections and index them in semantic memory."""

    def __init__(self, memory: Optional[MemoryService] = None) -> None:
        self._memory = memory or MemoryService()

    async def save_correction(
        self,
        session: AsyncSession,
        request: FeedbackRequest,
    ) -> str:
        """Persist the correction and store it in Qdrant. Returns correction id."""
        row = FeedbackCorrection(
            question=request.question.strip(),
            wrong_answer=request.wrong_answer.strip(),
            corrected_answer=request.corrected_answer.strip(),
            category=request.category.strip() if request.category else None,
            priority=10,  # numeric high-priority sentinel
        )
        session.add(row)
        # Flush to get the id without committing.
        await session.flush()
        correction_id = row.id

        memory_payload: dict[str, Any] = {
            "type": "correction",
            "priority": _CORRECTION_PRIORITY,
            "question": row.question,
            "wrong_answer": row.wrong_answer,
            "corrected_answer": row.corrected_answer,
            "correction_id": correction_id,
        }
        if row.category:
            memory_payload["category"] = row.category

        try:
            await self._memory.remember(
                text=f"Q: {row.question}\nCorrection: {row.corrected_answer}",
                payload_extra=memory_payload,
            )
        except Exception as exc:  # noqa: BLE001
            raise FeedbackSaveError(
                f"Failed to store correction {correction_id} in memory: {exc}"
            ) from exc

        return correction_id
