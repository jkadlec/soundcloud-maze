# A fitting copyright should be put here.

import configparser

class MazeConfig(object):

    """Configuration for Follower Maze server. Uses simple ConfigParser format (INI-like).
       
       Attributes:
           event_addr:   tuple with event listener address and port.
           client_addr:  tuple with client listener address and port.
           q_size:       maximum count of events in internal queue.
    """

    def __init__(self, conf_input):
        parser = configparser.ConfigParser()
        parser.read_string(conf_input)

        interface = parser["interface"]
        self.event_addr = (interface["event_address"], int(interface["event_port"]))
        self.client_addr = (interface["client_address"], int(interface["client_port"]))
        
        system = parser["system"]
        self.q_size = int(system["queue_size"])

