#!/usr/bin/python3

# A fitting copyright should be put here.

from MazeEvent import *
import unittest

def check_attributes(ev, seq, payload, src = None, dst = None):
    return ev.seq == seq and ev.payload == payload and \
          (not src or ev.src == src) and (not dst or ev.dst == dst)

class TestEvent(unittest.TestCase):
    def test_factory_valid(self):
        factory = MazeEventFactory()
        self.assertTrue(factory)

        # create follow event
        payload = b"123|F|1|2\n"
        ev = factory.create_event_from(payload)
        self.assertTrue(isinstance(ev, FollowEvent))
        self.assertTrue(check_attributes(ev, 123, payload, 1, 2))

        # create unfollow event
        payload = b"124|U|5|6\n"
        ev = factory.create_event_from(payload)
        self.assertTrue(isinstance(ev, UnfollowEvent))
        self.assertTrue(check_attributes(ev, 124, payload, 5, 6))

        # create broadcast event
        payload = b"125|B\n"
        ev = factory.create_event_from(payload)
        self.assertTrue(isinstance(ev, BroadcastEvent))
        self.assertTrue(check_attributes(ev, 125, payload))

        # create private message event
        payload = b"126|P|11|12\n"
        ev = factory.create_event_from(payload)
        self.assertTrue(isinstance(ev, MsgEvent))
        self.assertTrue(check_attributes(ev, 126, payload, dst=12))

        # create status update event
        payload = b"127|S|16\n"
        ev = factory.create_event_from(payload)
        self.assertTrue(isinstance(ev, StatusEvent))
        self.assertTrue(check_attributes(ev, 127, payload, 16))

    def test_factory_invalid(self):
        factory = MazeEventFactory()
        self.assertTrue(factory)

        # no data
        with self.assertRaises(ValueError):
            factory.create_event_from(b"\n")

        # too much data
        with self.assertRaises(ValueError):
            factory.create_event_from(b"1|B|bogus\n")

        # bad seq
        with self.assertRaises(ValueError):
            factory.create_event_from(b"a|B\n")

        # unknown event
        with self.assertRaises(KeyError):
            factory.create_event_from(b"1|X|10|12\n")

    def test_dispatch(self):
        pass

if __name__ == '__main__':
    unittest.main()
