from app.managers import PlayerManager
from .mock_websocket import MockWebsocket
from app.schemas import RoomEvent
import pytest

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

# Test to_schema method
def test_to_schema():
    player = PlayerManager(1, "test", False)
    schema = player.to_schema()
    assert schema.player_id == 1
    assert schema.nickname == "test"
    assert schema.is_connected == False
    assert schema.is_host == False

# Test send method
@pytest.mark.asyncio
async def test_send():
    player = PlayerManager(1, "test", False)
    ws = MockWebsocket()
    player.connect(ws)
    await player.send(RoomEvent.ERROR, "test")
    last_event = ws.data.pop()
    assert last_event.action == RoomEvent.ERROR
    assert last_event.data == "test"