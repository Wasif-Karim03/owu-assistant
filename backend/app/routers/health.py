from __future__ import annotations

import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check():
    db_ok = False
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        logger.exception("Health check: DB unreachable")

    claude_ok = False
    try:
        import anthropic
        client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY, timeout=5.0
        )
        client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        claude_ok = True
    except Exception:
        logger.warning("Health check: Claude API unreachable")

    status = "healthy" if (db_ok and claude_ok) else "degraded"
    return {
        "status": status,
        "database": "connected" if db_ok else "unreachable",
        "claude_api": "reachable" if claude_ok else "unreachable",
    }
