from fastapi import WebSocket, WebSocketException, APIRouter, WebSocketDisconnect
from ..managers import ConnectionManager, GameManager
from ..schemas import EventSchema, RoomEvent, GameEvent

# Managers
connection_manager = ConnectionManager()
game_manager = GameManager()

router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}}
)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str, credentials: str):

    room, player = None, None

    # Handle initial connection
    try:

        # Check if player_id is an integer
        if not player_id.isdigit():
            raise WebSocketException(4001, "Invalid player_id")
        player_id = int(player_id)

        # Connect to the room and send the game state
        room, player = await connection_manager.player_connected(room_id, player_id, credentials, websocket)

        # Listen for player events
        while True:

            # Get the event
            data = await websocket.receive_json()
            action = EventSchema.model_validate_json(data)

            # Handle the action
            if action.action == RoomEvent.PLAYER_LEFT:
                await connection_manager.player_left(room, player)
            elif action.action == RoomEvent.GAME_START:
                await game_manager.start_game(room, player)

    except WebSocketException as e:
        await websocket.close(code=e.code, reason=e.reason)
    except WebSocketDisconnect as e:
        await websocket.close()
    finally:
        if player is not None:
            await connection_manager.player_disconnected(room, player)