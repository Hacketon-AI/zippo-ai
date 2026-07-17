from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_user
from app.db.session import get_session
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackSaveError, FeedbackService

router = APIRouter(tags=["feedback"], dependencies=[Depends(require_user)])


def _get_feedback_service() -> FeedbackService:
    return FeedbackService()


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_session),
    svc: FeedbackService = Depends(_get_feedback_service),
) -> FeedbackResponse:
    """Save a user correction to PostgreSQL and semantic memory."""
    try:
        await svc.save_correction(session=db, request=request)
        await db.commit()
    except FeedbackSaveError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save correction: {exc}",
        ) from exc
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while saving feedback",
        ) from exc

    return FeedbackResponse()
