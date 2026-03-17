import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_send_message_returns_200(client, mock_chat_engine):
    res = await client.post(
        "/api/chat/message",
        json={"message": "Where is the career center?"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "response" in body
    assert "session_id" in body
    assert "sources" in body
    assert isinstance(body["sources"], list)


@pytest.mark.asyncio
async def test_empty_message_returns_422(client):
    res = await client.post(
        "/api/chat/message",
        json={"message": ""},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_missing_message_returns_422(client):
    res = await client.post(
        "/api/chat/message",
        json={},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_history_returns_list(client, mock_db):
    mock_db.execute = pytest.importorskip("unittest.mock").AsyncMock(
        return_value=type("R", (), {"scalar_one_or_none": lambda self: None})()
    )
    res = await client.get("/api/chat/history/00000000-0000-0000-0000-000000000001")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["service"] == "OWU Campus Assistant"
