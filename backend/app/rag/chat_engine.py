from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime

from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Conversation, Message
from app.rag.retriever import retrieve_relevant_chunks
from app.rag.prompt_builder import build_system_prompt, build_user_message

logger = logging.getLogger(__name__)

_FALLBACK_MESSAGE = (
    "I'm having trouble connecting right now. Please try again in a moment."
)


class ChatEngine:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.CHAT_MODEL

    async def chat(
        self,
        db: AsyncSession,
        session_id: str,
        user_message: str,
    ) -> dict:
        try:
            conversation = await self._get_or_create_conversation(db, session_id)
        except Exception:
            logger.exception("DB error creating/loading conversation %s", session_id)
            return self._error_response(session_id)

        try:
            history = await self._load_history(db, conversation.id, limit=6)
        except Exception:
            logger.exception("DB error loading history for %s", session_id)
            history = []

        try:
            chunks = await retrieve_relevant_chunks(
                db, user_message, top_k=settings.TOP_K_RESULTS
            )
            top_score = chunks[0]["similarity"] if chunks else 0
            logger.info(
                "Retrieval: %d chunks found, top_similarity=%.4f, session=%s",
                len(chunks), top_score, session_id,
            )
        except Exception:
            logger.exception("Retrieval error for session %s", session_id)
            chunks = []

        sources = [
            {"title": c["title"], "url": c["source_url"]}
            for c in chunks
            if c.get("source_url")
        ]
        seen_urls: set[str] = set()
        unique_sources: list[dict] = []
        for s in sources:
            if s["url"] not in seen_urls:
                seen_urls.add(s["url"])
                unique_sources.append(s)

        context_user_msg = build_user_message(user_message, chunks)

        messages: list[dict] = [
            {"role": "system", "content": build_system_prompt()},
        ]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": context_user_msg})

        try:
            t0 = time.perf_counter()
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=1024,
                messages=messages,
                timeout=30.0,
            )
            elapsed = time.perf_counter() - t0
            logger.info("LLM responded in %.2fs, session=%s", elapsed, session_id)
            assistant_text = response.choices[0].message.content
        except Exception as exc:
            logger.exception("LLM error, session=%s", session_id)
            return self._error_response(session_id)

        try:
            await self._save_message(db, conversation.id, "user", user_message)
            await self._save_message(
                db,
                conversation.id,
                "assistant",
                assistant_text,
                sources_json=unique_sources or None,
            )
            await db.commit()
        except Exception:
            logger.exception("DB error saving messages for session %s", session_id)

        return {
            "response": assistant_text,
            "sources": unique_sources,
            "session_id": session_id,
            "has_clarifying_question": self.has_clarifying_question(assistant_text),
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _error_response(session_id: str) -> dict:
        return {
            "response": _FALLBACK_MESSAGE,
            "sources": [],
            "session_id": session_id,
            "has_clarifying_question": False,
        }

    @staticmethod
    def has_clarifying_question(text: str) -> bool:
        return text.rstrip().endswith("?")

    @staticmethod
    async def _get_or_create_conversation(
        db: AsyncSession, session_id: str
    ) -> Conversation:
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        convo = result.scalar_one_or_none()
        if convo is None:
            convo = Conversation(id=uuid.uuid4(), session_id=session_id)
            db.add(convo)
            await db.flush()
        return convo

    @staticmethod
    async def _load_history(
        db: AsyncSession, conversation_id, limit: int = 6
    ) -> list[Message]:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        msgs = list(result.scalars().all())
        msgs.reverse()
        return msgs

    @staticmethod
    async def _save_message(
        db: AsyncSession,
        conversation_id,
        role: str,
        content: str,
        sources_json=None,
    ) -> Message:
        msg = Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources_json=sources_json,
        )
        db.add(msg)
        return msg
