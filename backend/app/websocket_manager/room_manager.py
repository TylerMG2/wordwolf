from fastapi import WebSocket
from app.schemas.player_schema import PlayerSchema, OtherPlayerSchema
from app.schemas.room_schema import RoomSchema
from pydantic import BaseModel

# Player class
class Player:
    def __init__(self, websocket: WebSocket ,username: str, is_host: bool):
        self.websocket = websocket
        self.username = username
        self.active = True
        self.word = ""
        self.is_host = is_host
        self.is_spy = False
    
    # Convert to player schema
    def to_player_schema(self, user_id: str):
        return PlayerSchema(
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
            username=self.username,
            active=self.active,
            is_host=self.is_host
        )

# Room class
class Room:
    def __init__(self, host: str):
        self.host: str = host
        self.players: dict[str, Player] = {}
        self.game_state: str = "waiting_for_players"

    # Convert to room schema
    def to_schema(self, user_id: str):
        return RoomSchema(
            players=[player.to_other_player_schema() for player in self.players.values()],
            game_state=self.game_state,
            you=self.players[user_id].to_player_schema(user_id)
        )
    
    # Player join
    def player_join(self, websocket: WebSocket, user_id: str, username: str):
        is_host = self.host == user_id
        
        # Check if the player is already in the room
        if user_id in self.players:
            self.players[user_id].websocket = websocket
            self.players[user_id].active = True
        else:
            # Add the player to the room
            self.players[user_id] = Player(websocket, username, is_host)

    # Send message to all players in the room
    async def broadcast(self, message: BaseModel):
        for player in self.players.values():
            await player.websocket.send_json(message.model_dump_json())
    
    # Send message to all players in the room except the sender
    async def broadcast_except(self, message: BaseModel, sender: str):
        for player in self.players.values():
            if player.user_id != sender:
                await player.websocket.send_json(message.model_dump_json())
        
    # Send message to a specific player
    async def send_to(self, message: BaseModel, receiver: str):
        await self.players[receiver].websocket.send_json(message.model_dump_json())