from pydantic import BaseModel
from app.schemas.player_schema import OtherPlayerSchema

class ActionSchema(BaseModel):
    action: str
    data: dict