"""Shared slowapi limiter for rate-limited endpoints.

When `rate_limit_enabled` is false, the limiter is created but not
attached to the app, so decorators become no-ops.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings


def _build_limiter() -> Limiter:
    settings = get_settings()
    return Limiter(
        key_func=get_remote_address,
        enabled=settings.rate_limit_enabled,
        default_limits=[],
    )


limiter: Limiter = _build_limiter()
