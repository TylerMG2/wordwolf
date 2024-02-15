import pytest
from httpx import AsyncClient
from app.main import app

# Function to create a test room
@pytest.fixture
async def test_room(user_id: str = "test_host_id", username: str = "test user"):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/rooms/", json={"username": username, "host": user_id})
    return response.json()