"""Tests for the semantic cache step in AssistantService.

All external resources are mocked. Covers:
- a high-score chat_qa hit returns the stored answer without calling the LLM,
- no hit falls through to the LLM,
- follow-up requests skip the semantic cache,
- a semantic cache failure never breaks the chat.
"""

from __future__ import annotations

from typing import Any
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


def _chat_qa_hit(score: float = 0.97) -> dict[str, Any]:
    return {
        "score": score,
        "payload": {
            "type": "chat_qa",
            "question": "apa itu qdrant?",
            "answer": "Qdrant adalah vector database.",
        },
    }


def _recall_router(semantic_hits: list[dict[str, Any]]) -> AsyncMock:
    """Return recall mock: corrections -> [], chat_qa filter -> semantic_hits."""

    async def recall(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        payload_filter = kwargs.get("payload_filter") or {}
        if payload_filter.get("type") == "chat_qa":
            return semantic_hits
        return []

    return AsyncMock(side_effect=recall)


@pytest.mark.asyncio
async def test_semantic_cache_hit_skips_llm() -> None:
    service, llm, _, memory = _make_service()
    memory.recall = _recall_router([_chat_qa_hit()])
    request = ChatRequest(message="qdrant itu apa?", use_memory=True)

    response = await service.handle_chat(request, _db())

    assert response.answer == "Qdrant adalah vector database."
    assert response.source == "cache"
    assert response.metadata["semantic_cache_hit"] is True
    llm.generate.assert_not_called()


@pytest.mark.asyncio
async def test_semantic_cache_miss_falls_through_to_llm() -> None:
    service, llm, _, memory = _make_service()
    memory.recall = _recall_router([])
    request = ChatRequest(message="apa itu docker?", use_memory=True)

    response = await service.handle_chat(request, _db())

    assert response.source == "ollama"
    llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_followup_skips_semantic_cache() -> None:
    service, llm, _, memory = _make_service()
    memory.recall = _recall_router([_chat_qa_hit()])
    request = ChatRequest(
        message="lalu?",
        use_memory=True,
        history=[{"role": "user", "content": "halo"}],
    )

    await service.handle_chat(request, _db())

    llm.generate.assert_called_once()
    for call in memory.recall.call_args_list:
        payload_filter = call.kwargs.get("payload_filter") or {}
        assert payload_filter.get("type") != "chat_qa"


@pytest.mark.asyncio
async def test_semantic_cache_failure_does_not_break_chat() -> None:
    service, llm, _, memory = _make_service()
    memory.recall = AsyncMock(side_effect=RuntimeError("qdrant down"))
    request = ChatRequest(message="apa itu fastapi?", use_memory=True)

    response = await service.handle_chat(request, _db())

    assert response.source == "ollama"
    llm.generate.assert_called_once()
