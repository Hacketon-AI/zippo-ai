from typing import Optional

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Incoming feedback / correction payload."""

    question: str = Field(..., min_length=1)
    wrong_answer: str = Field(..., min_length=1)
    corrected_answer: str = Field(..., min_length=1)
    category: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response returned after a correction is saved."""

    status: str = "saved"
    message: str = "Correction saved to memory"
