import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from json import dumps
from dotenv import load_dotenv
from app.schemas.room_schema import RoomJoinResponse
load_dotenv()

@pytest.fixture
def create_room():
    async def _create_room(nickname: str):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/rooms/", json={"nickname": nickname})
            return RoomJoinResponse.model_validate_json(response.json()) 
    return _create_room

@pytest.fixture
def join_room():
    async def _join_room(room_id: str, nickname: str):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/api/rooms/{room_id}", json={"nickname": nickname})
            return RoomJoinResponse.model_validate_json(response.json()) 
    return _join_room

@pytest_asyncio.fixture
async def test_client(scope="module"):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def websocket_connection(): 
    async def _connection(room_id, player_id, credentials):
        client = TestClient(app)
        
        # Construct the websocket URL
        websocket_url = "/ws?"

        # Add each query parameter
        if room_id != None:
            websocket_url += f"room_id={room_id}&"
        if player_id != None:
            websocket_url += f"player_id={player_id}&"
        if credentials != None:
            websocket_url += f"credentials={credentials}"
        print(websocket_url)
        ws = client.websocket_connect(websocket_url)
        yield ws
        await ws.close()

    return _connection