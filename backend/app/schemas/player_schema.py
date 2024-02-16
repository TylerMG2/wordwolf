from pydantic import BaseModel

class OtherPlayerSchema(BaseModel):
    id: str
    username: str
    active: bool
    is_host: bool

class PlayerSchema(BaseModel):
    id: str
    username: str
    active: bool
    word: str
    is_host: bool
    is_spy: bool
    user_id: str