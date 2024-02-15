import pytest
from http import HTTPStatus

# Constants
USER_ID = "test_user_id"

# Test room creation
@pytest.mark.asyncio
async def test_create_room(test_client):
    response = await test_client.post("/api/rooms/", json={"user_id": "test_user_id"})

    # Check response
    assert response.status_code == 200
    assert "code" in response.json()

# Test room creation with no user_id
@pytest.mark.asyncio
async def test_create_room_no_user_id(test_client):
    response = await test_client.post("/api/rooms/", json={})

    # Check response
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert any(error["loc"] == ["body", "user_id"] for error in response.json()["detail"])

# Test room creation with no json
@pytest.mark.asyncio
async def test_create_room_no_json(test_client):
    response = await test_client.post("/api/rooms/")

    # Check response
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert any(error["loc"] == ["body"] for error in response.json()["detail"])