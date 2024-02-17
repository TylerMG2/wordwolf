from fastapi import FastAPI, HTTPException
from app.schemas import RoomCreate, RoomJoinResponse
from app.websocket_manager import Room
import uuid
import uvicorn

# Create app
app = FastAPI()

# Store rooms
rooms : dict[str, Room] = {}

# Create room endpoint
@app.post("/api/rooms/")
async def create_room(room_create: RoomCreate): 

    # Generate a unique room code
    room_id = str(uuid.uuid4())[:6]
    while room_id in rooms:
        room_id = str(uuid.uuid4())[:6]
    room_id = room_id.upper()

    # Create the room
    room = Room(room_id)
    player_id, credentials = await room.add_player(room_create.nickname, True)
    rooms[room_id] = room
    print(rooms, room_id, player_id, credentials)

    # Return the room code
    return RoomJoinResponse(room_id=room_id, player_id=player_id, credentials=credentials).model_dump_json()

# Join room endpoint
@app.post("/api/rooms/{room_id}")
async def join_room(room_id: str, room_join: RoomCreate):
    
    # Check if the room exists
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    # Join the room
    room = rooms[room_id]
    player_id, credentials = await room.add_player(room_join.nickname)

    # Return the room code
    return RoomJoinResponse(room_id=room_id, player_id=player_id, credentials=credentials).model_dump_json()

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True, access_log=False)