"""Shared pytest fixtures.

Sets test-friendly env vars before the app is imported so that
slowapi, the DB engine, and other settings pick up safe defaults.
"""

from __future__ import annotations

import os

# Apply env BEFORE importing app. pytest collects this file first because
# it lives next to the test modules.
os.environ.setdefault("RATE_LIMIT_ENABLED", "true")
os.environ.setdefault("CHAT_RATE_LIMIT", "5/minute")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test"
)
