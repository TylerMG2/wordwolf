import pytest
from httpx import AsyncClient
from app.routers.room import RoomResponse
from app.main import app

client = AsyncClient(app=app, base_url="http://test")

# Test creating a room
@pytest.mark.asyncio
async def test_create_room():
    response = await client.post("/api/rooms", json={"nickname": "test"})
    assert response.status_code == 200
    response = RoomResponse(**response.json())
    assert response.room_id != None
    assert response.player_id != None
    assert response.credentials != None

# Test joining a room
@pytest.mark.asyncio
async def test_join_room():

    # Create a room
    response = await client.post("/api/rooms", json={"nickname": "test"})
    room_info = RoomResponse(**response.json())

    # Join the room
    response = await client.post(f"/api/rooms/{room_info.room_id}", json={"nickname": "test2"})
    assert response.status_code == 200
    response = RoomResponse(**response.json())

    # Check the response
    assert response.room_id == room_info.room_id
    assert response.player_id != None
    assert response.credentials != None

# Test missing parameters
@pytest.mark.parametrize("url", [
    "/api/rooms",
    "/api/rooms/invalid_room_id"
])
@pytest.mark.asyncio
async def test_missing_parameters(url):
    response = await client.post(url, json={})
    assert response.status_code == 422

# Test joining a non-existent room
@pytest.mark.asyncio
async def test_join_non_existent_room():
    response = await client.post("/api/rooms/invalid_room_id", json={"nickname": "test"})
    assert response.status_code == 404
    
    
    