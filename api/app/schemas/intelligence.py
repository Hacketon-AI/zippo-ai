"""Schemas for the intelligence / Bright Data search feature."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

IntelligenceSource = Literal["brightdata", "cache", "none"]


class BrightDataSearchResult(BaseModel):
    """A single normalized search result."""

    title: str
    url: str
    snippet: str
    source: IntelligenceSource = "brightdata"


class BrightDataSearchResponse(BaseModel):
    """Response from BrightDataService.search_web()."""

    used_brightdata: bool = False
    results: list[BrightDataSearchResult] = Field(default_factory=list)
    error: Optional[str] = None
    query: str = ""
    result_count: int = 0


# --- Intelligence route schemas ---


class IntelligenceRequest(BaseModel):
    """Request body for POST /intelligence/research."""

    query: str = Field(..., min_length=3, max_length=500)
    country: Optional[str] = None
    language: Optional[str] = None
    max_results: Optional[int] = Field(None, ge=1, le=20)
    track: Optional[Literal["GTM", "Finance", "Security", "General"]] = "General"
    company: Optional[str] = None
    competitors: Optional[str] = None
    max_sources: Optional[int] = Field(None, ge=1, le=20)
    use_brightdata: Optional[bool] = None


class IntelligenceSourceItem(BaseModel):
    """A source entry in the intelligence response."""

    title: str
    url: str
    snippet: str
    source: IntelligenceSource = "brightdata"


class IntelligenceSignal(BaseModel):
    """A single intelligence signal object."""

    title: str
    category: str
    confidence: Literal["high", "medium", "low"]
    description: str
    source_urls: list[str] = Field(default_factory=list)


class IntelligenceMetadata(BaseModel):
    """Metadata block for the intelligence response."""

    used_brightdata: bool = False
    saved_to_memory: bool = False
    source_count: int = 0
    track: str = "General"
    result_count: int = 0
    provider: Optional[str] = None
    fallback_provider: Optional[str] = None
    provider_error: Optional[str] = None


class IntelligenceResponse(BaseModel):
    """Response body for POST /intelligence/research."""

    query: str
    used_brightdata: bool = False
    sources: list[IntelligenceSourceItem] = Field(default_factory=list)
    executive_summary: str
    summary: Optional[str] = None  # Deprecated backward compatibility fallback
    signals: list[IntelligenceSignal] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: IntelligenceMetadata = Field(default_factory=IntelligenceMetadata)

