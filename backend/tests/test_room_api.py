import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app

# Test room creation
@pytest.mark.asyncio
async def test_create_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"name": "test room"})
    assert response.status_code == 200

    # Check for room code in response
    assert "code" in response.json()

    # Check for room name in response
    assert response.json()["name"] == "test room"

# Test room creation with no name
@pytest.mark.asyncio
async def test_create_room_no_name():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={})
    assert response.status_code == 422
    
    # Check if there is an error about missing name
    assert any(error["loc"] == ["body", "name"] for error in response.json()["detail"])