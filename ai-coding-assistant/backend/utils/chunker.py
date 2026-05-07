"""
Chunker Utility - Splits code into meaningful, overlapping chunks for RAG.
"""

import logging
from typing import Generator

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 1500   # characters
DEFAULT_OVERLAP = 200       # characters of overlap between chunks


def chunk_code(
    content: str,
    source: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict]:
    """
    Split code content into overlapping chunks with metadata.

    Strategy:
    - Prefer splitting on blank lines (preserves logical units like functions/classes)
    - Fall back to character-based splitting if needed

    Args:
        content: The raw code string.
        source: File path or identifier (stored as metadata).
        chunk_size: Target characters per chunk.
        overlap: Number of characters to overlap between adjacent chunks.

    Returns:
        List of dicts with 'content', 'source', and 'chunk_index'.
    """
    lines = content.splitlines(keepends=True)
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0

    for line in lines:
        line_len = len(line)

        # If adding this line exceeds chunk_size, flush current chunk
        if current_size + line_len > chunk_size and current_chunk:
            chunk_text = "".join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "source": source,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

            # Overlap: retain the last N characters worth of lines
            overlap_lines = _trim_to_char_limit(current_chunk, overlap)
            current_chunk = overlap_lines
            current_size = sum(len(l) for l in current_chunk)

        current_chunk.append(line)
        current_size += line_len

    # Flush the final chunk
    if current_chunk:
        chunk_text = "".join(current_chunk)
        if chunk_text.strip():
            chunks.append({
                "content": chunk_text,
                "source": source,
                "chunk_index": chunk_index,
            })

    logger.debug(f"Chunked '{source}' into {len(chunks)} chunks")
    return chunks


def _trim_to_char_limit(lines: list[str], max_chars: int) -> list[str]:
    """Return the trailing lines that fit within max_chars total."""
    result = []
    total = 0
    for line in reversed(lines):
        if total + len(line) > max_chars:
            break
        result.insert(0, line)
        total += len(line)
    return result


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """
    Simple character-based chunking for arbitrary text (not code-aware).
    Used for documentation or non-code files.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
