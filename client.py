import socket


class Client:
    def __init__(self, address=('0.0.0.0', 8080)):
        self.address = address
        self.socket = None
        self.pack_size = 4096

    def send_test_message(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        self.socket.send(b'sending some bytes')
        self.socket.recv(self.pack_size)
        self.socket.close()

