#!/usr/bin/python3

# A fitting copyright should be put here.

from MazeServer import *
import MazeEvent
import MazeQueue

import unittest
import unittest.mock

def default_set(server, conf):
    return server and \
           (server.conf is conf) and \
           (server.users == {}) and \
           (server.followers == {}) and \
           isinstance(server.factory, MazeEvent.MazeEventFactory) and \
           isinstance(server.q, MazeQueue.MazeQueue)

class TestServer(unittest.TestCase):
    def setUp(self):
        self.conf = unittest.mock.Mock(q_size = 1024)
        self.server = MazeServer(self.conf)
        self.server.factory = unittest.mock.Mock()
        self.server.q = unittest.mock.Mock()

    def test_init_reset(self):
        conf = unittest.mock.Mock(q_size = 1024)
        server = MazeServer(conf)
        self.assertTrue(default_set(server, conf))

        # overwrite attrs
        server.users, server.followers, server.factory, server.q = range(4)

        # reset server and check again
        server.reset()
        self.assertTrue(default_set(server, conf))

    def test_clients(self):
        fake_transport = "tr"
        fake_data = b"123\n"
        self.server.add_client(fake_transport, fake_data)
        self.assertEqual(self.server.users, {123:fake_transport})

        self.server.remove_client(123)
        self.assertEqual(self.server.users, {})

    def test_events(self):
        # test both unix and windows newlines
        for payload in [b"1|B\n2|B\n3|B\n", b"1|B\r\n2|B\r\n3|B\r\n"]:
            self.server.process_events(payload)
            sp = payload.splitlines(True)
            for ev in sp:
                self.server.factory.create_event_from.assert_any_call(ev)

            # q is tested elsewhere, knowing something was added should be enough here
            self.assertEqual(self.server.q.add_and_process.call_count, 3)
            self.server.q.reset_mock()

if __name__ == '__main__':
    unittest.main()
