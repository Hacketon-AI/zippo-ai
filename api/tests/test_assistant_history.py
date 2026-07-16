"""Tests for AssistantService history handling.

All external resources (LLM, cache, memory) are mocked; these tests
cover the orchestration rules only:
- history is forwarded to the LLM,
- requests with history bypass the exact cache (read and write),
- standalone requests still hit and populate the cache.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.schemas.chat import ChatRequest
from app.services.assistant_service import AssistantService


def _make_service() -> tuple[AssistantService, AsyncMock, AsyncMock, AsyncMock]:
    llm = AsyncMock()
    llm.generate = AsyncMock(return_value={"answer": "jawaban", "model": "qwen3:4b"})
    cache = AsyncMock()
    cache.get_cached_answer = AsyncMock(return_value=None)
    memory = AsyncMock()
    memory.recall = AsyncMock(return_value=[])
    service = AssistantService(ollama=llm, cache=cache, memory=memory)
    return service, llm, cache, memory


def _db() -> AsyncMock:
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_history_is_forwarded_to_llm() -> None:
    service, llm, _, _ = _make_service()
    request = ChatRequest(
        message="lalu kenapa?",
        use_memory=False,
        history=[
            {"role": "user", "content": "apa itu qdrant?"},
            {"role": "assistant", "content": "vector database."},
        ],
    )

    await service.handle_chat(request, _db())

    kwargs = llm.generate.call_args.kwargs
    assert kwargs["history"] == [
        {"role": "user", "content": "apa itu qdrant?"},
        {"role": "assistant", "content": "vector database."},
    ]


@pytest.mark.asyncio
async def test_followup_bypasses_cache_read_and_write() -> None:
    service, _, cache, memory = _make_service()
    request = ChatRequest(
        message="lalu?",
        use_memory=True,
        history=[{"role": "user", "content": "halo"}],
    )

    await service.handle_chat(request, _db())

    cache.get_cached_answer.assert_not_called()
    cache.save_cached_answer.assert_not_called()
    memory.remember.assert_not_called()


@pytest.mark.asyncio
async def test_standalone_request_uses_cache() -> None:
    service, llm, cache, _ = _make_service()
    request = ChatRequest(message="apa itu qdrant?", use_memory=False)

    await service.handle_chat(request, _db())

    cache.get_cached_answer.assert_called_once()
    cache.save_cached_answer.assert_called_once()
    assert llm.generate.call_args.kwargs["history"] is None
