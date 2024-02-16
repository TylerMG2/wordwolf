from fastapi import FastAPI, WebSocket, Query, HTTPException, Response
from app.schemas.room_schema import RoomCreate
from app.schemas.action_schemas import ActionSchema
from app.websocket_manager import WebSocketManager
import os

print(os.getenv('ENV'))

# Create app
app = FastAPI()

# Create websocket manager
manager = WebSocketManager()

# Create room endpoint
@app.post("/api/rooms/")
async def create_room(room_create: RoomCreate): 

    # Create the room
    room_code = await manager.create_room(room_create.user_id)

    # Return the room code
    return {"code": room_code}

# Room info endpoint
@app.get("/api/rooms/{room_code}")
async def room_info(room_code: str, user_id: str = Query(None)):

    # Check if we are in testing
    if os.getenv('ENV') != "TEST":
        return HTTPException(status_code=404, detail="Not found")

    return manager.rooms[room_code].to_schema(user_id)

# Websocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, room: str = Query(None), user_id: str = Query(None), username: str = "No name"):

    # Handle initial connection
    try:

        # Check if the user_id is provided
        if user_id is None:
            await websocket.close(code=4001, reason="User ID not provided")
            return

        # Check if the room is provided
        if room is None:
            await websocket.close(code=4001, reason="Room code not provided")
            return

        # Attempt to connect
        try: 
            await manager.connect(websocket, room, user_id, username)
        except Exception as e:
            await websocket.close(code=4001, reason=str(e))
            return        
    
        while True:
            # Get the action
            data = await websocket.receive_json()
            action = ActionSchema.model_validate_json(data)

            # Handle the action
            if action == "leave":
                await manager.leave_room(websocket, room)
            elif action == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text("Invalid action")
    except Exception as e:
        pass
    finally:
        manager.disconnect(websocket)