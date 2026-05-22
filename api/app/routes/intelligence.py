"""Intelligence research route.

Provides web research via Bright Data SERP API with AI synthesis
powered by local Qwen3 via OllamaService.
"""

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.schemas.intelligence import (
    IntelligenceRequest,
    IntelligenceResponse,
)
from app.services.intelligence_service import IntelligenceService

router = APIRouter(tags=["intelligence"])

_intelligence_rate_limit = get_settings().intelligence_rate_limit


@router.post("/intelligence/research", response_model=IntelligenceResponse)
@limiter.limit(_intelligence_rate_limit)
async def research(
    request: Request,
    payload: IntelligenceRequest,
) -> IntelligenceResponse:
    """Research a topic using web sources and local AI synthesis."""
    svc = IntelligenceService()
    return await svc.research(
        query=payload.query,
        country=payload.country,
        language=payload.language,
        max_results=payload.max_results,
    )
