from .mock_websocket import MockWebsocket
from app.managers import RoomManager
from app.schemas import OutgoingActionSchema, OutgoingActionType
import pytest

# Test add_player method
def test_add_player():
    room = RoomManager(1)
    player = room.add_player("test")
    assert player.player_id == 0
    assert player.nickname == "test"
    assert player.is_connected == False
    assert player.is_host == False

# Test add_host method
def test_add_host():
    room = RoomManager(1)
    player = room.add_player("test", True)
    assert player.is_host == True

# Test remove player
def test_remove_player():
    room = RoomManager(1)
    player = room.add_player("test")
    room.remove_player(player.player_id)
    assert player.player_id not in room.players

# Test removing and adding a player
def test_remove_and_add_player():
    room = RoomManager(1)
    player = room.add_player("test")
    room.remove_player(player.player_id)
    player = room.add_player("test2")

    assert player.player_id in room.players
    assert player.player_id == 0 # The player id should be the same as the previous player
    assert player.nickname == "test2"

# Test getting if all players are disconnected
def test_all_players_disconnected():
    room = RoomManager(1)
    player = room.add_player("test")
    player_2 = room.add_player("test")
    player.connect(MockWebsocket())
    player_2.connect(MockWebsocket())
    assert room.all_players_disconnected() == False
    player.disconnect()
    assert room.all_players_disconnected() == False
    player_2.disconnect()
    assert room.all_players_disconnected() == True

# Test room broadcast
@pytest.mark.asyncio
async def test_room_broadcast():
    room = RoomManager(1)
    player = room.add_player("test")
    player_2 = room.add_player("test")
    player.connect(MockWebsocket())
    player_2.connect(MockWebsocket())
    await room.broadcast(OutgoingActionSchema(action=OutgoingActionType.GAME_STATE, data="test"))

    # Check that both players received the message
    assert len(player.websocket.data) == 1
    assert len(player_2.websocket.data) == 1
    assert player.websocket.data[0].action == OutgoingActionType.GAME_STATE
    assert player_2.websocket.data[0].action == OutgoingActionType.GAME_STATE
    assert player.websocket.data[0].data == "test"
    assert player_2.websocket.data[0].data == "test"

# Test room broadcast except
@pytest.mark.asyncio
async def test_room_broadcast_except():
    room = RoomManager(1)
    player = room.add_player("test")
    player_2 = room.add_player("test")
    player_3 = room.add_player("test")
    player.connect(MockWebsocket())
    player_2.connect(MockWebsocket())
    player_3.connect(MockWebsocket())
    await room.broadcast_except(OutgoingActionSchema(action=OutgoingActionType.GAME_STATE, data="test"), player.player_id)

    # Check that player 1 was not notified
    assert len(player.websocket.data) == 0

    # Check that the other players received the message
    assert len(player_2.websocket.data) == 1
    assert len(player_3.websocket.data) == 1
    assert player_2.websocket.data[0].action == OutgoingActionType.GAME_STATE
    assert player_3.websocket.data[0].action == OutgoingActionType.GAME_STATE
    assert player_2.websocket.data[0].data == "test"
    assert player_3.websocket.data[0].data == "test"

# Test room send to specific player
@pytest.mark.asyncio
async def test_room_send_to_specific_player():
    room = RoomManager(1)
    player = room.add_player("test")
    player_2 = room.add_player("test")
    player.connect(MockWebsocket())
    player_2.connect(MockWebsocket())
    await room.send_to(OutgoingActionSchema(action=OutgoingActionType.GAME_STATE, data="test"), player.player_id)

    # Check that just player 1 received the message
    assert len(player.websocket.data) == 1
    assert len(player_2.websocket.data) == 0
    assert player.websocket.data[0].action == OutgoingActionType.GAME_STATE
    assert player.websocket.data[0].data == "test"

# Test get all active players
def test_get_all_active_players():
    room = RoomManager(1)
    player = room.add_player("test")
    player_2 = room.add_player("test")
    player_3 = room.add_player("test")
    player.connect(MockWebsocket())
    player_2.connect(MockWebsocket())

    # Check that only the connected players are returned
    assert room.get_connected_players() == [player, player_2]

    player_3.connect(MockWebsocket())
    player_2.disconnect()

    # Check that the disconnected player is not returned
    assert room.get_connected_players() == [player, player_3]