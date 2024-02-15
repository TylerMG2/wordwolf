import pytest
from httpx import AsyncClient
from app.main import app
from http import HTTPStatus

# Constants
USERNAME = "test user"
USER_ID = "test_user_id"

# Test room creation
@pytest.mark.asyncio
async def test_create_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"username": USERNAME, "host": USER_ID})
    assert response.status_code == 200

    # Check for room code in response
    assert "code" in response.json()

    # Check for room name in response
    assert response.json()["name"] == "test room"

# Test room creation with no username
@pytest.mark.asyncio
async def test_create_room_no_username():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"host": USER_ID})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
    # Check if there is an error about missing username
    assert any(error["loc"] == ["body", "username"] for error in response.json()["detail"])

# Test room creation with no host
@pytest.mark.asyncio
async def test_create_room_no_host():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"username": USERNAME})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
    # Check if there is an error about missing host
    assert any(error["loc"] == ["body", "host"] for error in response.json()["detail"])

# Test room creation with no data
@pytest.mark.asyncio
async def test_create_room_no_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
    # Check if there is an error about missing host
    assert any(error["loc"] == ["body", "username"] for error in response.json()["detail"])
    
    # Check if there is an error about missing name
    assert any(error["loc"] == ["body", "host"] for error in response.json()["detail"])