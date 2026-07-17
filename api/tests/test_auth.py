"""Tests for the auth flow: login, token validation, protected routes.

The database is faked at the service level (AsyncMock on session.execute)
so no Postgres is needed. Route-level protection is exercised through the
FastAPI dependency system with a real require_user (no override).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.models import User, UserSession
from app.db.session import get_session
from app.main import app
from app.services.auth_service import (
    AuthError,
    AuthService,
    _hash_token,
    hash_password,
)


def _user(password: str = "rahasia123") -> User:
    return User(
        id="u-1",
        email="agung@test.com",
        password_hash=hash_password(password),
        display_name="Bang Agung",
    )


def _db_returning(*results: object) -> AsyncMock:
    """AsyncSession stub whose execute() yields the given scalars in order."""
    db = AsyncMock()
    db.add = MagicMock()  # session.add is sync in SQLAlchemy
    mocks = []
    for value in results:
        result = MagicMock()
        result.scalar_one_or_none.return_value = value
        mocks.append(result)
    db.execute = AsyncMock(side_effect=mocks)
    return db


# ---------- AuthService ----------


@pytest.mark.asyncio
async def test_login_success_returns_token() -> None:
    service = AuthService()
    db = _db_returning(_user())

    user, token = await service.login(db, "agung@test.com", "rahasia123")

    assert user.email == "agung@test.com"
    assert len(token) > 30
    db.add.assert_called_once()
    added: UserSession = db.add.call_args.args[0]
    assert added.token_hash == _hash_token(token)


@pytest.mark.asyncio
async def test_login_wrong_password_raises() -> None:
    service = AuthService()
    db = _db_returning(_user())

    with pytest.raises(AuthError):
        await service.login(db, "agung@test.com", "salah")


@pytest.mark.asyncio
async def test_login_unknown_email_raises() -> None:
    service = AuthService()
    db = _db_returning(None)

    with pytest.raises(AuthError):
        await service.login(db, "ghost@test.com", "apapun")


@pytest.mark.asyncio
async def test_expired_session_is_rejected() -> None:
    service = AuthService()
    expired = UserSession(
        token_hash=_hash_token("token-abc"),
        user_id="u-1",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db = _db_returning(expired)

    assert await service.get_user_by_token(db, "token-abc") is None


@pytest.mark.asyncio
async def test_valid_session_returns_user() -> None:
    service = AuthService()
    session = UserSession(
        token_hash=_hash_token("token-abc"),
        user_id="u-1",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db = _db_returning(session, _user())

    user = await service.get_user_by_token(db, "token-abc")
    assert user is not None and user.id == "u-1"


# ---------- Route protection ----------


class _StubSession:
    async def commit(self) -> None:  # pragma: no cover
        pass

    async def rollback(self) -> None:  # pragma: no cover
        pass

    async def execute(self, *args: object) -> MagicMock:
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        return result


async def _stub_get_session() -> AsyncIterator[_StubSession]:
    yield _StubSession()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_session] = _stub_get_session
    try:
        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def test_chat_requires_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat", json={"message": "hai", "use_memory": False}
    )
    assert response.status_code == 401


def test_chat_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={"message": "hai", "use_memory": False},
        headers={"Authorization": "Bearer token-palsu"},
    )
    assert response.status_code == 401


def test_feedback_requires_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/feedback",
        json={
            "question": "q",
            "wrong_answer": "w",
            "corrected_answer": "c",
        },
    )
    assert response.status_code == 401


def test_health_stays_public(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_login_route_wrong_credentials_returns_401(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@test.com", "password": "apapun"},
    )
    assert response.status_code == 401
