#!/usr/bin/python3

# A fitting copyright should be put here.

from MazeConfig import *
import unittest

MOCK_INPUT = "\
[interface]\n\
event_address = 1.2.3.4\n\
event_port = 9090\n\
client_address = 5.6.7.8\n\
client_port = 9099\n\
\
[system]\n\
daemonize = yes\n\
backlog_size = 1024\n\
max_queue_size = 65536\n\
control_socket = control.sock\n\
workers = 4\n\
\
[log]\n\
verbosity = 1\n\
sink = syslog\n\
"

EXPECTED = { "event_addr":('1.2.3.4', 9090), \
             "client_addr":('5.6.7.8', 9099), \
             "daemonize":True, \
             "backlog_size":1024, \
             "q_size":65536, \
             "control_sock":"control.sock", \
             "workers":4, \
             "sink":"syslog", \
             "verbosity":1, \
             "map_path":None}

class TestConfig(unittest.TestCase):
    def test_parse(self):
        conf = MazeConfig(MOCK_INPUT)
        self.assertTrue(conf)

        # get class fields
        fields = list(filter(lambda x: not x[:2] == "__", dir(conf)))
        for f in fields:
            self.assertEqual(EXPECTED[f], getattr(conf, f))

if __name__ == '__main__':
    unittest.main()
