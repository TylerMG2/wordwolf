from fastapi import WebSocket
from app.schemas.action_schemas import ActionSchema
from app.schemas.player_schema import PlayerIdSchema
import uuid
from .room_manager import RoomManager, Player

# Manager for websocket connections
class WebSocketManager:
    def __init__(self):
        self.rooms: dict[str, RoomManager] = {}

    # Create a room
    async def create_room(self, nickname: str):

        # Generate a unique room code
        room_id = str(uuid.uuid4())[:6]
        while room_id in self.rooms:
            room_id = str(uuid.uuid4())[:6]
        room_id = room_id.upper()

        # Create the room
        room = RoomManager()
        player_id, credentials = room.add_player(nickname, True)
        self.rooms[room_id] = room

        # Return the room code
        return room_id, player_id, credentials
    
    # Join a room
    async def join_room(self, room_id: str, nickname: str):
                
        # Join the room
        room = self.rooms[room_id]
        player_id, credentials = room.add_player(nickname)
        return player_id, credentials

    

        
