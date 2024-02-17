from app.schemas import RoomSchema
from app.websocket_manager.player_manager import Player

# Room class
class Room:

    room_id: str
    host_id: int
    players: dict[str, Player] = {}
    game_state: str = "lobby"

    # Init room
    def __init__(self, room_id: str):
        self.room_id = room_id

    # Add a player to the room
    async def add_player(self, username: str, is_host: bool = False) -> tuple[int, str]:
        
        # Find the next available player id
        player_id = 0
        while player_id in self.players:
            player_id += 1

        # If the player is the host, set the host
        if is_host:
            self.host = player_id

        # Create the player
        player = Player(player_id, username, is_host)
        self.players[player_id] = player

        return player_id, player.credentials

    # Convert to room schema
    def to_schema(self, player_id: int) -> RoomSchema:
        return RoomSchema(
            room_id=self.room_id,
            host_id=self.host_id,
            players={player_id: player.to_other_player_schema() for player_id, player in self.players.items()},
            game_state=self.game_state,
            you=self.players[player_id].to_player_schema()
        )
    
    # # Add a player to the room
    # def player_join(self, websocket: WebSocket, user_id: str, username: str):
    #     player = Player(len(self.players), username, False)
    #     player.websocket = websocket
    #     self.players[user_id] = player

    # Send message to all players in the room
    # async def broadcast(self, message: ActionSchema):
    #     for player in self.players.values():
    #         await player.websocket.send_json(message.model_dump_json())
    
    # # Send message to all players in the room except the sender
    # async def broadcast_except(self, message: ActionSchema, sender: str):
    #     for user_id, player in self.players.items():
    #         if user_id != sender:
    #             await player.websocket.send_json(message.model_dump_json())
        
    # # Send message to a specific player
    # async def send_to(self, message: ActionSchema, receiver: str):
    #     await self.players[receiver].websocket.send_json(message.model_dump_json())