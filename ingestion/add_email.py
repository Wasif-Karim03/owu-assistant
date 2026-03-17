#!/usr/bin/env python3
"""Ingest an OWU Daily email into the vector database.

Usage:
    python ingestion/add_email.py --file emails/daily_2025-03-15.txt --date 2025-03-15
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.database import async_session, init_db  # noqa: E402
from app.ingestion.email_parser import parse_owu_daily  # noqa: E402
from app.ingestion.pipeline import ingest_document  # noqa: E402


async def main(file_path: str, date: str) -> None:
    await init_db()

    raw = Path(file_path).read_text(encoding="utf-8")
    parsed = parse_owu_daily(raw, date)

    async with async_session() as db:
        doc, chunk_count = await ingest_document(
            db,
            source_type=parsed["source_type"],
            title=parsed["title"],
            content=parsed["content"],
            source_url=f"email://owu-daily/{date}",
            metadata=parsed["metadata"],
        )
        print(f"Ingested email: {doc.title}  ({chunk_count} chunks, id={doc.id})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest an OWU Daily email")
    parser.add_argument("--file", required=True, help="Path to email text file")
    parser.add_argument("--date", required=True, help="Email date (YYYY-MM-DD)")
    args = parser.parse_args()

    asyncio.run(main(args.file, args.date))
