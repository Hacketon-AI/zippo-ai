from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login payload."""

    email: str = Field(
        ..., min_length=3, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    """Successful login: bearer token plus profile basics."""

    token: str
    display_name: str
    email: str


class MeResponse(BaseModel):
    """Profile of the authenticated user."""

    display_name: str
    email: str
