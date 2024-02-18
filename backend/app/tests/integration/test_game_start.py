from app.managers import ConnectionManager, GameManager, RoomManager, PlayerManager
from ..unit.mock_websocket import MockWebsocket
from app.schemas import RoomEvent, EventSchema, GameState
import pytest

# Fixture for ConnectionManager
@pytest.fixture
def manager():
    return ConnectionManager()

# Fixture for creating a room
@pytest.fixture
def room(manager: ConnectionManager):
    return manager.create_room()

# Fixture for the GameManager
@pytest.fixture
def game_manager(room : RoomManager):
    room.game_state = GameState.LOBBY
    return GameManager(room)

# Fixture for connecting a player to a room
@pytest.fixture
def connect_player(manager: ConnectionManager, room: RoomManager):
    async def _connect(nickname="test", host=False) -> tuple[PlayerManager, MockWebsocket]:
        player = room.add_player(nickname, host)
        ws = MockWebsocket()
        await manager.player_connected(room.room_id, player.player_id, player.credentials, ws)
        return player, ws
    return _connect

# Fixture that returns a started game
@pytest.fixture
async def started_game(room: RoomManager, connect_player, game_manager: GameManager) -> tuple[PlayerManager, MockWebsocket, MockWebsocket, MockWebsocket]:
    # Create players
    host, ws1 = await connect_player("test1", True)
    _, ws2 = await connect_player("test2")
    _, ws3 = await connect_player("test3")

    # Start the game
    await game_manager.start_game(host)

    return host, ws1, ws2, ws3

# Test start_game method
@pytest.mark.asyncio
async def test_start_game(room: RoomManager, connect_player, game_manager: GameManager):

    # Create players
    host, ws1 = await connect_player("test1", True)
    _, ws2 = await connect_player("test2")
    _, ws3 = await connect_player("test3")

    await game_manager.start_game(host)

    # Check that the game has started
    assert room.game_state == GameState.IN_PROGRESS

    # Check that all players have been notified
    events : list[EventSchema] = [ws1.data.pop(), ws2.data.pop(), ws3.data.pop()]
    assert all([event.action == RoomEvent.GAME_START for event in events])

    # Check that only one player has been told they are the spy
    spy_count = 0
    for event in events:
        if event.data.role.is_spy:
            spy_count += 1
    assert spy_count == 1

    # Check that each player got a word
    assert all([event.data.role.word is not None for event in events])

    # Check that each player has been given the same word except the spy
    non_spy_word = None
    for event in events:
        if not event.data.role.is_spy:
            if non_spy_word is None:
                non_spy_word = event.data.role.word
            else:
                assert non_spy_word == event.data.role.word
    
    # Finally test that a game timer has been started
    assert game_manager.game_timer is not None
    assert not game_manager.game_timer.done()

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
    result = await game_manager.start_game(host)

    # Check that the game has not started
    assert not result
    assert room.game_state == GameState.LOBBY

    # Check that the requesting player was notified
    ws1_last_event : EventSchema = ws1.data.pop()
    assert ws1_last_event.action == RoomEvent.ERROR
    assert ws1_last_event.data == message

# Test start_game method with the game already started
@pytest.mark.asyncio
async def test_start_game_already_started(room: RoomManager, connect_player, game_manager: GameManager):
    
    # Create players
    host, ws1 = await connect_player("test1", True)
    _, ws2 = await connect_player("test2")
    _, ws3 = await connect_player("test3")

    # Start the game
    await game_manager.start_game(host)

    # Try to start the game again
    result = await game_manager.start_game(host)
    assert not result

    # Check that the requesting player was notified
    ws1_last_event : EventSchema = ws1.data.pop()
    assert ws1_last_event.action == RoomEvent.ERROR
    assert ws1_last_event.data == "The game has already started"

# Test start_game method with one disconnected player
@pytest.mark.asyncio
async def test_start_game_disconnected_player(room: RoomManager, connect_player, game_manager: GameManager):
        
        # Create players
        host, ws1 = await connect_player("test1", True)
        _, ws2 = await connect_player("test2")
        player3, ws3 = await connect_player("test3")
        player4, ws4 = await connect_player("test4")
    
        # Disconnect a player
        player3.disconnect()
    
        # Start the game
        result = await game_manager.start_game(host)
        assert result

        # Check that player4 is not in the game
        assert player4.player_id not in game_manager.players