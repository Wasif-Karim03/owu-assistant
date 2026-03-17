"""Optional background scheduler that re-scrapes OWU pages every 24 hours.

Only runs when ENVIRONMENT=production.  Started as a daemon thread from
FastAPI's lifespan so it doesn't block the event loop.
"""

import asyncio
import logging
import threading
import time

from app.config import settings

logger = logging.getLogger(__name__)

_INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours


def _run_refresh() -> None:
    """Blocking helper executed inside a background thread."""
    from app.database import async_session, init_db
    from app.ingestion.pipeline import ingest_website_urls

    async def _job() -> None:
        await init_db()
        async with async_session() as db:
            docs = await ingest_website_urls(db)
            logger.info("Scheduled refresh complete — %d documents updated.", len(docs))

    asyncio.run(_job())


def _loop() -> None:
    while True:
        time.sleep(_INTERVAL_SECONDS)
        try:
            logger.info("Starting scheduled content refresh …")
            _run_refresh()
        except Exception:
            logger.exception("Scheduled refresh failed")


def start_refresh_scheduler() -> None:
    """Call once at application startup (production only)."""
    if settings.ENVIRONMENT != "production":
        logger.info("Skipping content refresh scheduler (not production).")
        return

    thread = threading.Thread(target=_loop, daemon=True, name="content-refresh")
    thread.start()
    logger.info("Content refresh scheduler started (every 24 h).")
