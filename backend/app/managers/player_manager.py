from fastapi import WebSocket
from ..schemas import PlayerSchema, EventSchema, ActionTypes, EventDataTypes
import uuid

# Player class
class PlayerManager:

    websocket: WebSocket
    player_id: int
    nickname: str
    credentials: str
    is_host: bool = False
    is_connected: bool = False

    def __init__(self, player_id: int, nickname: str, is_host: bool):
        self.websocket = None
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
    def to_schema(self):
        return PlayerSchema(
            player_id=self.player_id,
            nickname=self.nickname,
            is_connected=self.is_connected,
            is_host=self.is_host,
        )

    # Send an event to the player
    async def send(self, action: ActionTypes, data: EventDataTypes):

        # Build the event
        event = EventSchema(action=action, data=data)
        
        # If the player is connected, send the event
        if self.is_connected:
            await self.websocket.send_json(event.model_dump_json())