from pydantic import BaseModel

class OtherPlayerSchema(BaseModel):
    player_id: str
    username: str
    active: bool
    is_host: bool

class PlayerSchema(BaseModel):
    player_id: str
    username: str
    active: bool
    word: str
    is_host: bool
    is_spy: bool
    user_id: str

class PlayerIdSchema(BaseModel):
    player_id: str