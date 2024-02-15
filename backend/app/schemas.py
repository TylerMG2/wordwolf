from pydantic import BaseModel

class RoomCreate(BaseModel):
    user_id: str