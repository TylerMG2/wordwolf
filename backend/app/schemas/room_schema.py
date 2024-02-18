from pydantic import BaseModel
from .player_schema import PlayerSchema
from .game_schema import GameSchema
from enum import Enum

# Room states
class RoomState(str, Enum):
    LOBBY = "lobby"
    IN_PROGRESS = "in_progress"

# Room schema
class RoomSchema(BaseModel):
    room_id: str
    host_id: int
    players: dict[int, PlayerSchema]
    room_state: RoomState
    you: int