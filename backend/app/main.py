from fastapi import FastAPI

# Create app
app = FastAPI()

# Define a route
@app.get("/")
async def get_root():
    return {"message": "Hello World"}