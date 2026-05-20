"""Tests for app.utils.text_normalizer."""

from app.utils.text_normalizer import hash_question, normalize_question


def test_trims_whitespace():
    assert normalize_question("  hello  ") == "hello"


def test_collapses_multiple_spaces():
    assert normalize_question("hello   world") == "hello world"


def test_collapses_newlines():
    assert normalize_question("hello\n\nworld") == "hello world"


def test_lowercases():
    assert normalize_question("Hello World") == "hello world"


def test_empty_string():
    assert normalize_question("") == ""


def test_hash_stable_for_equivalent_text():
    h1 = hash_question("  Hello   World  ")
    h2 = hash_question("hello world")
    assert h1 == h2


def test_hash_differs_for_different_text():
    h1 = hash_question("hello world")
    h2 = hash_question("goodbye world")
    assert h1 != h2


def test_hash_is_hex_string():
    h = hash_question("test")
    assert len(h) == 64  # SHA-256 hex
    assert all(c in "0123456789abcdef" for c in h)
