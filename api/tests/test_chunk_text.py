"""Tests for app.utils.chunk_text."""

import pytest

from app.utils.chunk_text import chunk_text


def test_short_text_single_chunk():
    result = chunk_text("hello world", chunk_size=100, overlap=10)
    assert result == ["hello world"]


def test_chunks_long_text():
    text = "a" * 250
    result = chunk_text(text, chunk_size=100, overlap=0)
    assert len(result) == 3
    assert all(len(c) <= 100 for c in result)


def test_overlap_creates_more_chunks():
    text = "a" * 200
    no_overlap = chunk_text(text, chunk_size=100, overlap=0)
    with_overlap = chunk_text(text, chunk_size=100, overlap=50)
    assert len(with_overlap) > len(no_overlap)


def test_overlap_content():
    text = "abcdefghij" * 10  # 100 chars
    chunks = chunk_text(text, chunk_size=60, overlap=20)
    # Second chunk should start 40 chars in (step = 60 - 20)
    assert chunks[1][:20] == text[40:60]


def test_rejects_empty_text():
    with pytest.raises(ValueError, match="not be empty"):
        chunk_text("")


def test_rejects_whitespace_only():
    with pytest.raises(ValueError, match="not be empty"):
        chunk_text("   ")


def test_rejects_zero_chunk_size():
    with pytest.raises(ValueError, match="greater than 0"):
        chunk_text("hello", chunk_size=0)


def test_rejects_negative_overlap():
    with pytest.raises(ValueError, match=">= 0"):
        chunk_text("hello", overlap=-1)


def test_rejects_overlap_gte_chunk_size():
    with pytest.raises(ValueError, match="less than chunk_size"):
        chunk_text("hello", chunk_size=10, overlap=10)
