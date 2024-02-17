from pydantic import BaseModel

class OtherPlayerSchema(BaseModel):
    player_id: int
    nickname: str
    is_connected: bool
    is_host: bool

class PlayerSchema(BaseModel):
    player_id: int
    nickname: str
    word: str
    is_host: bool
    is_spy: bool
    is_connected: bool

class PlayerIdSchema(BaseModel):
    player_id: int