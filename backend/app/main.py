from fastapi import FastAPI
from .routers import room, websocket
import uvicorn

# Create app
app = FastAPI()

# Include routers
app.include_router(room.router)
app.include_router(websocket.router)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True, access_log=False)