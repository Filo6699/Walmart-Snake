import socket


class Network:
    def __init__(self, addr) -> None:
        self.addr = addr
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send(self, pocket):
        self.client.sendto(pocket, self.addr)
    
    def listen_loop(self, callback):
        self.client.sendto(b'hello', self.addr)
        while True:
            try:
                rec, addr = self.client.recvfrom(2048)
                callback(rec)
            except ConnectionResetError:
                pass
