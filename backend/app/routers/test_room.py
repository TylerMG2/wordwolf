from fastapi.testclient import TestClient
from .room import RoomResponse
from ..main import app

client = TestClient(app)

# Test creating a room
def test_create_room():
    response = client.post("/api/rooms/", json={"nickname": "test"})
    assert response.status_code == 200
    response = RoomResponse(**response.json())
    assert response.room_id != None
    assert response.player_id != None
    assert response.credentials != None

# Test joining a room
def test_join_room():

    # Create a room
    response = client.post("/api/rooms/", json={"nickname": "test"})
    room_info = RoomResponse(**response.json())

    # Join the room
    response = client.post(f"/api/rooms/{room_info.room_id}", json={"nickname": "test"})
    assert response.status_code == 200
    response = RoomResponse(**response.json())

    # Check the response
    assert response.room_id == room_info.room_id
    assert response.player_id != None
    assert response.credentials != None

# Test missing parameters
def test_missing_parameters():
    response = client.post("/api/rooms/", json={})
    assert response.status_code == 422
    response = client.post("/api/rooms/invalid_room_id", json={})
    assert response.status_code == 422

# Test joining a non-existent room
def test_join_non_existent_room():
    response = client.post("/api/rooms/invalid_room_id", json={"nickname": "test"})
    assert response.status_code == 404
    
    
    