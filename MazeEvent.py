# A fitting copyright should be put here.

import abc

def send_payload(dst, users, payload):
    if dst in users:
        users[dst].send(payload)

class MazeEvent(object, metaclass = abc.ABCMeta):
    def __init__(self, seq, payload):
        self.seq = seq
        self.payload = payload

    @staticmethod
    def dispatch(self, followers, users):
        pass

class FollowEvent(MazeEvent):
    def __init__(self, src, dst, **kwargs):
        super().__init__(**kwargs)
        self.src = src
        self.dst = dst

    def dispatch(self, followers, users):
        dst = self.dst
        src = self.src
        if not dst in followers:
            followers[dst] = {}
        followers[dst][src] = True

        send_payload(dst, users, self.payload)

class UnfollowEvent(FollowEvent):
    def dispatch(self, followers, users):
        dst = self.dst
        src = self.src
        if dst in followers:
            followers[dst].pop(src)
            if followers[dst] == {}:
                followers.pop(dst)

class MsgEvent(MazeEvent):
    def __init__(self, src, dst, **kwargs):
        super().__init__(**kwargs)
        self.dst = dst

    def dispatch(self, followers, users):
        send_payload(self.dst, users, self.payload)

class StatusEvent(MazeEvent):
    def __init__(self, src, **kwargs):
        super().__init__(**kwargs)
        self.src = src

    def dispatch(self, followers, users):
        src = self.src
        if src in followers:
            for user_id in followers[src].keys():
                send_payload(user_id, self.payload)

class BroadcastEvent(MazeEvent):
    def dispatch(self, followers, users):
        for u in users:
            u.send(self.payload)

EVENT_MAP = {'F':FollowEvent,
             'U':UnfollowEvent,
             'B':BroadcastEvent,
             'P':MsgEvent,
             'S':StatusEvent}

class MazeEventFactory(object):
    class EventParser(object):
        def __init__(self, delimiter, newline, encoding):
            self.delimiter = delimiter
            self.encoding = encoding
            self.nlsize = len(newline)
        def get_split_event(self, payload):
            decoded = payload.decode(self.encoding)
            split = decoded.split(self.delimiter)
            # strip line end from the end of last chunk TODO: only works for same newline lenghts
            split[-1] = split[-1][:-self.nlsize]
            return split

    def __init__(self):
        self.event_map = EVENT_MAP
        self.parser = self.EventParser("|", "\n", "utf-8")
    def create_event_from(self, payload):
        parsed = self.parser.get_split_event(payload)
        seq, etype = int(parsed[0]), parsed[1]
        rest = list(map(lambda x: int(x), parsed[2:]))
        return self.event_map[etype](seq=seq, payload=payload, *rest)


