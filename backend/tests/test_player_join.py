import pytest
import pytest_asyncio
from starlette.websockets import WebSocketDisconnect
from app.schemas.player_schema import OtherPlayerSchema, PlayerSchema
from app.schemas.room_schema import RoomSchema, RoomJoinResponse
from app.schemas.action_schemas import ActionSchema
from starlette.websockets import WebSocket
from json import dumps

@pytest.mark.asyncio
class TestPlayerJoin:

    USERNAME = "Test User"
    room : RoomJoinResponse = None

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, create_room):
        self.room = await create_room(user_id=self.USERNAME)

    # Test joining the room
    @pytest.mark.parametrize("user_role, expected_host_status", [
        ("host", True),
        ("other_user", False),
    ])
    async def test_user_join(self, room, websocket_connection, join_room, user_role, expected_host_status):

        # If the user is not the host, join the room
        player_id, credentials = self.room.player_id, self.room.credentials
        if user_role != "host":
            new_player : RoomJoinResponse = await join_room(self.room.room_id, user_role)
            player_id, credentials = new_player.player_id, new_player.credentials            

        # Establish a websocket connection
        ws : WebSocket
        async with websocket_connection(room.room_id, player_id, credentials) as ws:
            data = await ws.receive_json()
            game_state = ActionSchema.model_validate_json(data)

        # Assertions
        assert game_state.action == "game_state"
        room_data : RoomSchema = game_state.data
        assert room_data.room_id == self.room.room_id
        assert room_data.you.player_id == player_id
        assert room_data.host_id == self.room.player_id
        assert (len(room_data.players) == 1 and expected_host_status) or len(room_data.players) == 2
        assert player_id in room_data.players
        assert room_data.players[player_id].is_host == expected_host_status
        assert room_data.players[player_id].is_connected
    
    # Test joining a non-existent room
    # Expected to fail
    @pytest.mark.parametrize("room_id, player_id, credentials, expected message", [
        ("invalid_room", room.player_id, room.credentials, "Room not found"),
        (room.room_id, "invalid_player", room.credentials, "User not found"),
        (room.room_id, room.player_id, "invalid_credentials", "Invalid credentials"),
    ])
    async def test_invalid_join(self, room_id, player_id, credentials, expected_message, websocket_connection):
        with pytest.raises(WebSocketDisconnect) as e:
            with websocket_connection(room_id, player_id, credentials) as ws:
                pass
        assert e.value.code == 4001
        assert e.value.reason == expected_message
    
    # Test missing parameters
    # Expected to fail
    @pytest.mark.parametrize("room_id, player_id, credentials", [
        (None, room.player_id, room.credentials),
        (room.room_id, None, room.credentials),
        (room.room_id, room.player_id, None),
    ])
    async def test_missing_parameters(self, room_id, player_id, credentials, websocket_connection):
        with pytest.raises(WebSocketDisconnect) as e:
            with websocket_connection(room_id, player_id, credentials) as ws:
                pass
        assert e.value.code == 4001
        assert e.value.reason == "Missing parameters"
    
    # Test other player joining the room
    async def test_other_player_join(self, websocket_connection, join_room):
            
        # First player joins
        ws : WebSocket
        with websocket_connection(self.room.room_id, self.room.player_id, self.room.credentials) as ws:
            ws.receive_json() # Initial room data

            # Second player joins
            player2_data : RoomJoinResponse = await join_room(self.room.room_id, "other_user")
            ws2 : WebSocket
            with websocket_connection(self.room.room_id, player2_data.player_id, player2_data.credentials) as ws2:
                ws2.receive_json()
            
            # Convert to player join schema
            player_join = ws.receive_json()
            player_join = ActionSchema.model_validate_json(player_join)

        # Assertions first player
        assert isinstance(player_join, ActionSchema)
        assert player_join.action == "player_join"
        assert player_join.data.nickname == "other_user"
        assert player_join.data.player_id == player2_data.player_id