from .room_manager import RoomManager
from .player_manager import PlayerManager
from ..schemas import OutgoingActionSchema, OutgoingActionType

# Game manager class for managing the game logic
class GameManager:

    # Starts the game for a room
    async def start_game(self, room: RoomManager, player: PlayerManager):
        
        # Check if the game has already started
        if room.game_state != "lobby":
            await player.websocket.send_json(OutgoingActionSchema(action=OutgoingActionType.ERROR, data="Game already started").model_dump_json())
            return False

        # Check if the player is the host
        if player.player_id != room.host_id:
            await player.websocket.send_json(OutgoingActionSchema(action=OutgoingActionType.ERROR, data="Only the host can start the game").model_dump_json())
            return False

        # Check if there are enough players
        if len(room.get_connected_players()) < 3:
            await player.websocket.send_json(OutgoingActionSchema(action=OutgoingActionType.ERROR, data="Cannot start game with less than 3 players").model_dump_json())
            return False

        # Start the game
        room.game_state = "in_progress"
        await room.broadcast(OutgoingActionSchema(action=OutgoingActionType.GAME_STARTED, data=""))
        return True
        