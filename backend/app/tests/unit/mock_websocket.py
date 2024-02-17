# Class to mock a websocket connection for testing purposes, has a send_json method to send data to the client
class MockWebsocket:
    def __init__(self):
        self.data = None

    async def send_json(self, data):
        self.data = data