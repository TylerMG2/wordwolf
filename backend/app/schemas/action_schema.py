from pydantic import BaseModel
from app.schemas.room_schema import RoomSchema
from app.schemas.player_schema import PlayerSchema, OtherPlayerSchema, PlayerIdSchema

# Base action schemas
class ActionSchema(BaseModel):
    action: str
    data: RoomSchema | OtherPlayerSchema | PlayerIdSchema