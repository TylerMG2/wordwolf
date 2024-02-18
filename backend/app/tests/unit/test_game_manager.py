from app.managers import ConnectionManager, GameManager, RoomManager, PlayerManager
from .mock_websocket import MockWebsocket
from app.schemas import RoomEvent
import pytest

# Fixture for ConnectionManager
@pytest.fixture
def manager():
    return ConnectionManager()

# Fixture for the GameManager
@pytest.fixture
def game_manager():
    return GameManager()

# Fixture for creating a room
@pytest.fixture
def room(manager: ConnectionManager):
    return manager.create_room()

# Fixture for connecting a player to a room
@pytest.fixture
def connect_player(manager: ConnectionManager, room: RoomManager):
    async def _connect(nickname="test", host=False) -> tuple[PlayerManager, MockWebsocket]:
        player = room.add_player(nickname, host)
        ws = MockWebsocket()
        await manager.player_connected(room.room_id, player.player_id, player.credentials, ws)
        return player, ws
    return _connect

# Test start_game method with 3 players
@pytest.mark.asyncio
async def test_start_game(room: RoomManager, connect_player, game_manager: GameManager):

    # Create players
    host, ws1 = await connect_player("test1", True)
    _, ws2 = await connect_player("test2")
    _, ws3 = await connect_player("test3")

    # Start the game as the host
    await game_manager.start_game(room, host)

    # Check that the game has started
    assert room.game_state == "in_progress"

    # Check that all players have been notified
    for ws in [ws1, ws2, ws3]:
        assert ws.data[-1].action == RoomEvent.GAME_STARTED

    # Check that only one player has been told they are the spy
    spy_count = 0
    for ws in [ws1, ws2, ws3]:
        if ws.data[-1].data.is_spy:
            spy_count += 1
    assert spy_count == 1

    # Check that each player has been given the same word except the spy
    non_spy_word = None
    for ws in [ws1, ws2, ws3]:
        assert ws.data[-1].data.word is not None
        assert ws.data[-1].data.word != ""
        if not ws.data[-1].data.is_spy:
            if non_spy_word is None:
                non_spy_word = ws.data[-1].data.word
            else:
                assert non_spy_word == ws.data[-1].data.word

# Test start_game method with less than 3 players and not the host
@pytest.mark.parametrize("player_count, is_host, message", [
    (2, True, "Cannot start game with less than 3 players"), 
    (2, False, "Only the host can start the game"), 
    (1, True, "Cannot start game with less than 3 players"), 
    (1, False, "Only the host can start the game"),])
@pytest.mark.asyncio
async def test_start_game_invalid(room: RoomManager, connect_player, game_manager: GameManager, player_count, is_host, message):

    # Create first player
    host, ws1 = await connect_player("test1", is_host)

    # Create other players
    for i in range(player_count - 1):
        _, _ = await connect_player(f"test{i + 2}")

    # Start the game
    result = await game_manager.start_game(room, host)

    # Check that the game has not started
    assert not result
    assert room.game_state == "lobby"

    # Check that the requesting player was notified
    ws1_last_message = ws1.data.pop()
    assert ws1_last_message.action == RoomEvent.ERROR
    assert ws1_last_message.data == message

# Test start_game method with the game already started
@pytest.mark.asyncio
async def test_start_game_already_started(room: RoomManager, connect_player, game_manager: GameManager):
    
    # Create players
    host, ws1 = await connect_player("test1", True)
    _, ws2 = await connect_player("test2")
    _, ws3 = await connect_player("test3")

    # Start the game
    await game_manager.start_game(room, host)

    # Try to start the game again
    result = await game_manager.start_game(room, host)

    # Check that the game has not started
    assert not result
    assert room.game_state == "in_progress"

    # Check that the requesting player was notified
    ws1_last_message = ws1.data.pop()
    assert ws1_last_message.action == RoomEvent.ERROR
    assert ws1_last_message.data == "Game already started"

    
