"""OpenRouter LLM client (OpenAI-compatible API).

Drop-in replacement for OllamaService. Same interface:
  generate(prompt, *, system=None) -> {"answer": str, "model": str}

Raises OllamaUnavailableError / OllamaResponseError on failure so that
all existing error-handling in AssistantService continues to work
without changes.

Auto-retries with fallback models when primary model hits 429 rate limit.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

import httpx

from app.core.config import Settings, get_settings
from app.services.ollama_service import OllamaResponseError, OllamaUnavailableError

logger = logging.getLogger(__name__)

# Fallback model chain — tried in order when primary model fails with 429 or 404
_FALLBACK_MODELS = [
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "qwen/qwen3-coder:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "z-ai/glm-4.5-air:free",
    "moonshotai/kimi-k2.6:free",
    "openai/gpt-oss-120b:free",
    "google/gemma-4-26b-a4b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
]


class OpenRouterService:
    """Async OpenRouter LLM client (OpenAI-compatible) with auto-fallback."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._api_key = self._settings.openrouter_api_key
        self._default_model = self._settings.openrouter_model
        self._timeout = self._settings.openrouter_timeout_seconds
        self._base_url = self._settings.openrouter_base_url.rstrip("/")

    async def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """Call OpenRouter /chat/completions and return {"answer": str, "model": str}.

        history: prior turns as [{"role": ..., "content": ...}], oldest first.
        Automatically retries with fallback models on 429 rate limit errors.
        Raises OllamaUnavailableError or OllamaResponseError if all models fail.
        """
        if not self._api_key:
            raise OllamaUnavailableError("OpenRouter API key is not configured")

        # Build model list: primary first, then fallbacks (excluding primary)
        primary = self._default_model
        candidates = [primary] + [m for m in _FALLBACK_MODELS if m != primary]

        last_error: Optional[Exception] = None

        for candidate_model in candidates:
            try:
                result = await self._call_model(candidate_model, prompt, system, history)
                if candidate_model != primary:
                    logger.info(
                        "OpenRouter: used fallback model %s (primary %s failed)",
                        candidate_model,
                        primary,
                    )
                return result
            except OllamaResponseError as exc:
                # 429 = rate limit, 404 = model not available -> try next model
                err_str = str(exc)
                if "429" in err_str or "404" in err_str:
                    logger.warning(
                        "OpenRouter model %s unavailable (%s), trying next...",
                        candidate_model,
                        "429 rate-limit" if "429" in err_str else "404 not found",
                    )
                    last_error = exc
                    continue
                # Other response errors are fatal
                raise
            except OllamaUnavailableError:
                raise

        # All models exhausted
        raise OllamaResponseError(
            f"All OpenRouter models rate-limited. Last error: {last_error}"
        )

    async def _call_model(
        self,
        chosen_model: str,
        prompt: str,
        system: Optional[str],
        history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """Make a single OpenRouter API call for the given model."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
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

        # Strip thinking blocks (some models leak <think> even when not requested).
        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
        answer = re.sub(r"^.*?</think>\s*", "", answer, flags=re.DOTALL).strip()

        if not answer:
            raise OllamaResponseError("OpenRouter returned empty response")

        logger.debug(
            "OpenRouter response: model=%s length=%d", chosen_model, len(answer)
        )
        return {"answer": answer, "model": chosen_model}
