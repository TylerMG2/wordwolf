import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app

# Function to create a test room
@pytest.fixture
async def test_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"name": "test room"})
    return response.json()

# Test room creation
@pytest.mark.asyncio
async def test_create_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"name": "test room"})
    assert response.status_code == 200

    # Check for room code in response
    assert "code" in response.json()
    assert response.json()["name"] == "test room"

# Test room creation with no name
@pytest.mark.asyncio
async def test_create_room_no_name():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={})
    assert response.status_code == 422
    
    # Check if there is an error about missing name
    assert any(error["loc"] == ["body", "name"] for error in response.json()["detail"])

# Test websocket connection
@pytest.mark.asyncio
async def test_websocket_connect():
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"action": "ping"})
        data = ws.receive_text()
        assert data == "pong"

# Test room joining via websocket
@pytest.mark.asyncio
async def test_join_room(test_room):
    room_code = (await test_room)["code"]

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"action": "join", "room_code": room_code, "username": "test user"})
        data = ws.receive_json()

        # Assert that the response is correct
        assert data == {"message": "Joined room"}

# Test attempting to join a non-existent room
@pytest.mark.asyncio
async def test_join_non_existent_room():
    
    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"action": "join", "room_code": "1234", "username": "test user"})
        data = ws.receive_json()

        # Assert that the response is correct
        assert data == {"message": "Room does not exist"}