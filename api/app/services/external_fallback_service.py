"""External API fallback service skeleton.

Disabled by default. When enabled and implemented, this service will
call an external LLM provider (e.g. Groq, OpenRouter, Claude) only
when local Ollama fails and the user explicitly allows external mode.

Phase 7A: skeleton only — no real API calls are made.
"""

from __future__ import annotations

from typing import Optional

from app.core.config import Settings, get_settings


class ExternalFallbackError(Exception):
    """Base error for external fallback interactions."""


class ExternalFallbackDisabledError(ExternalFallbackError):
    """Raised when fallback is called but the feature is disabled."""


class ExternalFallbackUnavailableError(ExternalFallbackError):
    """Raised when the external provider cannot be reached."""


class ExternalFallbackService:
    """Skeleton for external LLM fallback.

    Currently raises ExternalFallbackDisabledError on every call.
    Real provider integration will be added in a future phase.
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._enabled = self._settings.external_fallback_enabled
        self._provider = self._settings.external_fallback_provider
        self._timeout = self._settings.external_fallback_timeout_seconds

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def generate(
        self,
        message: str,
        context: Optional[str] = None,
    ) -> str:
        """Generate an answer using an external LLM provider.

        Raises ExternalFallbackDisabledError if the feature is off.
        Raises ExternalFallbackUnavailableError when no provider is configured.
        """
        if not self._enabled:
            raise ExternalFallbackDisabledError(
                "External fallback is disabled. Set EXTERNAL_FALLBACK_ENABLED=true to enable."
            )

        if not self._provider or self._provider == "none":
            raise ExternalFallbackUnavailableError(
                "No external fallback provider configured. "
                "Set EXTERNAL_FALLBACK_PROVIDER to a supported value."
            )

        # TODO: Implement real provider calls (groq, openrouter, claude) in Phase 7B.
        raise ExternalFallbackUnavailableError(
            f"Provider '{self._provider}' is not yet implemented."
        )
