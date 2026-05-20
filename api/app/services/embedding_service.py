"""Async Ollama embeddings client.

Wraps the local Ollama `/api/embeddings` endpoint. Returns a single
embedding vector for an input string. Reuses the error classes from
`ollama_service` so callers can handle Ollama failures uniformly.
"""

from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import Settings, get_settings
from app.services.ollama_service import (
    OllamaResponseError,
    OllamaUnavailableError,
)


class EmbeddingService:
    """Thin async wrapper around the Ollama embeddings endpoint."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.ollama_base_url.rstrip("/")
        self._model = self._settings.ollama_embed_model
        self._timeout = self._settings.ollama_embed_timeout_seconds

    @property
    def model(self) -> str:
        return self._model

    async def embed(self, text: str, *, model: Optional[str] = None) -> list[float]:
        """Return the embedding vector for `text`.

        Raises OllamaUnavailableError on connection/timeout failures and
        OllamaResponseError on bad responses or empty embeddings.
        """
        if not text or not text.strip():
            raise ValueError("text must not be empty")

        chosen_model = model or self._model
        url = f"{self._base_url}/api/embeddings"
        payload = {"model": chosen_model, "prompt": text}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload)
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            raise OllamaUnavailableError(
                f"Cannot reach Ollama at {self._base_url}"
            ) from exc
        except httpx.ReadTimeout as exc:
            raise OllamaUnavailableError("Ollama embeddings request timed out") from exc
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

        embedding = data.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise OllamaResponseError("Ollama returned empty or invalid embedding")
        if not all(isinstance(x, (int, float)) for x in embedding):
            raise OllamaResponseError("Ollama embedding contains non-numeric values")

        return [float(x) for x in embedding]
