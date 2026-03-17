import re


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split *text* into chunks that respect sentence boundaries.

    Parameters
    ----------
    chunk_size : int
        Maximum character length per chunk.
    overlap : int
        Approximate character overlap between consecutive chunks.
    """
    sentences = _SENTENCE_BOUNDARY.split(text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        added_len = len(sentence) + (1 if current else 0)

        if current and current_len + added_len > chunk_size:
            chunks.append(" ".join(current))

            # walk backwards to build the overlap seed
            overlap_parts: list[str] = []
            overlap_len = 0
            for prev in reversed(current):
                if overlap_len + len(prev) > overlap:
                    break
                overlap_parts.insert(0, prev)
                overlap_len += len(prev) + 1

            current = overlap_parts
            current_len = sum(len(s) for s in current) + max(len(current) - 1, 0)

        current.append(sentence)
        current_len += added_len

    if current:
        chunks.append(" ".join(current))

    return chunks
