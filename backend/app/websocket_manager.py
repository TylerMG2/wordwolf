from fastapi import WebSocket
from typing import Dict, List, Optional

# Manager for websocket connections
class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.rooms: Dict[str, List[WebSocket]] = {}

    # On connect
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    # On disconnect
    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
        for room in self.rooms.values():
            if websocket in room:
                room.remove(websocket)
    
    