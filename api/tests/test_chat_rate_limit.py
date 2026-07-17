"""Rate limit test for POST /api/v1/chat.

Stubs out the assistant service and DB session so the test does not
require Postgres, Qdrant, or Ollama. Sends 12 requests and asserts
that requests beyond the configured limit return HTTP 429.
"""

from __future__ import annotations

from typing import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import require_user
from app.db.session import get_session
from app.main import app
from app.routes.chat import get_assistant_service
from app.schemas.chat import ChatResponse


class _StubSession:
    """Minimal stand-in that satisfies the chat route signature."""

    async def commit(self) -> None:  # pragma: no cover - unused
        pass

    async def rollback(self) -> None:  # pragma: no cover - unused
        pass


async def _stub_get_session() -> AsyncIterator[_StubSession]:
    yield _StubSession()


def _stub_assistant() -> object:
    stub = AsyncMock()
    stub.handle_chat = AsyncMock(
        return_value=ChatResponse(
            answer="ok",
            source="ollama",
            session_id="test-session",
            metadata={"cache_hit": False},
        )
    )
    return stub


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_session] = _stub_get_session
    app.dependency_overrides[get_assistant_service] = _stub_assistant
    app.dependency_overrides[require_user] = lambda: object()
    try:
        # Reset slowapi storage so each test starts with a clean window.
        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def test_chat_rate_limit_returns_429_after_limit(client: TestClient) -> None:
    """First 5 requests succeed, requests beyond the limit return 429."""
    payload = {"message": "hai", "mode": "local_only", "use_memory": False}
    statuses = []
    for _ in range(12):
        response = client.post("/api/v1/chat", json=payload)
        statuses.append(response.status_code)

    # The configured limit in conftest.py is 5/minute.
    success = [s for s in statuses if s == 200]
    too_many = [s for s in statuses if s == 429]

    assert len(success) <= 5, f"Expected at most 5 successes, got {len(success)}"
    assert len(too_many) >= 1, f"Expected at least one 429, got statuses={statuses}"
