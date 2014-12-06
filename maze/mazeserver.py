# A fitting copyright should be put here.

import maze.mazequeue as mazequeue
import maze.mazeevent as mazeevent

class MazeServer(object):
    def _setup(self, conf):
        self.conf = conf
        self.users = {}
        self.followers = {}
        self.factory = mazeevent.MazeEventFactory()
        self.q = mazequeue.MazeQueue(conf.q_size)

    def __init__(self, conf):
        self._setup(conf)

    def process_events(self, data):
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
        sp = data.splitlines()
        client_id = int(sp[0])
        self.users[client_id] = transport
        return client_id

    def remove_client(self, client_id):
        if client_id in self.users:
            self.users.pop(client_id)

    def reset(self):
        self._setup(self.conf)

