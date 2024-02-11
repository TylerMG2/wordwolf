from fastapi import WebSocket
from typing import Dict, List, Optional

# Manager for websocket connections
class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.rooms: Dict[str, List[WebSocket]] = {}

    # On connect
    async def connect(self, websocket: WebSocket):
        self.connections.append(websocket)

    # On disconnect
    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
        for room in self.rooms.values():
            if websocket in room:
                room.remove(websocket)

    # Create a room
    async def create_room(self, room_code: str, name: str):
        if room_code not in self.rooms:
            self.rooms[room_code] = []
        else:
            raise ValueError("Room already exists")
    
    # Join a room
    async def join_room(self, room_code: str, username: str, websocket: WebSocket):
        if room_code in self.rooms:
            self.rooms[room_code].append(websocket)
            await websocket.send_json({"message": "Joined room"})
        else:
            await websocket.send_json({"message": "Room does not exist"})
