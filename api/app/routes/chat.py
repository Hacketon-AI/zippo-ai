from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.assistant_service import AssistantService
from app.services.ollama_service import OllamaResponseError, OllamaUnavailableError

router = APIRouter(tags=["chat"])


def get_assistant_service() -> AssistantService:
    """FastAPI dependency for the assistant service."""
    return AssistantService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    assistant: AssistantService = Depends(get_assistant_service),
    db: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Send a message to the local assistant. Thin handler only."""
    try:
        return await assistant.handle_chat(request, db)
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
