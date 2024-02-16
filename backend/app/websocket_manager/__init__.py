from fastapi import WebSocket
from app.schemas.action_schemas import ActionSchema
import uuid
from .room_manager import Room

# Manager for websocket connections
class WebSocketManager:
    def __init__(self):
        self.connections: dict[WebSocket, str] = {}
        self.rooms: dict[str, Room] = {}

    # On connect
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, username: str):
        
        # Add the connection
        self.connections[websocket] = user_id

        # Check if the room exists
        if room_id not in self.rooms:
            raise Exception("Room does not exist")
        
        # Accept the connection
        await websocket.accept()

        # Else join the room
        room = self.rooms[room_id]
        room.player_join(websocket, user_id, username)

        # Send the room data to the joining player
        game_state = room.to_schema(user_id)
        await room.send_to(ActionSchema(action="game_state", data=game_state), user_id)

        # Broadcast the new player to the room
        player_join = ActionSchema(action="player_join", data=room.players[user_id].to_other_player_schema())
        await room.broadcast_except(player_join, user_id)

    # On disconnect
    def disconnect(self, websocket: WebSocket):
        user_id = self.connections[websocket]

        # Remove the connection
        del self.connections[websocket]

        # Set the user to inactive
        for room in self.rooms.values():
            if user_id in room.players:
                room.players[user_id].active = False

    # Create a room
    async def create_room(self, host: str):

        # Generate a room code
        room_code = str(uuid.uuid4())[:6]
        while room_code in self.rooms:
            room_code = str(uuid.uuid4())[:6]
        room_code = room_code.upper()

        # Create the room
        self.rooms[room_code] = Room(host)
        return room_code
    
    # Leave a room
    async def leave_room(self, websocket: WebSocket, room_code: str):
        user_id = self.connections[websocket]
        room = self.rooms[room_code]
        if room_code in self.rooms:
            del room.players[user_id]
            await websocket.send_json({"message": "Left room"})
            await websocket.close()
        else:
            await websocket.send_json({"message": "Room does not exist"})

        # Notify other players
        player_leave = ActionSchema(action="leave", data={"id": room.players[user_id].id})

        # Broadcast the player leaving
        await room.broadcast_except(player_leave, user_id)
