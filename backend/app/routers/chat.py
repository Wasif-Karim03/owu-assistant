from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Conversation, Message
from app.rag.chat_engine import ChatEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

_engine: ChatEngine | None = None

# ── simple in-memory rate limiter ────────────────────────────────────

_rate_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 20
_RATE_WINDOW = 3600  # 1 hour in seconds


def _check_rate_limit(session_id: str) -> None:
    now = time.time()
    window_start = now - _RATE_WINDOW
    timestamps = _rate_store[session_id]
    _rate_store[session_id] = [t for t in timestamps if t > window_start]
    if len(_rate_store[session_id]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before sending more messages.",
        )
    _rate_store[session_id].append(now)


def _is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def _get_engine() -> ChatEngine:
    global _engine
    if _engine is None:
        _engine = ChatEngine()
    return _engine


# ── schemas ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=2000)


class SourceOut(BaseModel):
    title: str
    url: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: list[SourceOut]
    has_clarifying_question: bool


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: str
    sources: list[SourceOut] | None = None


# ── endpoints ────────────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def send_message(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    if not body.message or not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if body.session_id and not _is_valid_uuid(body.session_id):
        session_id = str(uuid.uuid4())
    else:
        session_id = body.session_id or str(uuid.uuid4())

    _check_rate_limit(session_id)

    logger.info(
        "Chat request: session=%s, message_len=%d",
        session_id, len(body.message),
    )

    engine = _get_engine()
    result = await engine.chat(db, session_id, body.message)

    return ChatResponse(
        session_id=result["session_id"],
        response=result["response"],
        sources=[SourceOut(**s) for s in result["sources"]],
        has_clarifying_question=result["has_clarifying_question"],
    )


@router.get("/history/{session_id}", response_model=list[MessageOut])
async def get_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    convo_result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    convo = convo_result.scalar_one_or_none()
    if convo is None:
        return []

    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == convo.id)
        .order_by(Message.created_at.asc())
    )
    messages = msg_result.scalars().all()

    return [
        MessageOut(
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
            sources=[SourceOut(**s) for s in m.sources_json] if m.sources_json else None,
        )
        for m in messages
    ]


@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    convo_result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    convo = convo_result.scalar_one_or_none()
    if convo is None:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(convo)
    await db.commit()
    return {"status": "cleared", "session_id": session_id}
