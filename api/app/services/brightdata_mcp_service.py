"""Bright Data MCP service skeleton.

Provides the same interface as BrightDataService but is intended to
use the @brightdata/mcp package via a subprocess/client. Currently
returns safe fallback responses only.

TODO: Implement actual MCP process spawning and tool invocation.
"""

from __future__ import annotations

from typing import Optional

from app.core.config import Settings, get_settings
from app.schemas.intelligence import (
    BrightDataSearchResponse,
)


class BrightDataMCPService:
    """Async Bright Data MCP search client (skeleton)."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._enabled = self._settings.brightdata_mcp_enabled
        self._api_key = self._settings.brightdata_api_key
        self._command = self._settings.brightdata_mcp_command
        self._package = self._settings.brightdata_mcp_package
        self._timeout = self._settings.brightdata_mcp_timeout_seconds
        self._max_results = self._settings.brightdata_mcp_max_results

    async def search_web(
        self,
        query: str,
        country: Optional[str] = None,
        language: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> BrightDataSearchResponse:
        """Search the web via Bright Data MCP.

        Returns a safe response in all cases — never raises.
        """
        if not query or not query.strip():
            return BrightDataSearchResponse(
                query=query or "",
                error="Query must not be empty",
            )

        if not self._enabled:
            return BrightDataSearchResponse(
                query=query,
                error="Bright Data MCP is disabled",
            )

        if not self._api_key:
            return BrightDataSearchResponse(
                query=query,
                error="Bright Data API key is not configured",
            )

        # TODO: Spawn MCP process using self._command and self._package,
        #       pass API key via env (BRIGHTDATA_API_KEY), invoke the
        #       search tool with query/country/language/max_results,
        #       parse the tool response, and normalize into
        #       BrightDataSearchResult items.

        return BrightDataSearchResponse(
            query=query,
            error="Bright Data MCP integration is not yet implemented",
        )
