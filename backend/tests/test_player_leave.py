import pytest
from fastapi.testclient import TestClient
from app.main import app

# Constants
USERNAME = "test user"
USER_ID = "test_user_id"

# Test leaving a room as a player
@pytest.mark.asyncio
async def test_leave_room_as_player(test_room):
    room_code = (await test_room)["code"]

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&user_id={USER_ID}&username={USERNAME}") as ws:
        data = ws.receive_json()

        # Send a leave message
        await ws.send_json({"action": "leave"})

        # Check if the user left the room
        data = ws.receive_json()
        assert data == {"message": "Left room"}