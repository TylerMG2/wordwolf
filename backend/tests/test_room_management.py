import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/rooms/", json={"name": "test room"})
    assert response.status_code == 200

    # Check for room code in response
    assert "code" in response.json()
    assert response.json()["name"] == "test room"