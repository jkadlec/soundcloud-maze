#!/usr/bin/python3

# A fitting copyright should be put here.

from maze.mazeprotocol import *
import unittest
import unittest.mock

class TestProtocols(unittest.TestCase):
    def setUp(self):
        self.server = unittest.mock.Mock()
    def test_client_protocol(self):
        proto = MazeClientProtocol(self.server)
        self.assertTrue(proto)
        self.assertEqual(proto.state, CL_STATES.DISCONNECTED)
        self.assertEqual(proto.server, self.server)

        # test incoming connection
        fake_transport = "abcdef"
        proto.connection_made(fake_transport)
        self.assertIs(proto.transport, fake_transport)
        self.assertEqual(proto.state, CL_STATES.CONNECTED)

        # test incoming id
        fake_data = "12345\n"
        proto.data_received(fake_data)
        self.assertEqual(proto.state, CL_STATES.WAITING)
        self.assertTrue(hasattr(proto, "client_id"))
        self.server.add_client.assert_called_with(fake_transport, fake_data)

        # test lost connection
        client_id = proto.client_id
        proto.connection_lost(None)
        self.server.remove_client.assert_called_with(client_id)
        self.assertIsNone(proto.transport)
        self.assertIsNone(proto.client_id)
        self.assertEqual(proto.state, CL_STATES.DISCONNECTED)

        self.server.reset_mock()

    def test_event_protocol(self):
        proto = MazeEventProtocol(self.server)
        self.assertTrue(proto)
        self.assertEqual(proto.server, self.server)

        # test incoming connection
        fake_transport = "abcdef"
        proto.connection_made(fake_transport)
        self.assertIs(proto.transport, fake_transport)

        # test incoming events
        fake_data = "fake events"
        proto.data_received(fake_data)
        self.server.process_events.assert_called_with(fake_data)

        # test lost connection
        proto.connection_lost(None)
        self.assertIsNone(proto.transport)
        self.server.reset.assert_called()
        
if __name__ == '__main__':
    unittest.main()
