from pydantic import BaseModel
from enum import Enum
from .player_schema import PlayerSchema, PlayerRoleSchema

# Game states
class GameState(str, Enum):
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    VOTING = "voting"
    GAME_OVER = "game_over"

# Game schema
class GameSchema(BaseModel):
    players: list[PlayerSchema]
    game_state: GameState
    player_turn: int
    role: PlayerRoleSchema
