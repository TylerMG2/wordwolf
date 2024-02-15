import pytest
from httpx import AsyncClient
from app.main import app
from http import HTTPStatus

# Constants
USER_ID = "test_user_id"

# Test room creation
@pytest.mark.asyncio
async def test_create_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"user_id": USER_ID})
    assert response.status_code == 200

    # Check for room code in response
    assert "code" in response.json()

# Test room creation with no user_id
@pytest.mark.asyncio
async def test_create_room_no_user_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
    # Check if there is an error about missing name
    assert any(error["loc"] == ["body", "user_id"] for error in response.json()["detail"])

# Test room creation with no json
@pytest.mark.asyncio
async def test_create_room_no_json():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
    # Check if there is an error about missing name
    assert any(error["loc"] == ["body"] for error in response.json()["detail"])