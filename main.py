#!/usr/bin/python3

import asyncio
import sys

import MazeConfig
import MazeServer
import MazeProtocol

def main():
    if not len(sys.argv) == 3:
        sys.exit(1)

    with open(sys.argv[2], "r") as f:
        conf = MazeConfig.MazeConfig(f.read())

    server = MazeServer.MazeServer(conf)

    loop = asyncio.get_event_loop()

    loop.run_until_complete(loop.create_server(lambda : MazeProtocol.MazeEventProtocol(server),\
                            *conf.event_addr))
    loop.run_until_complete(loop.create_server(lambda : MazeProtocol.MazeClientProtocol(server),\
                            *conf.client_addr))

    loop.run_forever()

if __name__ == '__main__':
    main()
