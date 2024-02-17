import pytest
import pytest_asyncio
from starlette.websockets import WebSocketDisconnect
from app.schemas import RoomSchema, RoomJoinResponse, ActionSchema
from starlette.websockets import WebSocket

@pytest.mark.asyncio
class TestPlayerJoin:

    NICKNAME = "Test User"
    room : RoomJoinResponse = None

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, create_room):
        self.room = await create_room(nickname=self.NICKNAME)

    # Test joining the room
    @pytest.mark.parametrize("user_role, expected_host_status", [
        ("host", True),
        ("other_user", False),
    ])
    async def test_user_join(self, user_role, expected_host_status, websocket_connection, join_room):

        # If the user is not the host, join the room
        player_id, credentials = self.room.player_id, self.room.credentials
        if user_role != "host":
            new_player : RoomJoinResponse = await join_room(self.room.room_id, user_role)
            player_id, credentials = new_player.player_id, new_player.credentials            
        print(self.room.room_id, player_id, credentials)
        # Establish a websocket connection
        ws : WebSocket
        with websocket_connection(self.room.room_id, player_id, credentials) as ws:
            data = ws.receive_json()
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
    
    # Test joining a room with invalid parameters
    @pytest.mark.parametrize("valid_room_id, valid_player_id, valid_credentials, error_message", [
        (False, True, True, "Room not found"),
        (True, False, True, "Player not found"),
        (True, True, False, "Invalid credentials"),
    ])
    async def test_invalid_parameters(self, valid_room_id, valid_player_id, valid_credentials, error_message, websocket_connection):
        with pytest.raises(WebSocketDisconnect) as e:

            # Set invalid parameters
            if valid_room_id:
                self.room.room_id = "invalid_room_id"
            if valid_player_id:
                self.room.player_id = 999
            if valid_credentials:
                self.room.credentials = "invalid_credentials"

            with websocket_connection(self.room.room_id, self.room.player_id, self.room.credentials) as ws:
                pass
        print(e)
        assert e.value.code == 4001
        assert e.value.reason == error_message

    # Test missing parameters
    # Expected to fail
    @pytest.mark.parametrize("room_id, player_id, credentials, error_message", [
        (None, True, True, "No room_id provided"),
    ])
    async def test_missing_parameters(self, room_id, player_id, credentials, error_message, websocket_connection):
        with pytest.raises(WebSocketDisconnect) as e:
            with websocket_connection(room_id, player_id, credentials) as ws:
                pass
        assert e.value.code == 4001
        assert e.value.reason == "No room_id provided" if room_id is None else "No player_id provided" if player_id is None else "No credentials provided"
    
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