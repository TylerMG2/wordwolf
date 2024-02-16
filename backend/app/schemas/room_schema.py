from pydantic import BaseModel
from app.schemas.player_schema import OtherPlayerSchema, PlayerSchema

class RoomCreate(BaseModel):
    user_id: str

class RoomSchema(BaseModel):
    players: list[OtherPlayerSchema]
    game_state: str
    you: PlayerSchema