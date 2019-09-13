import socket
from utils import TEST_STRING, DEFAULT_ADDRESS


class Client:
    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.socket = None
        self.pack_size = 4096

    def send_test_message(self, message):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        message = TEST_STRING + message
        self.socket.send(message.encode())
        self.socket.recv(self.pack_size)
        self.socket.close()
