from httpx import AsyncClient
import pytest
from app.main import app

# Test the root route
@pytest.mark.asyncio
async def test_get_root():

    # Use the async client to make a request to the app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    
    # Assert the response status code and content
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}