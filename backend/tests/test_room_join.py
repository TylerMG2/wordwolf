import pytest
import pytest_asyncio
from app.schemas.room_schema import RoomJoinResponse
from app.schemas.room_schema import RoomJoinResponse
from httpx import AsyncClient

@pytest.mark.asyncio
class TestRoomJoin:

    NICKNAME = "Test User"
    room_info : RoomJoinResponse = None

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, create_room):
        self.room_info = await create_room(self.NICKNAME)

    # Test joining the room
    async def test_join_room(self, test_client : AsyncClient):
        response = await test_client.post(f"/api/rooms/{self.room_info.room_id}", json={"nickname": self.NICKNAME})

        # Convert response to room join response
        room_info = RoomJoinResponse.model_validate_json(response.json())

        # Check response
        assert response.status_code == 200
        assert room_info.room_id == self.room_info.room_id
    
    # Test joining the room with no nickname
    async def test_join_room_no_nickname(self, test_client : AsyncClient):
        response = await test_client.post(f"/api/rooms/{self.room_info.room_id}", json={})

        # Check response
        assert response.status_code == 422
        assert any(error["loc"] == ["body", "nickname"] for error in response.json()["detail"])
    
    # Test joining a room that does not exist
    async def test_join_room_no_room(self, test_client : AsyncClient):
        response = await test_client.post(f"/api/rooms/invalid_room", json={"nickname": "test"})

        # Check response
        assert response.status_code == 404
        assert response.json() == {"detail": "Room not found"}


