import pytest
from app.managers import WebsocketManager
from .mock_websocket import MockWebsocket

manager = WebsocketManager()

# Test create_room method
def test_create_room():
    previous_rooms = manager.rooms.copy()
    room = manager.create_room()

    # Check the room
    assert room != None
    assert room.room_id != None
    assert room.room_id in manager.rooms
    assert room.room_id not in previous_rooms

# Test connect_to_room method
@pytest.mark.asyncio
async def test_player_connected():
    room = manager.create_room()
    player = room.add_player("test")
    room, player = await manager.player_connected(room.room_id, player.player_id, player.credentials, MockWebsocket())

    # Check that the players status was changed
    assert player.is_connected == True
    assert player.websocket != None

# Test disconnect_from_room method
@pytest.mark.asyncio
async def test_player_disconnected():
    room = manager.create_room()
    player = room.add_player("test")
    player_2 = room.add_player("test")
    room, player = await manager.player_connected(room.room_id, player.player_id, player.credentials, MockWebsocket())
    await manager.player_disconnected(room, player)

    # Check that the players status was changed
    assert player.is_connected == False
    assert player.websocket == None

# Test when all players are disconnected
@pytest.mark.asyncio
async def test_all_players_disconnected():
    room = manager.create_room()
    player = room.add_player("test")
    player_2 = room.add_player("test")
    room, player = await manager.player_connected(room.room_id, player.player_id, player.credentials, MockWebsocket())
    room, player_2 = await manager.player_connected(room.room_id, player_2.player_id, player_2.credentials, MockWebsocket())
    await manager.player_disconnected(room, player)

    # Check that the room is not removed
    assert room.room_id in manager.rooms
    
    await manager.player_disconnected(room, player_2)

    # Check that the room was removed
    assert room.room_id not in manager.rooms