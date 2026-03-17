#!/usr/bin/env python3
"""Seed the vector database by scraping OWU web pages.

Usage:
    python ingestion/seed.py                  # scrape all default OWU pages
    python ingestion/seed.py --url <url>      # scrape a single URL
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Ensure the backend package is importable when running from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.database import async_session, init_db  # noqa: E402
from app.ingestion.pipeline import ingest_website_urls  # noqa: E402


async def main(urls: list[str] | None = None) -> None:
    await init_db()

    async with async_session() as db:
        docs = await ingest_website_urls(db, urls)
        print(f"\nIngestion complete. {len(docs)} documents indexed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed OWU assistant vector DB")
    parser.add_argument("--url", type=str, help="Ingest a single URL instead of all defaults")
    args = parser.parse_args()

    target = [args.url] if args.url else None
    asyncio.run(main(target))
