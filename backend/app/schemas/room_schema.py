from pydantic import BaseModel
from .player_schema import PlayerSchema
from .game_schema import GameState
from enum import Enum

# Room schema
class RoomSchema(BaseModel):
    room_id: str
    host_id: int
    players: dict[int, PlayerSchema]
    game_state: GameState
    you: int