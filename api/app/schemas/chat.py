from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

ChatMode = Literal["auto", "local_only", "external_allowed"]
ChatSource = Literal["cache", "memory", "ollama", "external"]


class ChatHistoryMessage(BaseModel):
    """One prior turn in the conversation, provided by the client."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    """Incoming chat request payload."""

    message: str = Field(..., min_length=1, max_length=8000)
    session_id: Optional[str] = None
    mode: ChatMode = "auto"
    use_memory: bool = True
    # Prior turns (oldest first). Follow-up questions depend on this context,
    # so requests with history bypass the exact-answer cache.
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    """Chat response payload."""

    answer: str
    source: ChatSource
    session_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)
