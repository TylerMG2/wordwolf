from fastapi import FastAPI
from .schemas import RoomCreate
from .websocket_manager import WebSocketManager
import uuid

# Create app
app = FastAPI()

# Create websocket manager
manager = WebSocketManager()

# Define a route
@app.get("/")
async def get_root():
    return {"message": "Hello World"}

# Create room endpoint
@app.post("/api/rooms/")
async def create_room(room_create: RoomCreate):

    # Generate a room code
    room_code = str(uuid.uuid4())[:6]

    # Check if the name is empty
    if not room_create.name:
        return {"message": "Room name is required"}, 422

    # Return the room code
    return {"code": room_code, "name": room_create.name}