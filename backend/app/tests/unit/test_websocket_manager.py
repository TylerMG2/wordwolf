import pytest
from app.managers import WebsocketManager, RoomManager, PlayerManager
from .mock_websocket import MockWebsocket

# Fixture for the WebsocketManager
@pytest.fixture
def manager():
    return WebsocketManager()

# Fixture for creating a room
@pytest.fixture
def room(manager):
    return manager.create_room()

# Fixture for connecting a player
@pytest.fixture
def connect_player(manager: WebsocketManager, room: RoomManager):
    async def _connect(nickname="test", host=False) -> tuple[PlayerManager, MockWebsocket]:
        player = room.add_player(nickname, host)
        ws = MockWebsocket()
        await manager.player_connected(room.room_id, player.player_id, player.credentials, ws)
        return player, ws
    return _connect

# Test create_room method
def test_create_room(manager: WebsocketManager):
    previous_rooms = manager.rooms.copy()
    room = manager.create_room()

    # Check the room
    assert room is not None
    assert room.room_id is not None
    assert room.room_id in manager.rooms
    assert room.room_id not in previous_rooms

# Test player connection
@pytest.mark.asyncio
async def test_player_connected(connect_player):
    player, ws = await connect_player("test")

    # Check that the player's status was changed
    assert player.is_connected == True
    assert player.websocket is not None

# Test multiple players connection and notification
@pytest.mark.asyncio
async def test_multiple_players_connected(connect_player):
    player1, ws1 = await connect_player("test1")
    player2, ws2 = await connect_player("test2")
    player3, _ = await connect_player("test3")

    # Check that all players are connected
    assert all([player1.is_connected, player2.is_connected, player3.is_connected])

    # Check that the first and second players were notified about the third player's join
    latest_data_ws1 = ws1.data[-1]
    latest_data_ws2= ws2.data[-1]
    assert latest_data_ws1.action == "played_connected"
    assert latest_data_ws1.data.player_id == player3.player_id
    assert latest_data_ws2.action == "played_connected"
    assert latest_data_ws2.data.player_id == player3.player_id

# Test player disconnection
@pytest.mark.asyncio
async def test_player_disconnected(room: RoomManager, connect_player, manager: WebsocketManager):
    player1, _ = await connect_player("test1")
    _, ws2 = await connect_player("test2")

    await manager.player_disconnected(room, player1)

    # Check that player1's status was changed
    assert player1.is_connected == False
    assert player1.websocket is None

    # Check that player2 was notified about player1's disconnection
    latest_data = ws2.data[-1]
    assert latest_data.action == "player_disconnected"
    assert latest_data.data.player_id == player1.player_id

# Test removal of room after all players are disconnected
@pytest.mark.asyncio
async def test_room_removal_on_all_disconnected(room : RoomManager, connect_player, manager: WebsocketManager):
    player1, _ = await connect_player("test1")
    player2, _ = await connect_player("test2")

    await manager.player_disconnected(room, player1)
    await manager.player_disconnected(room, player2)

    # Check that the room was removed after all players disconnected
    assert room.room_id not in manager.rooms

# Test normal player leaving
@pytest.mark.asyncio
async def test_player_leaving(room, connect_player, manager: WebsocketManager):
    player1, ws1 = await connect_player("test1", True)
    player2, ws2 = await connect_player("test2")
    player3, ws3 = await connect_player("test3")

    await manager.player_left(room, player2)

    # Check that the player was removed
    assert player2.player_id not in room.players

    # Check that other players were notified about the player leaving
    assert ws1.data.action == "player_left"
    assert ws1.data.data.player_id == player2.player_id
    assert ws3.data.action == "player_left"
    assert ws3.data.data.player_id == player2.player_id

# Test host leaving does not remove room immediately
@pytest.mark.asyncio
async def test_host_leaving(room, connect_player, manager: WebsocketManager):
    player1, ws1 = await connect_player("host", True)
    player2, ws2 = await connect_player("guest")

    await manager.player_left(room, player1)

    # Check that the room was removed
    assert room.room_id not in manager.rooms

    # Check that the guest was notified about the host leaving
    assert ws2.code == 1000
    assert ws2.reason == "Host left the room"