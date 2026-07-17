from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_user
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.assistant_service import AssistantService
from app.services.ollama_service import OllamaResponseError, OllamaUnavailableError

router = APIRouter(tags=["chat"], dependencies=[Depends(require_user)])

_chat_rate_limit = get_settings().chat_rate_limit


def get_assistant_service() -> AssistantService:
    """FastAPI dependency for the assistant service."""
    return AssistantService()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(_chat_rate_limit)
async def chat(
    request: Request,
    payload: ChatRequest,
    assistant: AssistantService = Depends(get_assistant_service),
    db: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Send a message to the local assistant. Thin handler only."""
    try:
        return await assistant.handle_chat(payload, db)
    except OllamaUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Local model unavailable: {exc}",
        ) from exc
    except OllamaResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Local model error: {exc}",
        ) from exc
