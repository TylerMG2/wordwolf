from fastapi import WebSocket
from app.schemas.player_schema import PlayerSchema, OtherPlayerSchema
import uuid

# Player class
class PlayerManager:

    websocket: WebSocket
    player_id: int
    nickname: str
    credentials: str
    word: str = ""
    is_host: bool = False
    is_connected: bool = False
    is_spy: bool = False

    def __init__(self, player_id: int, nickname: str, is_host: bool):
        self.player_id = player_id
        self.nickname = nickname
        self.is_host = is_host
        self.credentials = str(uuid.uuid4())

    # Set player as connected
    def connect(self, websocket: WebSocket):
        self.websocket = websocket
        self.is_connected = True

    # Set player as disconnected
    def disconnect(self):
        self.is_connected = False
        self.websocket = None
    
    # Convert to player schema
    def to_player_schema(self):
        return PlayerSchema(
            player_id=self.player_id,
            nickname=self.nickname,
            is_connected=self.is_connected,
            is_host=self.is_host,
            is_spy=self.is_spy,
            word=self.word
        )

    # Convert to other player schema
    def to_other_player_schema(self):
        return OtherPlayerSchema(
            player_id=self.player_id,
            nickname=self.nickname,
            is_connected=self.is_connected,
            is_host=self.is_host
        )