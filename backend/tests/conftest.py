import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture
def create_room():
    async def _create_room(user_id: str = "test_host_id"):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/rooms/", json={"user_id": user_id})
            return response.json()["code"]
    return _create_room

@pytest_asyncio.fixture
async def test_client(scope="session"):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def websocket_connection(): 
    def _connection(room_code, user_id, username=None):
        client = TestClient(app)
        
        # Construct the websocket URL
        websocket_url = "/ws?"

        # Add each query parameter
        if room_code:
            websocket_url += f"room={room_code}&"
        if user_id:
            websocket_url += f"user_id={user_id}&"
        if username:
            websocket_url += f"username={username}"
        
        return client.websocket_connect(websocket_url)
    return _connection

@pytest_asyncio.fixture
async def fetch_room_details():
    async def _fetch(room_code: str, user_id: str):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/api/rooms/{room_code}?user_id={user_id}")
            return response.json()
    return _fetch