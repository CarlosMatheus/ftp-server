import socket
import os
from utils import TEST_STRING, DEFAULT_ADDRESS, CONNECTION_BYTES, FILE_STRING


class Client:
    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.socket = None

    def send_message(self, message, encoded=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        if not encoded:
            message = message.encode()
        self.socket.sendall(message)
        self.socket.recv(CONNECTION_BYTES)
        self.socket.close()

    def send_test_message(self, message):
        message = TEST_STRING + message
        self.send_message(message)

    def send_file(self, path):
        _, file_name = os.path.split(path)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        with open(path, 'rb') as f:
            self.socket.sendfile(f, 0)
        self.socket.close()
