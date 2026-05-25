"""Bright Data web search service.

Calls the configured Bright Data SERP API (Direct API) to retrieve web
search results. Returns a normalized list of {title, url, snippet}.

If the response is structured JSON, it is parsed directly. If the
response is raw HTML (Google SERP page), a fallback BeautifulSoup
parser extracts organic results.

If the feature is disabled or misconfigured, returns a safe fallback
response without raising exceptions.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup, Tag

from app.core.config import Settings, get_settings
from app.schemas.intelligence import (
    BrightDataSearchResponse,
    BrightDataSearchResult,
)

logger = logging.getLogger(__name__)

# Google internal domains/paths to skip when extracting organic results.
_SKIP_DOMAINS = {
    "accounts.google.com",
    "support.google.com",
    "webcache.googleusercontent.com",
}
_SKIP_PATHS = {"/search", "/preferences", "/advanced_search", "/imgres"}

# Low-quality titles to filter out (case-insensitive exact match).
_LOW_QUALITY_TITLES = {
    "read more",
    "learn more",
    "more",
    "more results",
    "view all",
    "cached",
    "similar",
}

# URL fragment pattern indicating a text highlight — should be stripped.
_TEXT_FRAGMENT_RE = re.compile(r"#:~:text=.*$")

# Collapse whitespace.
_WHITESPACE_RE = re.compile(r"\s+")

# Max snippet length.
_MAX_SNIPPET_LEN = 300


class BrightDataService:
    """Async Bright Data SERP search client (Direct API / zone-based)."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._enabled = self._settings.brightdata_enabled
        self._api_key = self._settings.brightdata_api_key
        self._provider = self._settings.brightdata_provider
        self._serp_endpoint = self._settings.brightdata_serp_endpoint
        self._serp_zone = self._settings.brightdata_serp_zone
        self._timeout = self._settings.brightdata_timeout_seconds
        self._max_results = self._settings.brightdata_max_results
        self._country = self._settings.brightdata_country
        self._language = self._settings.brightdata_language

    async def search_web(
        self,
        query: str,
        country: Optional[str] = None,
        language: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> BrightDataSearchResponse:
        """Search the web via Bright Data SERP Direct API.

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
                error="Bright Data is disabled",
            )

        if not self._api_key:
            return BrightDataSearchResponse(
                query=query,
                error="Bright Data API key is not configured",
            )

        if not self._serp_endpoint:
            return BrightDataSearchResponse(
                query=query,
                error="Bright Data SERP endpoint is not configured",
            )

        if self._provider == "serp_api" and not self._serp_zone:
            return BrightDataSearchResponse(
                query=query,
                error="Bright Data SERP zone is not configured",
            )

        effective_country = country or self._country
        effective_language = language or self._language
        effective_limit = max_results if max_results is not None else self._max_results

        # Build Google search URL with safe encoding.
        search_params = urlencode({
            "q": query.strip(),
            "hl": effective_language,
            "gl": effective_country,
            "num": effective_limit,
        })
        search_url = f"https://www.google.com/search?{search_params}"

        # Bright Data Direct API request body.
        payload: dict[str, Any] = {
            "zone": self._serp_zone,
            "url": search_url,
            "format": "json",
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._serp_endpoint,
                    json=payload,
                    headers=headers,
                )

            if response.status_code >= 400:
                error_text = response.text[:200]
                logger.warning(
                    "Bright Data returned %d: %s", response.status_code, error_text
                )
                return BrightDataSearchResponse(
                    query=query,
                    error=f"Bright Data HTTP {response.status_code}: {error_text}",
                )

            # Determine if response is JSON or HTML.
            content_type = response.headers.get("content-type", "")
            raw_text = response.text.strip()

            if "text/html" in content_type or raw_text.startswith(("<!", "<html", "<HTML")):
                results = self._extract_html_results(raw_text, effective_limit)
            else:
                data = response.json()
                # Handle wrapped HTML in a JSON body field.
                if isinstance(data, dict) and isinstance(data.get("body"), str):
                    body = data["body"].strip()
                    if body.startswith(("<!", "<html", "<HTML")):
                        results = self._extract_html_results(body, effective_limit)
                    else:
                        results = self._normalize_results(data, effective_limit)
                else:
                    results = self._normalize_results(data, effective_limit)

            return BrightDataSearchResponse(
                used_brightdata=True,
                results=results,
                query=query,
                result_count=len(results),
            )

        except httpx.TimeoutException:
            logger.warning("Bright Data request timed out for query: %s", query)
            return BrightDataSearchResponse(
                query=query,
                error="Bright Data request timed out",
            )
        except httpx.HTTPStatusError as exc:
            logger.warning("Bright Data HTTP error: %s", exc)
            return BrightDataSearchResponse(
                query=query,
                error=f"Bright Data HTTP error: {exc}",
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error calling Bright Data")
            return BrightDataSearchResponse(
                query=query,
                error=f"Unexpected error: {type(exc).__name__}: {exc}",
            )

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_snippet(text: str) -> str:
        """Collapse whitespace and truncate snippet to max length."""
        cleaned = _WHITESPACE_RE.sub(" ", text).strip()
        if len(cleaned) > _MAX_SNIPPET_LEN:
            cleaned = cleaned[:_MAX_SNIPPET_LEN].rsplit(" ", 1)[0] + "…"
        return cleaned

    @staticmethod
    def _strip_text_fragment(url: str) -> str:
        """Remove #:~:text= fragments from a URL."""
        return _TEXT_FRAGMENT_RE.sub("", url)

    @staticmethod
    def _canonical_url(url: str) -> str:
        """Return a canonical form for deduplication (no fragment, no trailing slash)."""
        parsed = urlparse(url)
        clean = urlunparse(parsed._replace(fragment=""))
        return clean.rstrip("/")

    # ------------------------------------------------------------------
    # JSON normalizer
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_results(
        data: Any, limit: int
    ) -> list[BrightDataSearchResult]:
        """Extract and normalize organic results from structured JSON."""
        raw_results: list[dict[str, Any]] = []

        if isinstance(data, dict):
            raw_results = (
                data.get("organic")
                or data.get("organic_results")
                or data.get("results")
                or []
            )
        elif isinstance(data, list):
            raw_results = data

        normalized: list[BrightDataSearchResult] = []
        for item in raw_results[:limit]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            url = str(item.get("link") or item.get("url") or "").strip()
            snippet = str(
                item.get("description") or item.get("snippet") or ""
            ).strip()
            if not url:
                continue
            normalized.append(
                BrightDataSearchResult(
                    title=title or "(no title)",
                    url=url,
                    snippet=snippet,
                    source="brightdata",
                )
            )

        return normalized

    # ------------------------------------------------------------------
    # HTML fallback parser
    # ------------------------------------------------------------------

    @classmethod
    def _extract_html_results(
        cls, html: str, max_results: int
    ) -> list[BrightDataSearchResult]:
        """Parse Google SERP HTML and extract organic results."""
        soup = BeautifulSoup(html, "html.parser")
        results: list[BrightDataSearchResult] = []
        seen_urls: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            if len(results) >= max_results:
                break

            href = anchor["href"]
            url = cls._normalize_google_url(href)
            if url is None:
                continue

            # Strip text fragments from URL.
            url = cls._strip_text_fragment(url)

            # Deduplicate by canonical URL.
            canonical = cls._canonical_url(url)
            if canonical in seen_urls:
                continue

            # Title: text of the anchor or its first heading child.
            heading = anchor.find(["h3", "h2", "h1"])
            if heading:
                title = heading.get_text(separator=" ", strip=True)
            else:
                title = anchor.get_text(separator=" ", strip=True)

            # Clean title by removing breadcrumbs or appended URLs
            if " › " in title:
                title = title.split(" › ")[0].strip()
            elif " ... " in title:
                title = title.split(" ... ")[0].strip()
            elif " » " in title:
                title = title.split(" » ")[0].strip()
            elif " - " in title:
                title = title.split(" - ")[0].strip()
            elif " | " in title:
                title = title.split(" | ")[0].strip()

            if not title:
                continue

            # Filter low-quality titles.
            if title.lower() in _LOW_QUALITY_TITLES:
                continue

            # Snippet: look for a sibling or parent container with descriptive text.
            snippet = cls._clean_snippet(cls._find_snippet(anchor))

            seen_urls.add(canonical)
            results.append(
                BrightDataSearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source="brightdata",
                )
            )

        return results

    @staticmethod
    def _normalize_google_url(href: str) -> Optional[str]:
        """Resolve a Google redirect URL or filter internal links.

        Returns the clean external URL or None if the link should be skipped.
        """
        if not href:
            return None

        parsed = urlparse(href)

        # Google redirect: /url?q=https://example.com&sa=...
        if parsed.path == "/url":
            qs = parse_qs(parsed.query)
            targets = qs.get("q") or qs.get("url")
            if targets:
                target = targets[0]
                target_parsed = urlparse(target)
                if target_parsed.scheme in ("http", "https"):
                    return target
            return None

        # Skip internal Google paths.
        if parsed.path in _SKIP_PATHS:
            return None

        # Skip internal Google domains.
        domain = parsed.hostname or ""
        if domain in _SKIP_DOMAINS or "google" in domain:
            return None

        # Only accept absolute http(s) URLs.
        if parsed.scheme in ("http", "https") and parsed.hostname:
            return href

        return None

    @staticmethod
    def _find_snippet(anchor: Tag) -> str:
        """Attempt to find a snippet near the anchor element, skipping breadcrumbs and internal links."""
        parent = anchor.parent
        anchor_text = anchor.get_text(separator=" ", strip=True)
        for _ in range(6):
            if parent is None:
                break
            if isinstance(parent, Tag) and parent.name == "div":
                for el in parent.find_all(["span", "div"], recursive=True):
                    # Skip elements that are inside the anchor itself to avoid breadcrumbs
                    if el.find_parent("a") == anchor or el == anchor:
                        continue
                    
                    # Skip if element contains nested divs/spans to get the leaf text container
                    if el.find(["div", "span"]):
                        continue
                        
                    text = el.get_text(separator=" ", strip=True)
                    # Skip low quality breadcrumb-like texts or URLs
                    if "›" in text or "»" in text or "http" in text:
                        continue
                        
                    if len(text) > 40 and text != anchor_text:
                        return text
            parent = parent.parent
            
        # Fallback: less restrictive search
        parent = anchor.parent
        for _ in range(4):
            if parent is None:
                break
            if isinstance(parent, Tag) and parent.name == "div":
                for el in parent.find_all(["span", "div"], recursive=True):
                    if el.find_parent("a") == anchor or el == anchor:
                        continue
                    text = el.get_text(separator=" ", strip=True)
                    if len(text) > 30 and text != anchor_text and "›" not in text:
                        return text
            parent = parent.parent
        return ""
