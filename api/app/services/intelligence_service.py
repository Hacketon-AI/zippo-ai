"""Intelligence research orchestration service.

Coordinates Bright Data web search (Direct API or MCP) with local
Qwen3 AI synthesis via the existing OllamaService. Selects the
provider based on `brightdata_provider` config and falls back to
Direct API if MCP returns no results.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal, Optional

from app.core.config import get_settings
from app.schemas.intelligence import (
    BrightDataSearchResponse,
    IntelligenceMetadata,
    IntelligenceResponse,
    IntelligenceSourceItem,
    IntelligenceSignal,
)
from app.services.brightdata_mcp_service import BrightDataMCPService
from app.services.brightdata_service import BrightDataService
from app.services.ollama_service import OllamaError, OllamaService
from app.services.assistant_service import _create_llm_service
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

_SYNTHESIS_SYSTEM = """\
You are a research analyst. Analyze the provided web search results and produce a structured research brief.

Rules:
- Answer based ONLY on the provided sources. Do not invent facts.
- Be concise and practical.
- Include actionable recommendations.
- Return valid JSON with exactly these keys: executive_summary, signals, recommendations.
  - executive_summary: a short paragraph summarizing findings.
  - signals: a list of key insights or trends. Each signal MUST be a JSON object with:
    - title: a concise title for the signal.
    - category: the domain/category (matches the Research Track, e.g. GTM, Finance, Security, General).
    - confidence: confidence level based on source reliability (exactly one of: "high", "medium", "low").
    - description: a short detailed explanation of the signal.
    - source_urls: a list of URLs (from the provided sources) that support this signal.
  - recommendations: a list of practical next steps (strings).
