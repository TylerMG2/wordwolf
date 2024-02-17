from fastapi import WebSocket, WebSocketException, APIRouter
from ..managers import WebsocketManager

# Manager
manager = WebsocketManager()

router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}}
)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
