# A fitting copyright should be put here.

import asyncio

class MazeEventProtocol(asyncio.Protocol):

    """Protocol class for processing incoming events. No state is stored.

       Attributes:
           server:     server to relay data to
           transport:  connection to event source
    """

    def __init__(self, server):
        """Inits MazeEventProtocol instance.
           
           Args:
               server:  server to relay data to
        """
        self.server = server

    def connection_made(self, transport):
        """Callback method. Called when event source makes a connection.
           Just stores incoming transport object.
           
           Args:
               transport:  transport to communicate with event source.
        """
        self.transport = transport

    def data_received(self, data):
        """Callback method. Called when event source sends data.
           Forwards the data to server.
           
           Args:
               data:  data containing incoming events.
        """
        self.server.process_events(data)

    def connection_lost(self, ex):
        """Callback method. Called when event source disconnects for any reason.
           Resets the server.
           
           Args:
               ex:  exception that caused connection end.
        """
        self.transport = None
        self.server.reset()

from enum import Enum

class CL_STATES(Enum):
    DISCONNECTED, CONNECTED, WAITING = range(3)

class MazeClientProtocol(asyncio.Protocol):

    """Protocol class for handling client connections.

       The protocol has 3 states:
          DISCONNECTED:  client is not connected
          CONNECTED:     client has connected, waiting for user id
          WAITING:       user id sent, waiting for incoming events

       Attributes:
           server:     server to relay client data to
           transport:  connection to client
           client_id:  client interget id
           state:      current protocol state
    """

    def __init__(self, server):
        """Inits MazeClientProtocol instance.
           
           Args:
               server:  server to communicate with
        """
        self.server = server
        self.state = CL_STATES.DISCONNECTED

    def connection_made(self, transport):
        """Callback method. Called when client makes a connection.
           Stores incoming transport object and sets intial state.
           
           Args:
               transport:  transport to communicate with event source.
        """
        self.transport = transport
        self.state = CL_STATES.CONNECTED

    def data_received(self, data):
        """Callback method. Called when client sends data.
           Data should contain client id. Method registers the id with server.
           
           Args:
               data:  data containing client id.
        """
        if self.state == CL_STATES.CONNECTED:
            self.client_id = self.server.add_client(self.transport, data)
            if self.client_id:
                self.state = CL_STATES.WAITING

    def connection_lost(self, ex):
        """Callback method. Called when client disconnects for any reason.
           Removes the client from server.
           
           Args:
               ex:  exception that caused connection end.
        """
        if self.state == CL_STATES.WAITING:
            self.server.remove_client(self.client_id)
        self.transport = None
        self.client_id = None
        self.state = CL_STATES.DISCONNECTED

