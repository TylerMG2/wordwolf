from .player_manager import PlayerManager
from ..schemas import ActionSchema, RoomSchema

# Room class
class RoomManager:

    room_id: str
    host_id: int
    players: dict[int, PlayerManager]
    game_state: str

    # Init room
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players = {}
        self.game_state = "lobby"
    
    # Add a player to the room
    def add_player(self, nickname: str, is_host: bool = False) -> PlayerManager:
        
        # Find the next available player id
        player_id = 0
        while player_id in self.players:
            player_id += 1

        # If the player is the host, set the host
        if is_host:
            self.host_id = player_id

        # Create the player
        player = PlayerManager(player_id, nickname, is_host)
        self.players[player_id] = player

        return player

    # Remove a player from the room
    def remove_player(self, player_id: int):
        del self.players[player_id]
    
    # Check if all players are disconnected
    def all_players_disconnected(self) -> bool:
        for player in self.players.values():
            if player.is_connected:
                return False
        return True

    # Convert to room schema
    def to_schema(self, player_id: int) -> RoomSchema:
        return RoomSchema(
            room_id=self.room_id,
            host_id=self.host_id,
            players={player_id: player.to_other_player_schema() for player_id, player in self.players.items()},
            game_state=self.game_state,
            you=self.players[player_id].to_player_schema()
        )

    # Send message to all players in the room
    async def broadcast(self, message: ActionSchema):
        for player in self.players.values():
            if player.is_connected:
                await player.websocket.send_json(message.model_dump_json())
    
    # Send message to all players in the room except the sender
    async def broadcast_except(self, message: ActionSchema, sender_id: int):
        for player_id, player in self.players.items():
            if player_id != sender_id and player.is_connected:
                await player.websocket.send_json(message.model_dump_json())
    
    # Send message to a specific player
    async def send_to(self, message: ActionSchema, receiver_id: int):
        await self.players[receiver_id].websocket.send_json(message.model_dump_json())