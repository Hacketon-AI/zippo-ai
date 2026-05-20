"""Pure helpers for normalizing and hashing user questions.

Used by the cache layer to deduplicate semantically identical inputs.
No I/O, no side effects.
"""

from __future__ import annotations

import hashlib
import re

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_question(text: str) -> str:
    """Trim, collapse whitespace, and lowercase a question."""
    if not text:
        return ""
    collapsed = _WHITESPACE_RE.sub(" ", text).strip()
    return collapsed.lower()


def hash_question(text: str) -> str:
    """Return the SHA-256 hex digest of the normalized question."""
    normalized = normalize_question(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
