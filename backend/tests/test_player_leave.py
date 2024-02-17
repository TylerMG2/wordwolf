import pytest
import pytest_asyncio
from starlette.websockets import WebSocket
from app.main import manager
from backend.app.schemas.action_schema import ActionSchema

@pytest.mark.asyncio
class TestPlayerLeave:

    USERNAME = "test user"
    USER_ID = "test_user_id"
    HOST_ID = "test_host_id"
    room_code : str

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, create_room):
        self.room_code = await create_room(user_id=self.HOST_ID)

    # Test disconnecting from the room
    async def test_player_disconnect(self, websocket_connection):

        # Try and establish a websocket connection
        ws : WebSocket
        with websocket_connection(self.room_code, self.USER_ID, self.USERNAME) as ws:

            # Check if the user joined the room
            room_details = manager.rooms[self.room_code]
            assert self.USER_ID in room_details.players
            assert room_details.players[self.USER_ID].active == True

            # Disconnect from the room
            ws.close()

        # Check if the user left the room
        room_details = manager.rooms[self.room_code]
        assert self.USER_ID in room_details.players
        assert room_details.players[self.USER_ID].active == False
    
    # Test player leaving the room
    async def test_player_leave(self, websocket_connection):

        # Try and establish a websocket connection
        ws : WebSocket
        with websocket_connection(self.room_code, self.USER_ID, self.USERNAME) as ws:
            ws.receive_json()

            # Check if the user joined the room
            room_details = manager.rooms[self.room_code]
            assert self.USER_ID in room_details.players
            assert room_details.players[self.USER_ID].active == True

            # Leave the room
            ws.send_json({"action": "leave", "room_code": self.room_code})

            data = ws.receive_json()
            assert "message" in data
            assert data["message"] == "Left room"

        # Check if the user left the room
        room_details = manager.rooms[self.room_code]
        assert self.USER_ID not in room_details.players
    
    # Test player leaving whilst other players are in the room
    async def test_player_leave_other_players(self, websocket_connection):

        # First player joins
        ws : WebSocket
        with websocket_connection(self.room_code, self.USER_ID, self.USERNAME) as ws:
            ws.receive_json()

            # Second player joins
            ws2 : WebSocket
            with websocket_connection(self.room_code, "other_user_id", "other_user") as ws2:
                ws2.receive_json()

                # Leave the room
                ws2.send_json({"action": "leave", "room_code": self.room_code})

            # Receive the join message
            player_join = ws.receive_json()
            player_join = ActionSchema.model_validate_json(player_join)

            # Receive the leave message
            player_leave = ws.receive_json()
            player_leave = ActionSchema.model_validate_json(player_leave)
        
        # Assertions
        assert player_leave.action == "player_leave"
        assert player_leave.data["id"] == player_join.data["id"]


