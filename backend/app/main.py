from fastapi import FastAPI, WebSocket
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

    # Generate a unique room code that does not already exist
    room_code = str(uuid.uuid4())[:6]
    while room_code in manager.rooms:
        room_code = str(uuid.uuid4())[:6]
    
    # Create the room
    await manager.create_room(room_code, room_create.name)

    # Return the room code
    return {"code": room_code, "name": room_create.name}

# Websocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            # Wait for data
            data = await websocket.receive_json()

            # Parse the data
            action = data.get("action")
            print(action)

            # Handle the action
            if action == "join":
                room_code = data.get("room_code")
                username = data.get("username")

                # Join the room
                await manager.join_room(room_code, username, websocket)
            elif action == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text("Invalid action")

    except Exception as e:
        print(f"Websocket error: {e}")
    finally:
        manager.disconnect(websocket)