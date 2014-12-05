#!/usr/bin/python3

# A fitting copyright should be put here.

from MazeEvent import *
import unittest, unittest.mock

def check_attributes(ev, seq, payload, src = None, dst = None):
    return ev.seq == seq and ev.payload == payload and \
          (not src or ev.src == src) and (not dst or ev.dst == dst)

class TestEvent(unittest.TestCase):
    def setUp(self):
        self.factory = MazeEventFactory()
        self.assertTrue(self.factory)

    def test_factory_valid(self):
        factory = self.factory

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
        factory = self.factory

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
        factory = self.factory

        # create fake follower map
        followers = {}
        # dict with mock users
        users = { i:unittest.mock.Mock() for i in range(16) }

        # test follower addition
        ev = factory.create_event_from(b"1|F|2|1\n")
        ev.dispatch(followers, users)
        ev = factory.create_event_from(b"1|F|3|1\n")
        ev.dispatch(followers, users)

        # TODO: make sure its okay to compare dicts
        self.assertEqual(followers[1], {2:True, 3:True})

        # test status update
        payload = b"1|S|1\n"
        ev = factory.create_event_from(payload)
        ev.dispatch(followers, users)
        for m in [users[2], users[3]]:
            m.send.assert_called_with(payload)
            m.reset_mock()

        # test unsubsribes
        ev = factory.create_event_from(b"1|U|2|1\n")
        ev.dispatch(followers, users)
        self.assertEqual(followers[1], {3:True})
        ev = factory.create_event_from(b"1|U|3|1\n")
        ev.dispatch(followers, users)
        self.assertEqual(followers, {})

        # test broadcast
        payload = b"1|B\n"
        ev = factory.create_event_from(payload)
        ev.dispatch(followers, users)
        for m in users.values():
            m.send.assert_called_with(payload)
            m.reset_mock()

        # test private messages
        payload = b"1|P|1|2\n"
        ev = factory.create_event_from(payload)
        ev.dispatch(followers, users)
        users[2].send.assert_called_with(payload)

        # test that messages to invalid clients are ignored
        payload = b"1|P|1|566\n"
        ev = factory.create_event_from(payload)
        ev.dispatch(followers, users)

if __name__ == '__main__':
    unittest.main()
