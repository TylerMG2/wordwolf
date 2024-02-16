import pytest
import pytest_asyncio

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
    async def test_player_disconnect(self, websocket_connection, fetch_room_details):

        # Try and establish a websocket connection
        with websocket_connection(self.room_code, self.USER_ID, self.USERNAME) as ws:

            # Check if the user joined the room
            room_details = await fetch_room_details(self.room_code, self.USER_ID)
            assert self.USER_ID in room_details["players"]
            assert room_details["players"][self.USER_ID]["active"] == True

            # Disconnect from the room
            ws.close()

        # Check if the user left the room
        room_details = await fetch_room_details(self.room_code, self.USER_ID)
        assert self.USER_ID in room_details["players"]
        assert room_details["players"][self.USER_ID]["active"] == False
    
    # Test player leaving the room
    async def test_player_leave(self, websocket_connection, fetch_room_details):

        # Try and establish a websocket connection
        with websocket_connection(self.room_code, self.USER_ID, self.USERNAME) as ws:
            ws.receive_json()

            # Check if the user joined the room
            room_details = await fetch_room_details(self.room_code, self.USER_ID)
            assert self.USER_ID in room_details["players"]

            # Leave the room
            ws.send_json({"action": "leave", "room_code": self.room_code})

            data = ws.receive_json()
            assert "message" in data
            assert data["message"] == "Left room"

        # Check if the user left the room
        room_details = await fetch_room_details(self.room_code, self.USER_ID)
        assert self.USER_ID not in room_details["players"]
