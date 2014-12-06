# A fitting copyright should be put here.

class MazeQueue(object):

    """MazeEvent queue class. Represented as an array with modulo indexing.
        Dispatches events that are in correct order upon insertion of any new event.
        Uses sequence numbers for indexing (modulo queue size).

       Attributes:
           size:        queue array size
           last_valid:  seq number of last event that was in correct order
           q:           queue array, fixed size
           modder:      helper modulo indexer
    """

    class ModIndex(object):
        # Helper class, by using it, there's no need to explicitely mod.
        def __init__(self, mod):
            self.mod = mod

        def set(self, val):
            self.val = val % self.mod

        def inc(self):
            self.val = (self.val + 1) % self.mod

    def __init__(self, size):
        """Inits queue with given size.

           Args:
               size:  queue array size
        """
        self.size = size
        self.last_valid = 0
        self.q = [None] * size
        self.modder = self.ModIndex(size)

    def add_and_process(self, item, followers, users):
        """Inserts event into queue.
           Event can be dispatched right away, if not, it will eventually get dispatched
           when all the previous events arrive. if event source does not send
           all previous events, queue *can* get stuck. If an index for incoming event
           is already taken, the older event will be dispatched anyway.

           Args:
               item:  event to add to queue
               followers:  dict with follower relations (needed for dispatching)
               users:      dict with client transports (needed for dispatching)
        """
        mod = self.modder
        mod.set(item.seq)
        current = self.q[mod.val]
        if current:
            # cannot wait any longer
            current.dispatch(followers, users)

        self.q[mod.val] = item

        # try to dispatch all events that are in order
        mod.set(self.last_valid + 1)
        while self.q[mod.val]:
            ev = self.q[mod.val]
            ev.dispatch(followers, users)

            # clear place in queue
            self.q[mod.val] = None

            self.last_valid = ev.seq
            mod.inc()

