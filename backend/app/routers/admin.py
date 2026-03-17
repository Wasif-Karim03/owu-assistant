from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete as sa_delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document, DocumentChunk
from app.ingestion.pipeline import ingest_document, ingest_website_urls
from app.ingestion.web_scraper import scrape_url
from app.ingestion.email_parser import parse_owu_daily
from app.ingestion.manual_entries import MANUAL_KNOWLEDGE_BASE

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── schemas ──────────────────────────────────────────────────────────

class IngestURLRequest(BaseModel):
    url: str = Field(..., min_length=1)


class IngestEmailRequest(BaseModel):
    content: str = Field(..., min_length=1)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    document_sources: list[dict]


# ── endpoints ────────────────────────────────────────────────────────

@router.post("/ingest/url")
async def ingest_url(
    body: IngestURLRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        page = await scrape_url(body.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {exc}")

    doc, chunk_count = await ingest_document(
        db,
        source_type="website",
        title=page["title"],
        content=page["content"],
        source_url=page["url"],
    )
    return {
        "status": "ingested",
        "document_id": str(doc.id),
        "title": doc.title,
        "chunks": chunk_count,
    }


@router.post("/ingest/email")
async def ingest_email(
    body: IngestEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    parsed = parse_owu_daily(body.content, body.date)

    doc, chunk_count = await ingest_document(
        db,
        source_type=parsed["source_type"],
        title=parsed["title"],
        content=parsed["content"],
        source_url=f"email://owu-daily/{body.date}",
        metadata=parsed["metadata"],
    )
    return {
        "status": "ingested",
        "document_id": str(doc.id),
        "title": doc.title,
        "chunks": chunk_count,
    }


@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """One-shot endpoint: scrape OWU website pages + ingest manual entries."""
    results: list[dict] = []

    # 0. Delete all old manual documents so renamed/removed entries don't linger
    old_manual = await db.execute(
        select(Document.id).where(Document.source_type == "manual")
    )
    old_ids = [row[0] for row in old_manual.all()]
    if old_ids:
        await db.execute(
            sa_delete(DocumentChunk).where(DocumentChunk.document_id.in_(old_ids))
        )
        await db.execute(
            sa_delete(Document).where(Document.id.in_(old_ids))
        )
        await db.flush()

    # 1. Manual knowledge base
    for entry in MANUAL_KNOWLEDGE_BASE:
        doc, chunk_count = await ingest_document(
            db,
            source_type=entry["source_type"],
            title=entry["title"],
            content=entry["content"],
            source_url=f"manual://{entry['title']}",
            metadata=entry.get("metadata"),
        )
        results.append({"title": doc.title, "chunks": chunk_count})

    # 2. OWU website pages
    web_docs = await ingest_website_urls(db)
    for doc in web_docs:
        results.append({"title": doc.title, "chunks": 0})

    return {
        "status": "seeded",
        "documents_ingested": len(results),
        "details": results,
    }


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    doc_count = await db.scalar(select(func.count()).select_from(Document))
    chunk_count = await db.scalar(select(func.count()).select_from(DocumentChunk))

    source_rows = await db.execute(
        select(
            Document.source_type,
            func.count().label("count"),
        ).group_by(Document.source_type)
    )

    document_sources = [
        {"source_type": row.source_type, "count": row.count}
        for row in source_rows
    ]

    return StatsResponse(
        total_documents=doc_count or 0,
        total_chunks=chunk_count or 0,
        document_sources=document_sources,
    )
