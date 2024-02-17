from app.schemas import OutgoingActionSchema

# Class to mock a websocket connection for testing purposes, has a send_json method to send data to the client
class MockWebsocket:

    data : list[OutgoingActionSchema]
    code : int = None
    reason : str = None

    def __init__(self):
        self.data = []

    async def send_json(self, data):
        self.data.append(OutgoingActionSchema.model_validate_json(data))

    async def close(self, code=None, reason=None):
        self.code = code
        self.reason = reason

    async def accept(self):
        pass