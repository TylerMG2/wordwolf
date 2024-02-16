import pytest
from http import HTTPStatus
from app.schemas.room_schema import RoomJoinResponse
from httpx import AsyncClient

@pytest.mark.asyncio
class TestRoomCreate:

    NICKNAME = "Test User"
    
    # Test room creation
    async def test_create_room(self, test_client: AsyncClient):
        response = await test_client.post("/api/rooms/", json={"nickname": self.NICKNAME})
        assert RoomJoinResponse.model_validate_json(response.json())

        # Check response
        assert response.status_code == 200
    
    # Test room creation with no user_id
    async def test_create_room_no_user_id(self, test_client: AsyncClient):
        response = await test_client.post("/api/rooms/", json={})

        # Check response
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert any(error["loc"] == ["body", "nickname"] for error in response.json()["detail"])

    # Test room creation with no json
    async def test_create_room_no_json(self, test_client: AsyncClient):
        response = await test_client.post("/api/rooms/")

        # Check response
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert any(error["loc"] == ["body"] for error in response.json()["detail"])