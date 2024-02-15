import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app

# Constants
USERNAME = "test user"
USER_ID = "test_user_id"

# Function for checking if a user joined a room
async def check_user_joined_room(data):
    assert "is_host" in data
    assert "players" in data
    assert "game_state" in data

    # Check if the user is in the players list
    assert USER_ID in data["players"]

# Test room joining as a host
# Expected to succeed
@pytest.mark.asyncio
async def test_join_room_as_host(create_room):
    room_code = await create_room(user_id=USER_ID)

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
async def test_join_room_as_player(create_room):
    room_code = await create_room()

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
        assert data == {"message": "Room does not exist"}

# Test attempting to join a room with no username
# Expected to succeed
@pytest.mark.asyncio
async def test_join_room_no_username(create_room):
    room_code = await create_room()

    # Try and establish a websocket connection
    client = TestClient(app)
    with client.websocket_connect(f"/ws?room={room_code}&user_id={USER_ID}") as ws:
        data = ws.receive_json()

        # Assert that the response contains the room state
        await check_user_joined_room(data)

# Test attempting to join a room with no user_id
# Expected to fail
@pytest.mark.asyncio
async def test_join_room_no_user_id(create_room):
    room_code = await create_room()

    # Try and establish a websocket connection
    client = TestClient(app)
    try:
        with client.websocket_connect(f"/ws?room={room_code}&username={USERNAME}") as ws:
            
            # If the connection was successful, the test failed
            assert ws is None
    except WebSocketDisconnect as e:
        assert e.code == 4001
        assert e.reason == "User ID not provided"
    


# Test attempting to join a room with no room code
# Expected to fail
@pytest.mark.asyncio
async def test_join_room_no_room_code(create_room):
    room_code = await create_room()

    # Try and establish a websocket connection
    client = TestClient(app)
    try:
        with client.websocket_connect(f"/ws?user_id={USER_ID}&username={USERNAME}") as ws:
            
            # If the connection was successful, the test failed
            assert ws is None
    except WebSocketDisconnect as e:
        assert e.code == 4001
        assert e.reason == "Room code not provided"