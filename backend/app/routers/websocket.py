from fastapi import WebSocket, WebSocketException, APIRouter, WebSocketDisconnect
from ..managers import ConnectionManager, GameManager
from ..schemas import IncomingActionSchema, IncomingActionType

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

        # Listen for actions
        while True:

            # Get the action
            data = await websocket.receive_json()
            action = IncomingActionSchema.model_validate_json(data)

            # Handle the action
            if action.action == IncomingActionType.LEAVE_ROOM:
                await connection_manager.player_left(room, player)
            elif action.action == IncomingActionType.START_GAME:
                await game_manager.start_game(room, player)

    except WebSocketException as e:
        await websocket.close(code=e.code, reason=e.reason)
    except WebSocketDisconnect as e:
        await websocket.close()
    finally:
        if player is not None:
            await connection_manager.player_disconnected(room, player)