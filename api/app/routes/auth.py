"""Auth routes: login, logout, me. Thin handlers only."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import _extract_bearer, require_user
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import User
from app.db.session import get_session
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.services.auth_service import AuthError, AuthService

router = APIRouter(tags=["auth"])

_login_rate_limit = get_settings().login_rate_limit


def get_auth_service() -> AuthService:
    """FastAPI dependency for the auth service."""
    return AuthService()


@router.post("/auth/login", response_model=LoginResponse)
@limiter.limit(_login_rate_limit)
async def login(
    request: Request,
    payload: LoginRequest,
    auth: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_session),
) -> LoginResponse:
    """Verify credentials and return a bearer token."""
    try:
        user, token = await auth.login(db, payload.email, payload.password)
        await db.commit()
    except AuthError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return LoginResponse(
        token=token, display_name=user.display_name, email=user.email
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    auth: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_session),
) -> None:
    """Revoke the current session token. Idempotent."""
    token = _extract_bearer(request)
    await auth.logout(db, token)
    await db.commit()


@router.get("/auth/me", response_model=MeResponse)
async def me(user: User = Depends(require_user)) -> MeResponse:
    """Return the authenticated user's profile."""
    return MeResponse(display_name=user.display_name, email=user.email)
