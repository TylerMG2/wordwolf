from .room_manager import RoomManager
from .player_manager import PlayerManager
from ..schemas import OutgoingActionType, OutgoingActionSchema
from fastapi import WebSocket, WebSocketException
import uuid

# Connection manager class for managing the connections to rooms
class ConnectionManager():

    rooms : dict[str, RoomManager] = {}

    # Create a room
    def create_room(self) -> RoomManager:

        # Generate a unique room code
        room_id = str(uuid.uuid4())[:6]
        while room_id in self.rooms:
            room_id = str(uuid.uuid4())[:6]
        room_id = room_id.upper()

        room = RoomManager(room_id)

        self.rooms[room_id] = room
        return room
    
    # Connect to a room
    async def player_connected(self, room_id: str, player_id: int, credentials: str, websocket: WebSocket) -> tuple[RoomManager, PlayerManager]:

        # Check if the room exists
        if room_id not in self.rooms:
            raise WebSocketException(4001, "Room not found")
        room : RoomManager = self.rooms[room_id]
        
        # Check if the player exists
        if player_id not in room.players:
            raise WebSocketException(4001, "Player not found")
        player : PlayerManager = room.players[player_id]

        # Check if the credentials are correct
        if player.credentials != credentials:
            raise WebSocketException(4001, "Incorrect credentials")
        
        # Attempt to connect
        player.connect(websocket)

        # Send the game state
        await websocket.accept()
        await websocket.send_json(OutgoingActionSchema(action=OutgoingActionType.GAME_STATE, data=room.to_schema(player_id)).model_dump_json())

        # Update all players in the room on the new player
        await room.broadcast_except(OutgoingActionSchema(action=OutgoingActionType.PLAYER_CONNECTED, data=player.to_other_player_schema()), player_id)
        return room, player

    # On player disconnect
    async def player_disconnected(self, room: RoomManager, player: PlayerManager):
            
        # Disconnect the player
        player.disconnect()

        # Update all players in the room on the player leaving
        await room.broadcast_except(OutgoingActionSchema(action=OutgoingActionType.PLAYER_DISCONNECTED, data=player.to_other_player_schema()), player.player_id)

        # If all players are disconnected, delete the room
        if room.all_players_disconnected():
            del self.rooms[room.room_id]

    # On player leave
    async def player_left(self, room: RoomManager, player: PlayerManager):

        # Remove the player from the room
        room.remove_player(player.player_id)

        # Check if the player was the host
        if player.is_host:
            if room.players:

                # Find the next player to be the host
                new_host = None
                for p in room.players.values():
                    if p.is_connected:
                        new_host = p
                        break
                
                # Check if a new host was found
                if new_host:
                    new_host.is_host = True
                    room.host_id = new_host.player_id
                    await room.broadcast(OutgoingActionSchema(action=OutgoingActionType.HOST_CHANGED, data=new_host.to_other_player_schema()))
                else:
                    # Delete the room if no new host was found
                    del self.rooms[room.room_id]
                    await player.websocket.close(code=1000, reason="Room deleted")
                    return

        # Update all players in the room on the player leaving
        await room.broadcast(OutgoingActionSchema(action=OutgoingActionType.PLAYER_LEFT, data=player.to_other_player_schema()))

        # If all players are disconnected, delete the room
        if room.all_players_disconnected():
            del self.rooms[room.room_id]

        # Close player connection
        await player.websocket.close(code=1000, reason="Left Room")