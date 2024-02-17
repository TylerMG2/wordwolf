from .mock_websocket import MockWebsocket
from app.managers import RoomManager

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


