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

# Test get next players turn
def test_game_manager_get_next_players_turn():
    room = RoomManager(1)
    game_manager = GameManager(room)
    p1, p2, p3 = PlayerManager(1, "test", False), PlayerManager(2, "test", False), PlayerManager(3, "test", False)
    p1.connect(MockWebsocket())
    p2.connect(MockWebsocket())
    p3.connect(MockWebsocket())
    game_manager.players = [p1, p2, p3]
    game_manager.turn = 0

    # Check the next player
    game_manager.next_turn()
    assert game_manager.turn == 1
    game_manager.next_turn()
    assert game_manager.turn == 2
    game_manager.next_turn()
    assert game_manager.turn == 0

    # Disconnect a player
    p2.disconnect()
    game_manager.next_turn()
    assert game_manager.turn == 2
    game_manager.next_turn()
    assert game_manager.turn == 0

