from fastapi import WebSocket
from app.schemas.player_schema import PlayerSchema, OtherPlayerSchema
from app.schemas.action_schemas import ActionSchema
from app.schemas.room_schema import RoomSchema
from pydantic import BaseModel
import uuid

# Player class
class Player:

    websocket: WebSocket
    player_id: int
    username: str
    credentials: str
    word: str = ""
    is_host: bool = False
    is_connected: bool = True
    is_spy: bool = False

    def __init__(self, player_id: int, username: str, is_host: bool):
        self.player_id = player_id
        self.username = username
        self.is_host = is_host
        self.credentials = str(uuid.uuid4())
    
    # Convert to player schema
    def to_player_schema(self, user_id: str):
        return PlayerSchema(
            player_id=self.player_id,
            username=self.username,
            active=self.active,
            word=self.word,
            is_host=self.is_host,
            is_spy=self.is_spy,
            user_id=user_id
        )

    # Convert to other player schema
    def to_other_player_schema(self):
        return OtherPlayerSchema(
            player_id=self.player_id,
            username=self.username,
            active=self.active,
            is_host=self.is_host
        )

# Room class
class RoomManager:

    host_id: int
    players: dict[str, Player] = {}
    game_state: str = "lobby"

    # Add a player to the room
    def add_player(self, username: str, is_host: bool = False) -> tuple[int, str]:
        
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

    # # Convert to room schema
    # def to_schema(self, user_id: str):
    #     return RoomSchema(
    #         players={player.player_id: player.to_other_player_schema() for player in self.players.values()},
    #         game_state=self.game_state,
    #         you=self.players[user_id].to_player_schema(user_id)
    #     )
    
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