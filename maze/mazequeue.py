# A fitting copyright should be put here.

class ModIndex(object):
        def __init__(self, mod):
            self.mod = mod

        def set(self, val):
            self.val = val % self.mod

        def inc(self):
            self.val = (self.val + 1) % self.mod

class MazeQueue(object):
    def __init__(self, max_size):
        self.max_size = max_size
        self.last_valid = 0
        self.q = [None] * max_size
        self.modder = ModIndex(max_size)

    def add_and_process(self, item, followers, users):
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

