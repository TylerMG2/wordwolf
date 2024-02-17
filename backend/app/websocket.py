# from fastapi import WebSocket, WebSocketException
# from app.schemas import ActionSchema
# from app.managers import Room, Player
# from app.main import app, rooms

# # Websocket route
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str, credentials: str):

#     # Handle initial connection
#     try:

#         await websocket.accept()

#         player_id = int(player_id)

#         # Check if the room exists
#         print("Checking room existence...")
#         if room_id not in rooms: await websocket.close(code=4001, reason="Room not found")
#         room : Room = rooms[room_id]
        
#         # Check if the player exists
#         print("Checking player existence...")
#         if player_id not in room.players: await websocket.close(code=4001, reason="Player not found")
#         player : Player = room.players[player_id]
        
#         # Check if the credentials are correct
#         if player.credentials != credentials: await websocket.close(code=4001, reason="Invalid credentials")

#         # Attempt to connect
#         player.connect(websocket)
#         await websocket.send_json(room.to_schema(player_id).model_dump_json())
    
#         while True:
#             # Get the action
#             data = await websocket.receive_json()
#             action = ActionSchema.model_validate_json(data)

#             # Handle the action
#             if action == "ping":
#                 await websocket.send_text("pong")
#             else:
#                 await websocket.send_text("Invalid action")
#     except Exception as e:
#         pass
#     finally:
#         await player.disconnect()