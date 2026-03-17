from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Document, DocumentChunk
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import Embedder
from app.ingestion.web_scraper import scrape_owu_pages, OWU_SEED_URLS

_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def _prepare_chunks(content: str) -> list[tuple[str, list[float]]]:
    """Chunk text and compute embeddings synchronously (CPU/IO bound)."""
    chunks = chunk_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    if not chunks:
        return []
    embedder = _get_embedder()
    embeddings = embedder.embed_batch(chunks)
    return list(zip(chunks, embeddings))


async def ingest_document(
    db: AsyncSession,
    source_type: str,
    title: str,
    content: str,
    source_url: str | None = None,
    metadata: dict | None = None,
) -> tuple[Document, int]:
    """Chunk, embed, and persist a single document.

    If a document with the same *source_url* already exists its old chunks are
    replaced so re-ingestion is idempotent.
    """
    loop = asyncio.get_event_loop()
    prepared = await loop.run_in_executor(None, _prepare_chunks, content)

    existing: Document | None = None
    if source_url:
        result = await db.execute(
            select(Document).where(Document.source_url == source_url)
        )
        existing = result.scalar_one_or_none()

    if existing:
        await db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == existing.id)
        )
        existing.title = title
        existing.content = content
        existing.source_type = source_type
        existing.metadata_json = metadata
        existing.updated_at = datetime.utcnow()
        doc = existing
    else:
        doc = Document(
            id=uuid.uuid4(),
            source_type=source_type,
            source_url=source_url,
            title=title,
            content=content,
            metadata_json=metadata,
        )
        db.add(doc)

    await db.flush()

    for idx, (chunk_str, embedding) in enumerate(prepared):
        chunk = DocumentChunk(
            id=uuid.uuid4(),
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_str,
            embedding=embedding,
            token_count=len(chunk_str.split()),
        )
        db.add(chunk)

    await db.commit()
    return doc, len(prepared)


async def ingest_website_urls(
    db: AsyncSession,
    urls: list[str] | None = None,
) -> list[Document]:
    """Scrape and ingest a list of web pages (defaults to OWU_SEED_URLS)."""
    targets = urls or OWU_SEED_URLS
    print(f"Scraping {len(targets)} URLs …")
    pages = await scrape_owu_pages(targets)

    docs: list[Document] = []
    for page in pages:
        print(f"  Ingesting: {page['title']}")
        doc, _count = await ingest_document(
            db,
            source_type="website",
            title=page["title"],
            content=page["content"],
            source_url=page["url"],
        )
        docs.append(doc)

    print(f"Ingestion complete. {len(docs)} documents indexed.")
    return docs
