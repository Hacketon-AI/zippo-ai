"""OpenRouter LLM client (OpenAI-compatible API).

Drop-in replacement for OllamaService. Same interface:
  generate(prompt, *, model=None, system=None) -> {"answer": str, "model": str}

Raises OllamaUnavailableError / OllamaResponseError on failure so that
all existing error-handling in AssistantService and IntelligenceService
continues to work without changes.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.core.config import Settings, get_settings
from app.services.ollama_service import OllamaResponseError, OllamaUnavailableError

logger = logging.getLogger(__name__)

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class OpenRouterService:
    """Async OpenRouter LLM client (OpenAI-compatible)."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._api_key = self._settings.openrouter_api_key
        self._default_model = self._settings.openrouter_model
        self._timeout = self._settings.openrouter_timeout_seconds
        self._base_url = (
            self._settings.openrouter_base_url.rstrip("/")
            if self._settings.openrouter_base_url
            else _OPENROUTER_BASE
        )

    @property
    def default_model(self) -> str:
        return self._default_model

    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
    ) -> dict[str, Any]:
        """Call OpenRouter /chat/completions and return {"answer": str, "model": str}.

        Raises OllamaUnavailableError or OllamaResponseError on failure.
        """
        if not self._api_key:
            raise OllamaUnavailableError("OpenRouter API key is not configured")

        chosen_model = model or self._default_model

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": chosen_model,
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://zippoai.legaltechz.com",
            "X-Title": "Zippo AI",
            "Content-Type": "application/json",
        }

        url = f"{self._base_url}/chat/completions"

        logger.debug("OpenRouter request: model=%s url=%s", chosen_model, url)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            raise OllamaUnavailableError(
                f"Cannot reach OpenRouter at {self._base_url}"
            ) from exc
        except httpx.ReadTimeout as exc:
            raise OllamaUnavailableError("OpenRouter request timed out") from exc
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError(f"OpenRouter HTTP error: {exc}") from exc

        if response.status_code >= 400:
            raise OllamaResponseError(
                f"OpenRouter returned {response.status_code}: {response.text[:300]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaResponseError("OpenRouter returned invalid JSON") from exc

        try:
            answer = (data["choices"][0]["message"]["content"] or "").strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise OllamaResponseError(
                f"Unexpected OpenRouter response structure: {str(data)[:200]}"
            ) from exc

        if not answer:
            raise OllamaResponseError("OpenRouter returned empty response")

        logger.debug("OpenRouter response: model=%s length=%d", chosen_model, len(answer))
        return {"answer": answer, "model": chosen_model}
