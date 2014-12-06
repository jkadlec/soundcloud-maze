# A fitting copyright should be put here.

import abc

def send_payload(dst, users, payload):
    """Helper function. Sends payload to user, if user exists.

       Args:
           users:    dictionary with transports to clients
           payload:  payload to send
    """
    if dst in users:
        users[dst].write(payload)

class MazeEvent(object, metaclass = abc.ABCMeta):

    """An abstract event class.


        Attributes:
            seq:      integer sequence number
            payload:  encoded event payload
    """

    def __init__(self, seq, payload):
        self.seq = seq
        self.payload = payload

    """Processes event, adds/removes new followers and sends payloads to users.

        Args:
            followers:  dictionary with followers, i.e. { id:{id_1:True,id_2:True} }
            users:      dictionary with user transports
    """
    @staticmethod
    def dispatch(self, followers, users):
        raise NotImplementedError

class FollowEvent(MazeEvent):

    """Follow event.

        Attributes:
            seq:      integer sequence number (inherited)
            payload:  encoded event payload (inherited)
            src:      id of user that sent event
            dst:      id of destination user
    """

    def __init__(self, src, dst, **kwargs):
        """Inits a FollowEvent instance.
           
           Args:
              src:       id of user that sent the event
              dst:       id of destination user
              **kwargs:  'seq' and 'payload' arguments for parent constructor
        """
        super().__init__(**kwargs)
        self.src = src
        self.dst = dst

    def dispatch(self, followers, users):
        """Dispatches a FollowEvent instance.
           Adds a source user as a followers of destination user.

           Args:
               followers:  dictionary with follower relations
               users:      dictionary with user transports
        """
        dst = self.dst
        src = self.src
        if not dst in followers:
            followers[dst] = {}
        followers[dst][src] = True

        send_payload(dst, users, self.payload)

class UnfollowEvent(FollowEvent):

    """Unfollow event.

        Attributes:
            seq:      integer sequence number (inherited)
            payload:  encoded event payload (inherited)
            src:      id of user that sent the event (inherited)
            dst:      if of destination user (inherited)
    """

    def dispatch(self, followers, users):
        """Dispatches an UnfollowEvent instance.
           Removes a source user as a followers of destination user.

           Args:
               followers:  dictionary with follower relations
               users:      dictionary with user transports
        """
        dst = self.dst
        src = self.src
        if dst in followers:
            followers[dst].pop(src)
            if followers[dst] == {}:
                followers.pop(dst)

class MessageEvent(MazeEvent):

    """Private message event.

        Attributes:
            seq:      integer sequence number (inherited)
            payload:  encoded event payload (inherited)
            dst:      if of destination user (inherited)
    """

    def __init__(self, src, dst=None, **kwargs):
        """Inits a MessageEvent instance.
           
           Args:
              src:       id of user that sent the event
              dst:       id of destination user, will be ignored, present for unified creation
              **kwargs:  'seq' and 'payload' arguments for parent constructor
        """
        super().__init__(**kwargs)
        # ignore src, not needed for dispatch
        self.dst = dst

    def dispatch(self, followers, users):
        """Dispatches a MessageEvent instance.
           Sends the private message to destination user.

           Args:
               followers:  dictionary with follower relations.
               users:      dictionary with user transports.
        """
        send_payload(self.dst, users, self.payload)

class StatusEvent(MazeEvent):
    
    """Status update message event.

        Attributes:
            seq:      integer sequence number (inherited)
            payload:  encoded event payload (inherited)
            dst:      id of destination user
    """

    def __init__(self, src, **kwargs):
        """Inits a StatusEvent instance.
           
           Args:
              src:       id of user that sent the event
              **kwargs:  'seq' and 'payload' arguments for parent constructor
        """
        super().__init__(**kwargs)
        self.src = src

    def dispatch(self, followers, users):
        """Dispatches a StatusEvent instance.
           Sends the status update message all followers of source user.

           Args:
               followers:  dictionary with follower relations.
               users:      dictionary with user transports.
        """
        src = self.src
        if src in followers:
            for user_id in followers[src].keys():
                send_payload(user_id, users, self.payload)

class BroadcastEvent(MazeEvent):
        
    """Broadcast event.

        Attributes:
            seq:      integer sequence number (inherited)
            payload:  encoded event payload (inherited)
    """

    def dispatch(self, followers, users):
        """Dispatches a BroadcastEvent instance.
           Sends the status broadcast message to connected user clients.

           Args:
               followers:  dictionary with follower relations.
               users:      dictionary with user transports.
        """
        for u in users.values():
            u.write(self.payload)

# mapping between event type chars and classes
EVENT_MAP = {'F':FollowEvent,
             'U':UnfollowEvent,
             'B':BroadcastEvent,
             'P':MessageEvent,
             'S':StatusEvent}

class MazeEventFactory(object):
            
    """Event factory. Creates MazeEvent objects from payloads.

        Attributes:
            parser:     instance of EventParser, used for single event splitting.
            event_map:  event_char:event_class map.
    """

    class EventParser(object):
        # helper class for event splitting
        def __init__(self, delimiter, newlines, encoding):
            self.delimiter = delimiter
            self.encoding = encoding
            self.newlines = newlines
        def get_split_event(self, payload):
            decoded = payload.decode(self.encoding)
            split = decoded.split(self.delimiter)
            # strip line end from the end of last chunk
            split[-1] = split[-1].strip(self.newlines)
            return split

    def __init__(self):
        """Inits a MazeEventFactory instance.
        """
        self.event_map = EVENT_MAP
        self.parser = self.EventParser("|", "\r\n", "utf-8")
    def create_event_from(self, payload):
        """Creates MazeEvent from single encoded payload line, ending with \n or \r\n.

           Args:
               payload:  payload to create event instance from

           Returns:
               created MazeEvent
        """
        parsed = self.parser.get_split_event(payload)
        seq, etype = int(parsed[0]), parsed[1]
        rest = list(map(lambda x: int(x), parsed[2:]))
        return self.event_map[etype](seq=seq, payload=payload, *rest)

