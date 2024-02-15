from fastapi import WebSocket
from typing import Dict, List, Optional
import uuid

class Room:
    def __init__(self, host: str):
        self.host = host
        self.players = []
        self.game_state = "waiting_for_players"

# Manager for websocket connections
class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.rooms: Dict[str, Room] = {}

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
    async def create_room(self, host: str):

        # Generate a room code
        room_code = str(uuid.uuid4())[:6]
        while room_code in self.rooms:
            room_code = str(uuid.uuid4())[:6]

        # Create the room
        self.rooms[room_code] = Room(host)

    # Join a room
    async def join_room(self, room_code: str, username: str, websocket: WebSocket):
        if room_code in self.rooms:
            self.rooms[room_code].append(websocket)
            await websocket.send_json({"message": "Joined room"})
        else:
            await websocket.send_json({"message": "Room does not exist"})
