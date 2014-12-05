#!/usr/bin/python3

# A fitting copyright should be put here.

from maze.mazequeue import *
import unittest, unittest.mock

Q_SIZE = 8

def create_dispatch(seq_nr, dispatched):
    return lambda x, y: dispatched.append(seq_nr)

class TestQueue(unittest.TestCase):
    def test_order(self):
        q = MazeQueue(Q_SIZE)

        order = [4, 5, 3, 1, 2, 6, 7, 8, 12, 11, 10, 9]
        batch_sizes = [5, 1, 1, 1, 4]

        dispatched = []
        events = [ unittest.mock.Mock(\
                   seq = seq_nr,\
                   dispatch = create_dispatch(seq_nr, dispatched)) for seq_nr in order ]
        for batch_size in batch_sizes:
            dispatched.clear()
            for _ in range(batch_size):
                ev = events.pop(0)
                q.add_and_process(ev, None, None)
            # check that whole batch has been dispatched
            self.assertEqual(len(dispatched), batch_size)
            # check that the order was correct
            self.assertEqual(dispatched, sorted(dispatched))

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
