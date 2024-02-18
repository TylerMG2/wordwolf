from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .websocket import connection_manager
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
    room = connection_manager.create_room()

    # Join the room
    player = room.add_player(room_create.nickname, is_host=True)

    # Return the room code
    return RoomResponse(room_id=room.room_id, player_id=player.player_id, credentials=player.credentials)

# Join room endpoint
@router.post("/{room_id}")
async def join_room(room_id: str, room_join: RoomRequest) -> RoomResponse:

    # Check if the room exists
    if room_id not in connection_manager.rooms:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Room not found")
    room = connection_manager.rooms[room_id]
    
    # Join the room
    player = room.add_player(room_join.nickname) 

    # Return the room code
    return RoomResponse(room_id=room.room_id, player_id=player.player_id, credentials=player.credentials)
