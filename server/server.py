import json
import socket
from random import randint


class Server:
    def __init__(self, addr) -> None:
        self.addr = addr
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(addr)
        self.conns = set()
        self.summon_appol()
    
    def summon_appol(self):
        apol = [randint(0, 9), randint(0, 9)]
        self.apple = apol

        data = json.dumps({"type": "appol", "pos": apol}).encode()
        for a in self.conns:
            self.server.sendto(data, a)
    
    def run(self):
        while True:
            try:
                data, addr = self.server.recvfrom(2048)
                unc1 = data.decode()
                if unc1 == "hello":
                    data = {
                        'type': "appol",
                        'pos': self.apple
                    }
                    self.server.sendto(json.dumps(data).encode(), addr)
                    continue
                uncode = json.loads(unc1)
                if uncode['type'] == 'player_pocket':
                    try:
                        if uncode['pos'] == self.apple:
                            self.summon_appol()
                    except KeyError:
                        pass
                    for a in self.conns:
                        if a == addr:
                            continue
                        self.server.sendto(json.dumps(uncode).encode(), a)
                if uncode['type'] == "death":
                    for a in self.conns:
                        if a == addr:
                            continue
                        self.server.sendto(json.dumps(uncode).encode(), a)
                self.conns.add(addr)
            except (json.JSONDecodeError, ConnectionResetError):
                continue