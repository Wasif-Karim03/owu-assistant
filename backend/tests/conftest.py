import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import get_db


@pytest.fixture
def mock_db():
    """Yields a mock AsyncSession and patches it into the FastAPI dep."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async def _override():
        yield session

    app.dependency_overrides[get_db] = _override
    yield session
    app.dependency_overrides.clear()


@pytest.fixture
def mock_chat_engine():
    """Patches ChatEngine.chat to return a canned response."""
    fake_result = {
        "session_id": str(uuid.uuid4()),
        "response": "The IOCP is in the Corns Building.",
        "sources": [{"title": "IOCP", "url": "https://owu.edu/iocp"}],
        "has_clarifying_question": False,
    }
    with patch("app.routers.chat._get_engine") as mock_get:
        engine = MagicMock()
        engine.chat = AsyncMock(return_value=fake_result)
        mock_get.return_value = engine
        yield engine, fake_result


@pytest.fixture
def client(mock_db):
    """AsyncClient bound to the FastAPI app with DB mocked out."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
