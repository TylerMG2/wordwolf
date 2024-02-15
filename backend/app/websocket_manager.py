from fastapi import WebSocket
import uuid

# Player class
class Player:
    def __init__(self, username: str, is_host: bool):
        self.username = username
        self.active = True
        self.is_host = is_host
        self.is_spy = False
    
    # Convert to dictionary
    def to_dict(self):
        return {
            "username": self.username,
            "active": self.active,
            "is_host": self.is_host,
            "is_spy": self.is_spy
        }

# Room class
class Room:
    def __init__(self, host: str):
        self.host: str = host
        self.players: dict[str, Player] = {}
        self.game_state: str = "waiting_for_players"

    # Convert to dictionary
    def to_dict(self):
        return {
            "players": {key: player.to_dict() for key, player in self.players.items()},
            "game_state": self.game_state
        }

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
        is_host = room.host == user_id
        
        # Check if the player is already in the room
        if user_id in room.players:
            room.players[user_id].active = True
        else:
            # Add the player to the room
            room.players[user_id] = Player(username, is_host)

        # Send the room data
        response = room.to_dict()
        response["is_host"] = is_host
        await websocket.send_json(response)

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

        # Create the room
        self.rooms[room_code] = Room(host)
        return room_code

    # Join a room
    async def join_room(self, room_code: str, username: str, websocket: WebSocket):
        if room_code in self.rooms:
            self.rooms[room_code].append(websocket)
            await websocket.send_json({"message": "Joined room"})
        else:
            await websocket.send_json({"message": "Room does not exist"})
