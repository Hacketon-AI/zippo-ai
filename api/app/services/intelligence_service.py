"""Intelligence research orchestration service.

Coordinates Bright Data web search (Direct API or MCP) with local
Qwen3 AI synthesis via the existing OllamaService. Selects the
provider based on `brightdata_provider` config and falls back to
Direct API if MCP returns no results.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.core.config import get_settings
from app.schemas.intelligence import (
    BrightDataSearchResponse,
    IntelligenceMetadata,
    IntelligenceResponse,
    IntelligenceSourceItem,
)
from app.services.brightdata_mcp_service import BrightDataMCPService
from app.services.brightdata_service import BrightDataService
from app.services.ollama_service import OllamaError, OllamaService
from app.services.assistant_service import _create_llm_service

logger = logging.getLogger(__name__)

_SYNTHESIS_SYSTEM = """\
You are a research analyst. Analyze the provided web search results and produce a concise research brief.

Rules:
- Answer based ONLY on the provided sources. Do not invent facts.
- Be concise and practical.
- Include actionable recommendations.
- Return valid JSON with exactly these keys: summary, signals, recommendations.
  - summary: a short paragraph summarizing findings.
  - signals: a list of key insights or trends (strings).
  - recommendations: a list of practical next steps (strings).
- If sources are insufficient, say so in the summary.
"""

_NO_SOURCES_SUMMARY = (
    "Live research is currently unavailable because no external sources were returned."
)


class IntelligenceService:
    """Orchestrates web research + AI synthesis."""

    def __init__(
        self,
        brightdata: Optional[BrightDataService] = None,
        brightdata_mcp: Optional[BrightDataMCPService] = None,
        ollama: Optional[OllamaService] = None,
    ) -> None:
        self._brightdata = brightdata or BrightDataService()
        self._brightdata_mcp = brightdata_mcp or BrightDataMCPService()
        self._ollama = ollama or _create_llm_service()
        self._provider = get_settings().brightdata_provider

    async def research(
        self,
        query: str,
        country: Optional[str] = None,
        language: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> IntelligenceResponse:
        """Run web search and synthesize results with local AI."""

        # 1) Fetch web sources via selected provider.
        bd_result, provider_used, fallback_provider = await self._fetch_sources(
            query=query,
            country=country,
            language=language,
            max_results=max_results,
        )

        sources = [
            IntelligenceSourceItem(
                title=r.title,
                url=r.url,
                snippet=r.snippet,
                source=r.source,
            )
            for r in bd_result.results
        ]

        metadata = IntelligenceMetadata(
            result_count=bd_result.result_count,
            provider=provider_used,
            fallback_provider=fallback_provider,
            provider_error=bd_result.error,
        )

        # 2) If no sources, return safe fallback.
        if not sources:
            return IntelligenceResponse(
                query=query,
                used_brightdata=bd_result.used_brightdata,
                sources=[],
                summary=_NO_SOURCES_SUMMARY,
                signals=[],
                recommendations=[],
                metadata=metadata,
            )

        # 3) Build prompt for AI synthesis.
        prompt = self._build_synthesis_prompt(query, sources)

        # 4) Call Qwen3 via existing OllamaService.
        summary, signals, recommendations = await self._synthesize(prompt)

        return IntelligenceResponse(
            query=query,
            used_brightdata=bd_result.used_brightdata,
            sources=sources,
            summary=summary,
            signals=signals,
            recommendations=recommendations,
            metadata=metadata,
        )

    async def _fetch_sources(
        self,
        query: str,
        country: Optional[str],
        language: Optional[str],
        max_results: Optional[int],
    ) -> tuple[BrightDataSearchResponse, str, Optional[str]]:
        """Select provider, fetch results, and fallback if needed.

        Returns (response, provider_used, fallback_provider_or_None).
        """
        fallback_provider: Optional[str] = None

        if self._provider == "mcp":
            result = await self._brightdata_mcp.search_web(
                query=query,
                country=country,
                language=language,
                max_results=max_results,
            )
            # If MCP returned no results, try Direct API as fallback.
            if not result.results and self._brightdata._enabled:
                logger.info(
                    "MCP returned no results; falling back to Direct API"
                )
                result = await self._brightdata.search_web(
                    query=query,
                    country=country,
                    language=language,
                    max_results=max_results,
                )
                fallback_provider = "serp_api"
            return result, "mcp", fallback_provider

        # Default: serp_api (Direct API).
        result = await self._brightdata.search_web(
            query=query,
            country=country,
            language=language,
            max_results=max_results,
        )
        return result, "serp_api", None

    @staticmethod
    def _build_synthesis_prompt(
        query: str, sources: list[IntelligenceSourceItem]
    ) -> str:
        """Build a user prompt listing the query and source snippets."""
        lines = [f"Research query: {query}", "", "Sources:"]
        for i, s in enumerate(sources, start=1):
            lines.append(f"[{i}] {s.title}")
            lines.append(f"    URL: {s.url}")
            lines.append(f"    Snippet: {s.snippet}")
            lines.append("")
        lines.append(
            "Analyze these sources and return JSON with keys: summary, signals, recommendations."
        )
        return "\n".join(lines)

    async def _synthesize(
        self, prompt: str
    ) -> tuple[str, list[str], list[str]]:
        """Call Ollama and parse the structured response."""
        try:
            result = await self._ollama.generate(
                prompt=prompt,
                system=_SYNTHESIS_SYSTEM,
            )
            return self._parse_synthesis(result["answer"])
        except OllamaError as exc:
            logger.warning("AI synthesis failed (Ollama): %s", exc)
            return self._fallback_synthesis()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error during AI synthesis")
            return (
                f"AI synthesis encountered an error: {type(exc).__name__}",
                [],
                [],
            )

    @staticmethod
    def _parse_synthesis(
        raw: str,
    ) -> tuple[str, list[str], list[str]]:
        """Try to parse JSON from the AI response; fallback to raw text."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()

        try:
            data: dict[str, Any] = json.loads(cleaned)
            summary = str(data.get("summary") or "").strip()
            signals = [str(s) for s in (data.get("signals") or []) if s]
            recommendations = [
                str(r) for r in (data.get("recommendations") or []) if r
            ]
            return summary or raw, signals, recommendations
        except (json.JSONDecodeError, TypeError, ValueError):
            return raw, [], []

    @staticmethod
    def _fallback_synthesis() -> tuple[str, list[str], list[str]]:
        """Return a safe fallback when AI is unavailable."""
        return (
            "AI synthesis is currently unavailable. Sources were retrieved successfully.",
            [],
            ["Review the sources manually for insights."],
        )
