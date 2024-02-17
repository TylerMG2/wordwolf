from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .websocket import manager
from typing import Any
from http import HTTPStatus

router = APIRouter(
    prefix="/api/rooms",
    tags=["rooms"],
    responses={HTTPStatus.NOT_FOUND: {"description": "Not found"}},
)

# Room join/create request schema
class RoomRequest(BaseModel):
    nickname: str

# New room response schema
class RoomResponse(BaseModel):
    room_id: str
    player_id: int
    credentials: str

# Create room endpoint
@router.post("")
async def create_room(room_create: RoomRequest) -> RoomResponse: 

    # Create a room
    room = await manager.create_room()
    print(room.players)

    # Join the room
    player_id, credentials = await room.add_player(room_create.nickname, is_host=True)

    # Return the room code
    return RoomResponse(room_id=room.room_id, player_id=player_id, credentials=credentials)

# Join room endpoint
@router.post("/{room_id}")
async def join_room(room_id: str, room_join: RoomRequest) -> RoomResponse:

    # Check if the room exists
    if room_id not in manager.rooms:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Room not found")
    
    # Join the room
    room, player_id, credentials = await manager.join_room(room_id, room_join.nickname)  

    # Return the room code
    return RoomResponse(room_id=room.room_id, player_id=player_id, credentials=credentials)
