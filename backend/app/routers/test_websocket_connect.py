from httpx import AsyncClient
import pytest, pytest_asyncio
from typing import Optional
from fastapi.testclient import TestClient
from ..schemas import RoomSchema, ActionSchema
from .room import RoomResponse
from ..main import app

@pytest.mark.asyncio
class TestWebsocketConnect:

    room : RoomResponse = None
    NICKNAME : str = "test"
    client : AsyncClient = AsyncClient(app=app, base_url="http://test")

    # Create a room before each test
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        response = await self.client.post("/api/rooms", json={"nickname": self.NICKNAME})
        self.room = RoomResponse(**response.json())

    # Test connecting to a room as a player and host
    @pytest.mark.parametrize("is_host", [True, False])
    async def test_connect_to_room(self, is_host):
        
        # Create new player if not host
        if not is_host:
            response = await self.client.post(f"/api/rooms/{self.room.room_id}", json={"nickname": self.NICKNAME})
            self.room = RoomResponse(**response.json())
        
        # Connect to the room
        client = TestClient(app)
        with client.websocket_connect(f"/ws?room_id={self.room.room_id}&player_id={self.room.player_id}&credentials={self.room.credentials}") as ws:
            data = ws.receive_json()
            action = ActionSchema.model_validate_json(data)

            # Check the response
            assert action.action == "game_state"
            assert action.data.room_id == self.room.room_id
            assert self.room.player_id in action.data.players
            assert len(action.data.players) == 1
            assert action.data.players[self.room.player_id].nickname == self.NICKNAME
            assert action.data.you.nickname == self.NICKNAME
            assert action.data.you.is_host == is_host
            assert action.data.host_id == self.room.player_id if is_host else 0



        
