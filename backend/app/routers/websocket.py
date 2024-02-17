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
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: int, credentials: str):

    # Handle initial connection
    try:

        # Connect to the room
        room, player = await manager.connect_to_room(room_id, player_id, credentials, websocket)

        # Accept the websocket
        await websocket.accept()

        # Send the game state
        await websocket.send_json(ActionSchema(action="game_state", data=room.to_schema(player_id)).model_dump_json())

        while True:
            # Get the action
            data = await websocket.receive_json()

    except WebSocketException as e:
        await websocket.close(code=e.status_code, reason=e.detail)
    except WebSocketDisconnect as e:
        pass
    finally:
        player.disconnect()
        await websocket.close()