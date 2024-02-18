from pydantic import BaseModel
from enum import Enum
from .player_schema import PlayerSchema
from .room_schema import RoomSchema
from .game_schema import GameSchema
from typing import TypeAlias

# Game event types
class GameEvent(str, Enum):
    GAME_STATE = "game_state"
    PLAYER_TURN = "player_turn"
    GAME_OVER = "game_over"
    CALL_VOTE = "call_vote"
    VOTE = "vote"
    ASK_QUESTION = "ask_question"
    ANSWER_QUESTION = "answer_question"
    SPY_GUESS = "spy_guess"
    ERROR = "error"

# Room event types
class RoomEvent(str, Enum):
    ROOM_STATE = "room_state"
    PLAYER_CONNECTED = "player_connected"
    PLAYER_DISCONNECTED = "player_disconnected"
    PLAYER_LEFT = "player_left"
    HOST_CHANGED = "host_changed"
    GAME_START = "game_start"
    ERROR = "error"

# Type for data in event schema
ActionTypes : TypeAlias = RoomEvent | GameEvent
EventDataTypes : TypeAlias = PlayerSchema | GameSchema | RoomSchema | int | str

# Event schema
class EventSchema(BaseModel):
    action: ActionTypes
    data: EventDataTypes