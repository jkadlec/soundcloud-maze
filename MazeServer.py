# A fitting copyright should be put here.

import MazeQueue
import MazeEvent

class MazeServer(object):
    def _setup(self, conf):
        self.conf = conf
        self.users = {}
        self.followers = {}
        self.factory = MazeEvent.MazeEventFactory()
        self.q = MazeQueue.MazeQueue(conf.q_size)

    def __init__(self, conf):
        self._setup(conf)

    def process_events(self, data):
        sp = data.splitlines(True)
        for line in sp:
            ev = self.factory.create_event_from(line)
            if ev:
                self.q.add_and_process(ev, self.followers, self.users)

    def add_client(self, transport, data):
        sp = data.splitlines()
        self.users[int(sp[0])] = transport

    def remove_client(self, client_id):
        self.users.pop(client_id)

    def reset(self):
        self._setup(self.conf)

