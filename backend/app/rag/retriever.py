from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.embedder import Embedder

logger = logging.getLogger(__name__)

_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


SIMILARITY_THRESHOLD = 0.30

_SQL = text(
    "SELECT dc.content, dc.document_id, d.title, d.source_url, d.source_type, "
    "1 - (dc.embedding <=> :emb ::vector) AS similarity "
    "FROM document_chunks dc "
    "JOIN documents d ON dc.document_id = d.id "
    "ORDER BY similarity DESC "
    "LIMIT :top_k"
)


async def retrieve_relevant_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 6,
) -> list[dict]:
    """Embed *query* and return the closest document chunks from pgvector."""
    embedder = _get_embedder()
    query_embedding = embedder.embed_single(query)

    emb_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    result = await db.execute(_SQL, {"emb": emb_str, "top_k": top_k})
    rows = result.mappings().all()

    logger.info("RAW retrieval returned %d rows", len(rows))

    chunks: list[dict] = []
    for row in rows:
        sim = float(row["similarity"])
        logger.info("  -> %.4f  %s", sim, row["title"])
        if sim < SIMILARITY_THRESHOLD:
            continue
        chunks.append(
            {
                "content": row["content"],
                "title": row["title"],
                "source_url": row["source_url"],
                "source_type": row["source_type"],
                "similarity": round(sim, 4),
            }
        )

    top_score = chunks[0]["similarity"] if chunks else 0
    logger.info(
        "Retrieval: query_len=%d, chunks_returned=%d, top_similarity=%.4f",
        len(query), len(chunks), top_score,
    )
    return chunks
