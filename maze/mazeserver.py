# A fitting copyright should be put here.

import maze.mazequeue as mazequeue
import maze.mazeevent as mazeevent

class MazeServer(object):

    """A Follower Maze server. Handles incoming events and active users.

       Attributes:
           conf:       server configuration, instance of MazeConfig
           users:      dictionary with active users, values are asyncio transports
           followers:  dictionary with users followers, values are dictionaries with following users.
           factory:    factory used to create MazeEvent objects from payloads.
           q:          queue used for correct order processing and event dispatching.
    """

    def _setup(self, conf):
        self.conf = conf
        self.users = {}
        self.followers = {}
        self.factory = mazeevent.MazeEventFactory()
        self.q = mazequeue.MazeQueue(conf.q_size)

    def __init__(self, conf):
        """Inits server using given configuration, internal structures are created.

           Args:
               conf:  parsed MazeConfig configuration
        """
        self._setup(conf)
    def process_events(self, data):
        """Processes incoming stream of events, stores them into server queue.
           Will also dispatch events from queue if they are in correct order after event addtion.

           Args:
               data:  stream of encoded data, delimited with \n or \r\n.
        """
        sp = data.splitlines(True)
        for line in sp:
            try:
                ev = self.factory.create_event_from(line)
                if ev:
                    self.q.add_and_process(ev, self.followers, self.users)
            except:
                # silently ignore malformed data
                pass

    def add_client(self, transport, data):
        """Adds a new client's transport object into server user dictionary.

           Args:
               transport:  asyncio.transport connected to the client
               data:       data containing user id
        """

        try:
            sp = data.splitlines()
            client_id = int(sp[0])
            self.users[client_id] = transport
            return client_id
        except:
            return None

    def remove_client(self, client_id):
        """Removes a client from server user dictionary.

           Args:
               client_id:  id of client to be removed
        """
        if client_id in self.users:
            self.users.pop(client_id)

    def reset(self):
        """Resets all the server structures.
        """
        self._setup(self.conf)

