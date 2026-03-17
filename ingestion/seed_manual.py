#!/usr/bin/env python3
"""Seed the vector database with hardcoded OWU office/resource entries.

Usage:
    python ingestion/seed_manual.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.database import async_session, init_db  # noqa: E402
from app.ingestion.manual_entries import MANUAL_KNOWLEDGE_BASE  # noqa: E402
from app.ingestion.pipeline import ingest_document  # noqa: E402


async def main() -> None:
    await init_db()

    async with async_session() as db:
        count = 0
        for entry in MANUAL_KNOWLEDGE_BASE:
            print(f"  Ingesting: {entry['title']}")
            await ingest_document(
                db,
                source_type=entry["source_type"],
                title=entry["title"],
                content=entry["content"],
                source_url=f"manual://{entry['title'].lower().replace(' ', '-')}",
                metadata=entry.get("metadata"),
            )  # returns (doc, chunk_count) tuple
            count += 1

        print(f"\nManual ingestion complete. {count} entries indexed.")


if __name__ == "__main__":
    asyncio.run(main())
