from app.managers import ConnectionManager, GameManager, RoomManager, PlayerManager
from ..unit.mock_websocket import MockWebsocket
from app.schemas import RoomEvent, EventSchema, GameState, PlayerRoleSchema
import pytest

# Test game manager to schema
@pytest.mark.asyncio
async def test_game_manager_to_schema():
    room = RoomManager(1)
    player1 = room.add_player("test", True)
    player1.connect(MockWebsocket())
    player2 = room.add_player("test")
    player2.connect(MockWebsocket())
    player3 = room.add_player("test")
    player3.connect(MockWebsocket())
    game_manager = GameManager(room)
    await game_manager.start_game(player1)
    schema = game_manager.to_schema(PlayerRoleSchema(is_spy=True, word="test"))

    # Check the schema
    assert schema.game_state == GameState.IN_PROGRESS
    assert len(schema.players) == 3
    assert schema.role.is_spy == True
    assert schema.role.word == "test"

    game_manager.game_timer.cancel()