from app.managers import PlayerManager
from .mock_websocket import MockWebsocket

# Test connect method
def test_player_connect():
    player = PlayerManager(1, "test", False)
    player.connect(MockWebsocket())
    assert player.is_connected == True
    assert player.websocket != None

# Test disconnect method
def test_player_disconnect():
    player = PlayerManager(1, "test", False)
    player.connect(MockWebsocket())
    player.disconnect()
    assert player.is_connected == False
    assert player.websocket == None

# Test to_player_schema method
def test_to_player_schema():
    player = PlayerManager(1, "test", False)
    schema = player.to_player_schema()
    assert schema.player_id == 1
    assert schema.nickname == "test"
    assert schema.is_connected == False
    assert schema.is_host == False
    assert schema.is_spy == False
    assert schema.word == ""

# Test to_other_player_schema method
def test_to_other_player_schema():
    player = PlayerManager(1, "test", False)
    schema = player.to_other_player_schema()
    assert schema.player_id == 1
    assert schema.nickname == "test"
    assert schema.is_connected == False
    assert schema.is_host == False