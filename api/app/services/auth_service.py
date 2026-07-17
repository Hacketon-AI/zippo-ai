"""Authentication service: password verification and session tokens.

Users are provisioned by the create_user seeder script (no signup flow).
Tokens are random URL-safe strings; only their SHA-256 hash is stored,
so a database leak does not leak usable tokens.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import User, UserSession


class AuthError(Exception):
    """Raised when login credentials are invalid."""


def hash_password(password: str) -> str:
    """Return the bcrypt hash for a plaintext password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("ascii")
        )
    except ValueError:
        return False


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AuthService:
    """Login, session validation, and logout."""

    def __init__(self) -> None:
        self._session_ttl = timedelta(
            hours=get_settings().auth_session_ttl_hours
        )

    async def login(
        self, db: AsyncSession, email: str, password: str
    ) -> tuple[User, str]:
        """Verify credentials and open a session. Returns (user, raw token).

        Raises AuthError on unknown email or wrong password. Caller commits.
        """
        stmt = select(User).where(User.email == email.strip().lower()).limit(1)
        user = (await db.execute(stmt)).scalar_one_or_none()
        # Hash even on unknown email so response time does not reveal
        # whether the account exists.
        supplied_hash = user.password_hash if user else hash_password("invalid")
        if user is None or not _verify_password(password, supplied_hash):
            raise AuthError("Email atau password salah")

        token = secrets.token_urlsafe(32)
        db.add(
            UserSession(
                token_hash=_hash_token(token),
                user_id=user.id,
                expires_at=_now() + self._session_ttl,
            )
        )
        await db.flush()
        return user, token

    async def get_user_by_token(
        self, db: AsyncSession, token: str
    ) -> Optional[User]:
        """Return the user for a valid, non-expired token, else None."""
        if not token:
            return None
        stmt = (
            select(UserSession)
            .where(UserSession.token_hash == _hash_token(token))
            .limit(1)
        )
        session = (await db.execute(stmt)).scalar_one_or_none()
        if session is None or session.expires_at <= _now():
            return None
        user_stmt = select(User).where(User.id == session.user_id).limit(1)
        return (await db.execute(user_stmt)).scalar_one_or_none()

    async def logout(self, db: AsyncSession, token: str) -> None:
        """Revoke the session for a token. Idempotent. Caller commits."""
        await db.execute(
            delete(UserSession).where(
                UserSession.token_hash == _hash_token(token)
            )
        )
