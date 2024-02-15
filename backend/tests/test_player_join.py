import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app


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
        with websocket_connection(self.room_code, user_id, username) as ws:
            data = ws.receive_json()

            # Check if the user joined the room
            assert "is_host" in data
            assert "players" in data
            assert "game_state" in data

            # Check if the user is in the players list
            assert user_id in data["players"]

            # Assert that we are the host
            assert data["is_host"] == is_host
    
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