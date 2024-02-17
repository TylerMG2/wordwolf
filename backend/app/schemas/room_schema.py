from pydantic import BaseModel
from .player_schema import OtherPlayerSchema, PlayerSchema

class RoomSchema(BaseModel):
    room_id: str
    host_id: int
    players: dict[int, OtherPlayerSchema]
    game_state: str
    you: PlayerSchema