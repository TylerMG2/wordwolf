from httpx import AsyncClient
import pytest, pytest_asyncio
from fastapi import WebSocketDisconnect
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
            assert len(action.data.players) == (1 if is_host else 2)
            assert action.data.players[self.room.player_id].nickname == self.NICKNAME
            assert action.data.you.nickname == self.NICKNAME
            assert action.data.you.is_host == is_host
            assert action.data.host_id == (self.room.player_id if is_host else 0)

    # Test connecting with invalid room_id, player_id, and credentials
    @pytest.mark.parametrize("room_id, player_id, credentials, code, reason", [
        ("invalid_room_id", None, None, 4001, "Room not found"),
        (None, "invalid_player_id", None, 4001, "Invalid player_id"),
        (None, 999, None, 4001, "Player not found"),
        (None, None, "invalid_credentials", 4001, "Incorrect credentials")
    ])
    async def test_connect_with_invalid_values(self, room_id, player_id, credentials, code, reason):
        client = TestClient(app)
        url = f"/ws?room_id={room_id or self.room.room_id}&player_id={player_id or self.room.player_id}&credentials={credentials or self.room.credentials}"
        with pytest.raises(WebSocketDisconnect) as e:
            with client.websocket_connect(url) as ws:
                pass
        assert e.value.code == code
        assert e.value.reason == reason

    # Test connecting with missing parameters
    @pytest.mark.parametrize("url", [
        "/ws?room_id=invalid_room_id&player_id=1",
        "/ws?room_id=invalid_room_id&credentials=credentials",
        "/ws?player_id=1&credentials=credentials"
    ])
    async def test_connect_with_missing_parameters(self, url):
        client = TestClient(app)
        with pytest.raises(WebSocketDisconnect) as e:
            with client.websocket_connect(url) as ws:
                pass
        assert e.value.code == 1008

    # Test connecting after another player has joined
    async def test_connect_after_join(self):
        player_2_resp = await self.client.post(f"/api/rooms/{self.room.room_id}", json={"nickname": "test2"})
        player_2 = RoomResponse(**player_2_resp.json())

        # Player 1 connects
        client = TestClient(app)
        with client.websocket_connect(f"/ws?room_id={self.room.room_id}&player_id={self.room.player_id}&credentials={self.room.credentials}") as ws:
            ws.receive_json()
            
            # Player 2 connects
            with client.websocket_connect(f"/ws?room_id={player_2.room_id}&player_id={player_2.player_id}&credentials={player_2.credentials}") as ws2:
                data = ws2.receive_json()
                action = ActionSchema.model_validate_json(data)

                # Check the response
                assert action.action == "game_state"
                assert action.data.room_id == self.room.room_id
                assert player_2.player_id in action.data.players
                assert len(action.data.players) == 2
                assert action.data.players[self.room.player_id].is_connected == True

            # Get player join action
            data = ws.receive_json()
            action = ActionSchema.model_validate_json(data)

            # Check the response
            assert action.action == "player_join"
            assert action.data.player_id == player_2.player_id
            assert action.data.nickname == "test2"
            assert action.data.is_host == False
            
        
