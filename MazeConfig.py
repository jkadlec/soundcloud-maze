# A fitting copyright should be put here.

import configparser

class MazeConfig(object):

    """Configuration for Follower Maze server. Uses simple ConfigParser format.
       
       Attributes:
           event_addr:     tuple with event listener address and port.
           client_addr:    tuple with client listener address and port.
           control_sock:   path to server control unix socket.
           map_path:       path to pickled follower dict.
           q_size:         maximum count of events in internal queue.
           workers:        number of answering processes.
           sink:           logging sink.
           verbosity:      server logging verbosity.
    """

    def __init__(self, conf_input):
        parser = configparser.ConfigParser()
        parser.read_string(conf_input)

        interface = parser["interface"]
        self.event_addr = (interface["event_address"], int(interface["event_port"]))
        self.client_addr = (interface["client_address"], int(interface["client_port"]))
        
        system = parser["system"]
        self.daemonize = system["daemonize"] == "yes"
        self.backlog_size = int(system["backlog_size"])
        self.q_size = int(system["max_queue_size"])
        self.workers = int(system["workers"])
        self.control_sock = system["control_socket"]

        log = parser["log"]
        self.verbosity = int(log["verbosity"])
        self.sink = log["sink"]

