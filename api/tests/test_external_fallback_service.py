"""Tests for ExternalFallbackService skeleton."""

import pytest

from app.services.external_fallback_service import (
    ExternalFallbackDisabledError,
    ExternalFallbackService,
)


@pytest.fixture
def disabled_service():
    """Service with fallback disabled (default)."""
    return ExternalFallbackService()


def test_disabled_by_default(disabled_service):
    assert disabled_service.enabled is False


@pytest.mark.asyncio
async def test_generate_raises_when_disabled(disabled_service):
    with pytest.raises(ExternalFallbackDisabledError):
        await disabled_service.generate("hello")


@pytest.mark.asyncio
async def test_no_external_call_made(disabled_service):
    """Ensure no network call happens — exception is raised immediately."""
    with pytest.raises(ExternalFallbackDisabledError):
        await disabled_service.generate("test", context="some context")
