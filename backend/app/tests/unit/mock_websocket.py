from app.schemas import ActionSchema

# Class to mock a websocket connection for testing purposes, has a send_json method to send data to the client
class MockWebsocket:

    data : list[ActionSchema]
    code : int = None
    reason : str = None

    def __init__(self):
        self.data = []

    async def send_json(self, data):
        self.data.append(ActionSchema.model_validate_json(data))

    async def close(self, code=None, reason=None):
        pass