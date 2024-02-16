from pydantic import BaseModel
from app.schemas.room_schema import RoomSchema
from app.schemas.player_schema import PlayerSchema, OtherPlayerSchema

# Base action schemas
class ActionSchema(BaseModel):
    action: str
    data: RoomSchema | OtherPlayerSchema