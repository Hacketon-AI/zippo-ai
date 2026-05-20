"""Pure helper for splitting text into overlapping chunks.

Used by the document ingestion pipeline. No I/O, no side effects.
"""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """Split `text` into a list of overlapping chunks.

    - chunk_size: maximum characters per chunk.
    - overlap: characters reused from the end of the previous chunk to
      preserve context across boundaries.

    Empty pieces (whitespace-only) are skipped. Returns at least one
    chunk for any non-empty input.
    """
    if text is None or not str(text).strip():
        raise ValueError("text must not be empty")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")

    cleaned = text.strip()
    step = chunk_size - overlap
    chunks: list[str] = []
    start = 0
    length = len(cleaned)

    while start < length:
        end = start + chunk_size
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start += step

    return chunks
