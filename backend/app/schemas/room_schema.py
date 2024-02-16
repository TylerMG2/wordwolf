from pydantic import BaseModel
from app.schemas.player_schema import OtherPlayerSchema, PlayerSchema

class RoomCreate(BaseModel):
    nickname: str

class RoomJoinResponse(BaseModel):
    room_id: str
    player_id: int
    credentials: str

class RoomSchema(BaseModel):
    players: dict[str, OtherPlayerSchema]
    game_state: str
    you: PlayerSchema