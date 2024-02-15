import pytest
from fastapi.testclient import TestClient
from app.main import app
from .test_fixtures import test_room

# Constants
USERNAME = "test user"
USER_ID = "test_user_id"

# Function for checking if a user joined a room
async def check_user_joined_room(data):
    assert "is_host" in data
    assert "players" in data
    assert "game_state" in data

# Test room joining as a host
# Expected to succeed
@pytest.mark.asyncio
async def test_join_room_as_host(test_room):
    room_code = (await test_room(USER_ID))["code"]

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&user_id={USER_ID}&username={USERNAME}") as ws:
        data = ws.receive_json()

        # Check if the user joined the room
        await check_user_joined_room(data)

        # Assert that we are the host
        assert data["is_host"] == True

# Test room joining as a player
# Expected to succeed
@pytest.mark.asyncio
async def test_join_room_as_player(test_room):
    room_code = (await test_room)["code"]

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&user_id={USER_ID}&username={USERNAME}") as ws:
        data = ws.receive_json()

        # Check if the user joined the room
        await check_user_joined_room(data)

        # Assert that we are the host
        assert data["is_host"] == False

# Test attempting to join a non-existent room
# Expected to fail
@pytest.mark.asyncio
async def test_join_non_existent_room():
    
    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room=1234&user_id={USER_ID}&username={USERNAME}") as ws:
        data = ws.receive_json()

        # Assert that the response is correct
        assert data == {"message": "Room not found"}

# Test attempting to join a room with no username
# Expected to succeed
@pytest.mark.asyncio
async def test_join_room_no_username(test_room):
    room_code = (await test_room)["code"]

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&user_id={USER_ID}") as ws:
        data = ws.receive_json()

        # Assert that the response contains the room state
        assert "is_host" in data
        assert "players" in data
        assert "game_state" in data

# Test attempting to join a room with no user_id
# Expected to fail
@pytest.mark.asyncio
async def test_join_room_no_user_id(test_room):
    room_code = (await test_room)["code"]

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&username={USERNAME}") as ws:
        data = ws.receive_json()

        # Assert that the response is correct
        assert data == {"message": "User ID not provided"}

# Test attempting to join a room with no room code
# Expected to fail
@pytest.mark.asyncio
async def test_join_room_no_room_code():
        
    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?user_id={USER_ID}&username={USERNAME}") as ws:
        data = ws.receive_json()

        # Assert that the response is correct
        assert data == {"message": "Room code not provided"}