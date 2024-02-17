from .room_manager import RoomManager
from .player_manager import PlayerManager
from fastapi import WebSocket, WebSocketException
import uuid

class WebsocketManager():

    rooms : dict[str, RoomManager] = {}

    # Create a room
    async def create_room(self) -> RoomManager:

        # Generate a unique room code
        room_id = str(uuid.uuid4())[:6]
        while room_id in self.rooms:
            room_id = str(uuid.uuid4())[:6]
        room_id = room_id.upper()

        room = RoomManager(room_id)
        
        self.rooms[room_id] = room
        return room

    # Join a room
    async def join_room(self, room_id: str, username: str) -> tuple[RoomManager, int, str]:

        # Join the room
        room = self.rooms[room_id]
        player_id, credentials = await room.add_player(username)
        return room, player_id, credentials
    
    # Connect to a room
    async def connect_to_room(self, room_id: str, player_id: int, credentials: str, websocket: WebSocket) -> tuple[RoomManager, PlayerManager]:

        # Check if the room exists
        if room_id not in self.rooms:
            raise WebSocketException(status_code=4001, detail="Room not found")
        room : RoomManager = self.rooms[room_id]
        
        # Check if the player exists
        if player_id not in room.players:
            raise WebSocketException(status_code=4001, detail="Player not found")
        player : PlayerManager = room.players[player_id]

        # Check if the credentials are correct
        if player.credentials != credentials:
            return WebSocketException(status_code=4001, detail="Invalid credentials")
        
        # Attempt to connect
        player.connect(websocket)
        return room, player