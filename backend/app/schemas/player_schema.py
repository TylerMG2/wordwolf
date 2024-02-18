from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_id: int
    nickname: str
    is_host: bool
    is_connected: bool

class PlayerRoleSchema(BaseModel):
    is_spy: bool
    word: str