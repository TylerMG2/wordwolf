from .room_manager import RoomManager
from .player_manager import PlayerManager
from ..schemas import RoomEvent, PlayerRoleSchema, GameState, GameSchema, ActionTypes, EventDataTypes
from random import choice, shuffle

# Game manager class for managing the game logic
class GameManager:

    state: GameState
    room: RoomManager
    players: list[PlayerManager]
    turn: int
    spy: PlayerManager
    spy_word: str
    word: str

    # Init game manager
    def __init__(self, room: RoomManager):
        self.state = GameState.LOBBY
        self.room = room
        self.spy = None

    # To schema
    def to_schema(self, role: PlayerRoleSchema) -> GameSchema:
        return GameSchema(
            players=[player.to_schema() for player in self.players],
            game_state=self.state,
            player_turn=self.turn,
            role=role
        )
    
    ### Broadcast events to players
    async def broadcast(self, action: ActionTypes, data: EventDataTypes):
        for player in self.players:
            await player.send(action, data)
    
    # Broadcast except
    async def broadcast_except(self, action: ActionTypes, data: EventDataTypes, player_id):
        for player in self.players:
            if player.player_id != player_id:
                await player.send(action, data)

    # Starts the game for a room
    async def start_game(self, player: PlayerManager) -> bool:

        # Get the players
        self.players = self.room.get_connected_players()

        # Checks
        if player.player_id != self.room.host_id:
            await player.send(RoomEvent.ERROR, "Only the host can start the game")
            return False

        # Check if the room has enough players
        if len(self.players) < 3:
            await player.send(RoomEvent.ERROR, "Cannot start game with less than 3 players")
            return False
        
        # Check if the room is already in a game
        if self.state != GameState.LOBBY:
            await player.send(RoomEvent.ERROR, "The game has already started")
            return False
        
        # Start the game
        self.state = GameState.IN_PROGRESS
        self.room.game_state = self.state

        # Setup
        self.spy = choice(self.players)
        self.word = "test"
        self.spy_word = "spy"
        self.turn = 0
        shuffle(self.players)

        # Roles
        spy_role = PlayerRoleSchema(is_spy=True, word=self.spy_word)
        player_role = PlayerRoleSchema(is_spy=False, word=self.word)

        # Send the game started event with different roles to each player
        await self.spy.send(RoomEvent.GAME_START, self.to_schema(spy_role))
        await self.broadcast_except(RoomEvent.GAME_START, self.to_schema(player_role), self.spy.player_id)
        return True
        