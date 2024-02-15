import pytest
from fastapi.testclient import TestClient
from app.main import app

# Constants
USERNAME = "test user"
USER_ID = "test_user_id"

# Test websocket disconnection
# Expected to succeed
@pytest.mark.asyncio
async def test_leave_room(create_room):
    room_code = await create_room(user_id=USER_ID)

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&user_id={USER_ID}&username={USERNAME}") as ws:
        # Close the websocket connection
        await ws.close()

        # Check if the user left the room
        with pytest.raises(Exception):
            await ws.receive_json()