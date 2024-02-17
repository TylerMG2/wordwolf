from fastapi import WebSocket, WebSocketException, APIRouter, WebSocketDisconnect
from ..managers import WebsocketManager
from ..schemas import ActionSchema

# Manager
manager = WebsocketManager()

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
        room, player = await manager.connect_to_room(room_id, player_id, credentials, websocket)
        await websocket.accept()

        # Send the game state to the player
        await websocket.send_json(ActionSchema(action="game_state", data=room.to_schema(player_id)).model_dump_json())

        # Listen for actions
        while True:

            # Get the action
            data = await websocket.receive_json()
            action = ActionSchema.model_validate_json(data)

            # Handle the action

    except WebSocketException as e:
        await websocket.close(code=e.code, reason=e.reason)
    except WebSocketDisconnect as e:
        await websocket.close()
    finally:
        if player is not None:
            player.disconnect()