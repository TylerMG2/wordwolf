import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
def create_room():
    async def _create_room(user_id: str = "test_host_id"):
        async with AsyncClient(app=app, base_url="http://testserver") as ac:
            response = await ac.post("/api/rooms/", json={"user_id": user_id})
            return response.json()["code"]
    return _create_room