- If sources are insufficient, say so in the executive_summary and return empty lists for signals and recommendations.
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
        memory: Optional[MemoryService] = None,
    ) -> None:
        self._brightdata = brightdata or BrightDataService()
        self._brightdata_mcp = brightdata_mcp or BrightDataMCPService()
        self._ollama = ollama or _create_llm_service()
        self._memory = memory or MemoryService()
        self._provider = get_settings().brightdata_provider

    async def research(
        self,
        query: str,
        country: Optional[str] = None,
        language: Optional[str] = None,
        max_results: Optional[int] = None,
        track: str = "General",
        company: Optional[str] = None,
        competitors: Optional[str] = None,
        use_brightdata: Optional[bool] = None,
    ) -> IntelligenceResponse:
        """Run web search and synthesize results with local AI."""

        # 1) Fetch web sources via selected provider.
        bd_result, provider_used, fallback_provider = await self._fetch_sources(
            query=query,
            country=country,
            language=language,
            max_results=max_results,
            use_brightdata=use_brightdata,
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
            used_brightdata=bd_result.used_brightdata,
            saved_to_memory=False,
            source_count=len(sources),
            track=track,
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
                executive_summary=_NO_SOURCES_SUMMARY,
                summary=_NO_SOURCES_SUMMARY,
                signals=[],
                recommendations=[],
                metadata=metadata,
            )

        # 3) Build prompt for AI synthesis.
        prompt = self._build_synthesis_prompt(
            query=query,
            sources=sources,
            track=track,
            company=company,
            competitors=competitors,
        )

        # 4) Call Qwen3 via existing OllamaService.
        executive_summary, signals_dict, recommendations = await self._synthesize(prompt, track)

        # Map list of dictionaries to Pydantic models robustly
        signals = [
            IntelligenceSignal(
                title=s.get("title", "Key Insight"),
                category=s.get("category", track),
                confidence=s.get("confidence", "medium"),
                description=s.get("description", ""),
                source_urls=s.get("source_urls", []),
            )
            for s in signals_dict
        ]

        # 5) Store findings to semantic memory (best-effort)
        saved_to_memory = False
        if executive_summary and executive_summary != _NO_SOURCES_SUMMARY:
            try:
                # Store synthesis summary & signals into memory
                mem_text = f"Research Query: {query}\nExecutive Summary: {executive_summary}"
                if signals:
                    mem_text += "\nKey Insights:\n" + "\n".join(f"- {s.title}: {s.description}" for s in signals)
                
                await self._memory.remember(
                    text=mem_text,
                    payload_extra={
                        "type": "research",
                        "query": query,
                        "executive_summary": executive_summary,
                        "track": track,
                    }
                )
                saved_to_memory = True
            except Exception:  # noqa: BLE001
                logger.exception("Failed to save research results to semantic memory")

        # Update metadata saved_to_memory
        metadata.saved_to_memory = saved_to_memory

        return IntelligenceResponse(
            query=query,
            used_brightdata=bd_result.used_brightdata,
            sources=sources,
            executive_summary=executive_summary,
            summary=executive_summary,  # Deprecated compatibility field
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
        use_brightdata: Optional[bool] = None,
    ) -> tuple[BrightDataSearchResponse, str, Optional[str]]:
        """Select provider, fetch results, and fallback if needed.

        Returns (response, provider_used, fallback_provider_or_None).
        """
        # If user explicitly turned off Bright Data, return empty results
        if use_brightdata is False:
            return BrightDataSearchResponse(query=query, results=[]), "none", None

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
        query: str,
        sources: list[IntelligenceSourceItem],
        track: str,
        company: Optional[str],
        competitors: Optional[str],
    ) -> str:
        """Build a user prompt listing the query and source snippets."""
        lines = [f"Research query: {query}"]
        if company:
            lines.append(f"Target Company: {company}")
        if competitors:
            lines.append(f"Competitors: {competitors}")
        lines.append(f"Research Track: {track}")
        lines.append("")
        lines.append("Sources:")
        for i, s in enumerate(sources, start=1):
            lines.append(f"[{i}] {s.title}")
            lines.append(f"    URL: {s.url}")
            lines.append(f"    Snippet: {s.snippet}")
            lines.append("")
        lines.append(
            "Analyze these sources and return JSON with keys: executive_summary, signals, recommendations."
        )
        return "\n".join(lines)

    async def _synthesize(
        self, prompt: str, track: str
    ) -> tuple[str, list[dict[str, Any]], list[str]]:
        """Call Ollama and parse the structured response."""
        try:
            result = await self._ollama.generate(
                prompt=prompt,
                system=_SYNTHESIS_SYSTEM,
            )
            return self._parse_synthesis(result["answer"], track)
        except OllamaError as exc:
            logger.warning("AI synthesis failed (Ollama): %s", exc)
            return self._fallback_synthesis(track)
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
        track: str = "General",
    ) -> tuple[str, list[dict[str, Any]], list[str]]:
        """Try to parse JSON from the AI response; fallback to raw text."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()

        try:
            data: dict[str, Any] = json.loads(cleaned)
            executive_summary = str(data.get("executive_summary") or "").strip()
            # If the response used "summary" instead of "executive_summary", support it as fallback
            if not executive_summary:
                executive_summary = str(data.get("summary") or "").strip()
            
            raw_signals = data.get("signals") or []
            signals: list[dict[str, Any]] = []
            for rs in raw_signals:
                if isinstance(rs, dict):
                    # Ensure confidence is high/medium/low
                    confidence = str(rs.get("confidence") or "medium").lower()
                    if confidence not in ("high", "medium", "low"):
                        confidence = "medium"
                    
                    signals.append({
                        "title": str(rs.get("title") or "Key Trend").strip(),
                        "category": str(rs.get("category") or track).strip(),
                        "confidence": confidence,
                        "description": str(rs.get("description") or "").strip(),
                        "source_urls": [str(url) for url in (rs.get("source_urls") or []) if url]
                    })
                elif isinstance(rs, str):
                    # If LLM returned a list of strings instead of objects, construct a standard signal object!
                    signals.append({
                        "title": rs[:50],
                        "category": track,
                        "confidence": "medium",
                        "description": rs,
                        "source_urls": []
                    })
            
            recommendations = [
                str(r) for r in (data.get("recommendations") or []) if r
            ]
            return executive_summary or raw, signals, recommendations
        except (json.JSONDecodeError, TypeError, ValueError):
            return raw, [], []

    @staticmethod
    def _fallback_synthesis(track: str = "General") -> tuple[str, list[dict[str, Any]], list[str]]:
        """Return a safe fallback when AI is unavailable."""
        return (
            "AI synthesis is currently unavailable. Sources were retrieved successfully.",
            [],
            ["Review the sources manually for insights."],
        )

