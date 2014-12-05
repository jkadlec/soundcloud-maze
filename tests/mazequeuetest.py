#!/usr/bin/python3

# A fitting copyright should be put here.

from maze.mazequeue import *
from maze.mazeevent import * #TODO no-go
import unittest, unittest.mock

Q_SIZE = 8

def create_payload(seq):
    return "".join(str(seq) + "|P|1|" + str(seq) + "\n").encode()

class TestQueue(unittest.TestCase):
    def test_order(self):
        q = MazeQueue(Q_SIZE)

        # create private messages with the same seq as destination, real events are easier TODO for now
        order = [4, 5, 3, 1, 2, 6, 7, 8, 12, 11, 10, 9]
        fc = MazeEventFactory()
        events = [ fc.create_event_from(create_payload(seq)) for seq in order ]
        batch_sizes = [5, 1, 1, 1, 4]
        users = { i:unittest.mock.Mock() for i in range(13) }
        for batch_size in batch_sizes:
            added = []
            for _ in range(batch_size):
                ev = events.pop(0)
                q.add_and_process(ev, None, users)
                added.append(ev.seq)
            # check that whole batch has been called
            for seq in added:
                users[seq].write.assert_called_with(create_payload(seq))

    def test_overfill(self):
        q = MazeQueue(4)
        items = [ unittest.mock.Mock(seq = i) for i in [2, 6] ]
        for i in items:
            q.add_and_process(i, {}, {})

        # test that both items have been dispatched
        for i in items:
            i.dispatch.assert_called()

if __name__ == '__main__':
    unittest.main()
