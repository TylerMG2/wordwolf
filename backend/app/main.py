from fastapi import FastAPI, WebSocket, Query, HTTPException, Response, status
from app.schemas.room_schema import RoomCreate, RoomJoinResponse
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
    room_id, player_id, credentials = await manager.create_room(room_create.nickname)

    # Return the room code
    return RoomJoinResponse(room_id=room_id, player_id=player_id, credentials=credentials).model_dump_json()

# Join room endpoint
@app.post("/api/rooms/{room_id}")
async def join_room(room_id: str, room_join: RoomCreate, response: Response):
    
        # Check if the room exists
        if room_id not in manager.rooms:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"detail": "Room not found"} 
    
        # Join the room
        player_id, credentials = await manager.join_room(room_id, room_join.nickname)
    
        # Return the room code
        return RoomJoinResponse(room_id=room_id, player_id=player_id, credentials=credentials).model_dump_json()

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
        await manager.disconnect(websocket)