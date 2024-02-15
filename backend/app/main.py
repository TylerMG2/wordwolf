from fastapi import FastAPI, WebSocket, Query, WebSocketDisconnect
from .schemas import RoomCreate
from .websocket_manager import WebSocketManager

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

    # Create the room
    room_code = await manager.create_room(room_create.user_id)

    # Return the room code
    return {"code": room_code}

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

        await websocket.accept()

        # Connect to the websocket
        result = await manager.connect(websocket, room, user_id, username)

        # If the connection was unsuccessful
        if not result:
            await websocket.close()
            return
    
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