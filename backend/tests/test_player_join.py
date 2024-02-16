import pytest
import pytest_asyncio
from starlette.websockets import WebSocketDisconnect
from app.schemas.player_schema import OtherPlayerSchema, PlayerSchema
from app.schemas.room_schema import RoomSchema
from app.schemas.action_schemas import ActionSchema
from starlette.websockets import WebSocket
from json import dumps

@pytest.mark.asyncio
class TestPlayerJoin:

    USERNAME = "test user"
    USER_ID = "test_user_id"
    HOST_ID = "test_host_id"
    room_code : str

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, create_room):
        self.room_code = await create_room(user_id=self.HOST_ID)

    # Test joining the room as a host and a player and no username
    @pytest.mark.parametrize("user_id, username, is_host", [
        (HOST_ID, USERNAME, True),
        (USER_ID, USERNAME, False),
        (USER_ID, None, False),
    ])
    async def test_join_room(self, user_id, username, is_host, websocket_connection):

        # Try and establish a websocket connection
        ws : WebSocket
        with websocket_connection(self.room_code, user_id, username) as ws:
            data = ws.receive_json()

            # Convert response to room schema
            action = ActionSchema.model_validate_json(data)

        # Assertions
        assert action.action == "game_state"
        assert all(isinstance(player, OtherPlayerSchema) for player in action.data.players.values())
        assert isinstance(action.data.you, PlayerSchema)
        assert action.data.you.is_host == is_host
        assert action.data.you.username == username or "No name"
        assert action.data.you.active == True
        assert action.data.you.user_id == user_id
    
    # Test other player joining the room
    async def test_other_player_join(self, websocket_connection):
            
        # First player joins
        ws : WebSocket
        with websocket_connection(self.room_code, self.USER_ID, self.USERNAME) as ws:
            ws.receive_json() # Initial room data

            # Second player joins
            ws2 : WebSocket
            with websocket_connection(self.room_code, "other_user_id", "other_user") as ws2:
                data = ws2.receive_json()
                join_action = ActionSchema.model_validate_json(data)
            
            # Convert to player join schema
            player_join = ws.receive_json()
            player_join = ActionSchema.model_validate_json(player_join)
        
        # Assertions second player
        assert len(join_action.data.players) == 2
        assert join_action.data.you.user_id == "other_user_id"

        # Assertions first player
        assert isinstance(player_join, ActionSchema)
        assert player_join.action == "player_join"
        assert player_join.data.username == "other_user"
    
    # Test joining a non-existent room
    # Expected to fail
    async def test_join_non_existent_room(self, websocket_connection):
        with pytest.raises(WebSocketDisconnect) as e:
            with websocket_connection("1234", self.USER_ID, self.USERNAME) as ws:
                pass
        assert e.value.code == 4001
        assert e.value.reason == "Room does not exist"
    
    # Test parameterized input validation
    # Expected to fail
    @pytest.mark.parametrize("room_code, user_id, expected_error", [
        ("test_room_code", None, "User ID not provided"),
        (None, "test user", "Room code not provided"),
    ])
    async def test_join_room_input_validation(self, room_code, user_id, expected_error, websocket_connection):
        with pytest.raises(WebSocketDisconnect) as e:
            with websocket_connection(room_code, user_id, self.USERNAME) as ws:
                pass
        assert e.value.code == 4001
        assert e.value.reason == expected_error