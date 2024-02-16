from pydantic import BaseModel
from app.schemas.player_schema import OtherPlayerSchema

class PlayerJoinSchema(BaseModel):
    action: str = "join"
    player: OtherPlayerSchema