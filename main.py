#!/usr/bin/python3

import asyncio
import sys

import maze.mazeconfig as mazeconfig
import maze.mazeserver as mazeserver
import maze.mazeprotocol as mazeprotocol

def help():
    print("USAGE: ./main.py -c configuration_file\n\n"
          "minimal configuration file could look like this:\n\n"
          "[interface]\n"
          "event_address = 127.0.0.1\n"
          "event_port = 9090\n"
          "client_address = 127.0.0.1\n"
          "client_port = 9099\n"
          "[system]\n"
          "queue_size = 1048576\n")

def main():
    if not len(sys.argv) == 3:
        help()
        sys.exit(1)

    with open(sys.argv[2], "r") as f:
        conf = mazeconfig.MazeConfig(f.read())

    server = mazeserver.MazeServer(conf)

    loop = asyncio.get_event_loop()

    loop.run_until_complete(loop.create_server(lambda : mazeprotocol.MazeEventProtocol(server),\
                            *conf.event_addr))
    loop.run_until_complete(loop.create_server(lambda : mazeprotocol.MazeClientProtocol(server),\
                            *conf.client_addr))

    loop.run_forever()

if __name__ == '__main__':
    main()
