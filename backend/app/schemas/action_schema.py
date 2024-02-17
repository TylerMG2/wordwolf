from pydantic import BaseModel
from app.schemas.room_schema import RoomSchema
from app.schemas.player_schema import PlayerSchema, OtherPlayerSchema, PlayerIdSchema
from enum import Enum

# Action types
class OutgoingActionType(str, Enum):
    PLAYER_CONNECTED = "player_connected"
    PLAYER_DISCONNECTED = "player_disconnected"
    PLAYER_LEFT = "player_left"
    HOST_CHANGED = "host_changed"
    GAME_STARTED = "game_started"
    GAME_STATE = "game_state"
    ERROR = "error"

class IncomingActionType(str, Enum):
    START_GAME = "start_game"
    LEAVE_ROOM = "leave_room"

# Base action schemas
class OutgoingActionSchema(BaseModel):
    action: OutgoingActionType
    data: RoomSchema | OtherPlayerSchema | PlayerSchema | int | str

class IncomingActionSchema(BaseModel):
    action: IncomingActionType
    data: PlayerSchema | str | int