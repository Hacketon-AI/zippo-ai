"""Async Ollama HTTP client.

Talks to a local Ollama server via the /api/generate endpoint.
Keeps surface area small: one method to generate a single answer.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from app.core.config import Settings, get_settings


class OllamaError(Exception):
    """Base error for Ollama interactions."""


class OllamaUnavailableError(OllamaError):
    """Raised when Ollama cannot be reached (connection/timeout)."""


class OllamaResponseError(OllamaError):
    """Raised when Ollama returns a non-success response."""


class OllamaService:
    """Thin async wrapper around the Ollama HTTP API."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.ollama_base_url.rstrip("/")
        self._timeout = self._settings.ollama_timeout_seconds
        self._default_model = self._settings.ollama_default_model

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
        """Call Ollama /api/generate and return the parsed payload.

        Returns a dict with at least: {"answer": str, "model": str}.
        Raises OllamaUnavailableError or OllamaResponseError on failure.
        """
        chosen_model = model or self._default_model
        payload: dict[str, Any] = {
            "model": chosen_model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        url = f"{self._base_url}/api/generate"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload)
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            raise OllamaUnavailableError(
                f"Cannot reach Ollama at {self._base_url}"
            ) from exc
        except httpx.ReadTimeout as exc:
            raise OllamaUnavailableError("Ollama request timed out") from exc
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError(f"Ollama HTTP error: {exc}") from exc

        if response.status_code >= 400:
            raise OllamaResponseError(
                f"Ollama returned {response.status_code}: {response.text[:200]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaResponseError("Ollama returned invalid JSON") from exc

        answer = (data.get("response") or "").strip()
        if not answer:
            raise OllamaResponseError("Ollama returned empty response")

        return {"answer": answer, "model": chosen_model}
