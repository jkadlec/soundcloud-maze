# A fitting copyright should be put here.

import asyncio

class MazeEventProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
    def connection_made(self, transport):
        self.transport = transport
    def data_received(self, data):
        self.server.process_events(data)
    def connection_lost(self, ex):
        self.transport = None
        self.server.reset()

from enum import Enum

class CL_STATES(Enum):
    DISCONNECTED, CONNECTED, WAITING = range(3)

class MazeClientProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.state = CL_STATES.DISCONNECTED
    def connection_made(self, transport):
        self.transport = transport
        self.state = CL_STATES.CONNECTED
    def data_received(self, data):
        if self.state == CL_STATES.CONNECTED:
            self.client_id = self.server.add_client(self.transport, data)
            self.state = CL_STATES.WAITING
    def connection_lost(self, ex):
        if self.state == CL_STATES.WAITING:
            self.server.remove_client(self.client_id)
        self.transport = None
        self.client_id = None
        self.state = CL_STATES.DISCONNECTED


