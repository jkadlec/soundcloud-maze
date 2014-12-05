# A fitting copyright should be put here.

class MazeQueue(object):
    class ModIndex(object):
        def __init__(self, mod, val):
            self.mod = mod
            self.val = val % mod

        def inc(self):
            self.val = (self.val + 1) % self.mod

    def __init__(self, max_size):
        self.max_size = max_size # TODO: change to next power of 2
        self.last_valid = 0
        self.q = [None] * max_size

    def add_and_process(self, item, followers, users):
        # TODO not pretty
        index = MazeQueue.ModIndex(self.max_size, item.seq)
        current = self.q[index.val]
        if current:
            # cannot wait any longer
            current.dispatch(followers, users)

        self.q[index.val] = item

        # try to dispatch all events that are in order
        index = MazeQueue.ModIndex(self.max_size, self.last_valid + 1)
        while self.q[index.val]:
            ev = self.q[index.val]
            ev.dispatch(followers, users)
            self.q[index.val] = None
            self.last_valid = ev.seq
            index.inc()

