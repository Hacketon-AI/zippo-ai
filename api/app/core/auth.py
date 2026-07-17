"""Auth dependency for protected routes.

Reads `Authorization: Bearer <token>` and resolves it to a User via
AuthService. Raises 401 when the token is missing, invalid, or expired.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_session
from app.services.auth_service import AuthService

_auth_service = AuthService()


def _extract_bearer(request: Request) -> str:
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token.strip()


async def require_user(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> User:
    """FastAPI dependency: return the authenticated user or raise 401."""
    token = _extract_bearer(request)
    user = await _auth_service.get_user_by_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
