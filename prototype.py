import asyncio
import sys

client_dict = {}
followers = {}

MAX_Q_SIZE = 2 ** 20

def send_answer(event, client_id):
    if client_id in client_dict:
        client_dict[client_id].add(event)

class EventQ(object):
    def __init__(self):
        self.array = [None] * MAX_Q_SIZE
        self.last_sent = 0
    def add(self, item):
        index = item.seq % MAX_Q_SIZE
        current = self.array[index]
        if current:
            # cannot wait any longer, send current
            current.dispatch()
        self.array[index] = item

        index = (self.last_sent + 1) % MAX_Q_SIZE

        current = self.array[index]
        while current:
            current.dispatch()
            self.array[index] = None
            self.last_sent = (self.last_sent + 1) % MAX_Q_SIZE
            index = (index + 1) % MAX_Q_SIZE
            current = self.array[index]

event_q = EventQ()

class Event(object):
    def __init__(self, seq, type, raw, fr=None, to=None):
        self.seq = int(seq)
        self.type = type
        self.raw = raw + '\n'
        if fr:
            self.fr = fr
        if to:
            self.to = to
    def dispatch(self):
        if self.type == 'B':
            for client in client_dict.values():
                client.add(self)
        elif self.type == 'F':
            if not self.to in followers:
                followers[self.to] = {}
            followers[self.to][self.fr] = True
            send_answer(self, self.to)
        elif self.type == 'U':
            if self.to in followers:
                followers[self.to].pop(self.fr)
                if followers[self.to] == {}:
                    followers.pop(self.to)
        elif self.type == 'P':
            send_answer(self, self.to)
        elif self.type == 'S':
            if self.fr in followers:
                for client_id in followers[self.fr].keys():
                    send_answer(self, client_id)

class EventProtocol(asyncio.Protocol):
    def _parse_payload(self, data):
        sp = data.split('|')
        seq, event_type = sp[0], sp[1]
        if event_type in ['F', 'U', 'P']:
            return Event(seq, event_type, data, sp[2], sp[3])
        elif event_type == 'S':
            return Event(seq, event_type, data, sp[2])
        elif event_type == 'B':
            return Event(seq, event_type, data)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        self.transport = transport

    def data_received(self, data):
        decoded = data.decode('utf-8')
        sp = decoded.split('\n')
        for s in sp:
            if not s == '':
                event = self._parse_payload(s)
                if event:
                    event_q.add(event)

    def connection_lost(self, exc):
        self.transport = None

CLIENT_DISCONNECTED = 0
CLIENT_CONNECTED = 1
CLIENT_INFO_SENT = 2
CLIENT_WAITING = 3

class ClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.state = CLIENT_CONNECTED 

    def data_received(self, data):
        if self.state == CLIENT_CONNECTED:
            decoded = data.decode('utf-8')
            client = decoded.split('\n')[0]
            self.state = CLIENT_WAITING
            self.client = int(client)
            client_dict[client] = self

    def add(self, what):
        self.transport.write(what.raw.encode('utf-8'))

    def connection_lost(self, exc):
        self.state = CLIENT_DISCONNECTED
        self.client = None

loop = asyncio.get_event_loop()

event_server = loop.run_until_complete(loop.create_server(EventProtocol, '127.0.0.1', 9090))
client_server = loop.run_until_complete(loop.create_server(ClientProtocol, '127.0.0.1', 9099))

loop.run_forever()
