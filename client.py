import socket
import os
from utils import \
    TEST_STRING, \
    DEFAULT_ADDRESS, \
    CONNECTION_BYTES, \
    FILE_STRING, \
    USER_AUTH, \
    CONNECTION_ACCEPTED, \
    CONNECTION_DENIED, \
    READING
from hashlib import sha256 as sha


class Client:
    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.socket = None
        self.state = USER_AUTH
        self.switch_function = self.initiate_switch_function()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

        self.client_loop()

        self.socket.close()

    def client_loop(self):
        while True:
            self.switch_function[self.state]()

    def initiate_switch_function(self):
        return {
            USER_AUTH: self.authenticate_user,
        }

    def authenticate_user(self):
        user_input = input('Please enter the password:')
        password_hash = sha(user_input.encode()).hexdigest()
        answer = self.send_message(password_hash).decode()
        if answer == CONNECTION_ACCEPTED:
            self.state = READING
            print('win')
        elif answer == CONNECTION_DENIED:
            print('Incorrect password')
        else:
            print('Failed to connect: %s' % answer)

    def send_message(self, message, encoded=False):
        if not encoded:
            message = message.encode()
        self.socket.sendall(message)
        return self.socket.recv(CONNECTION_BYTES)

    def send_test_message(self, message):
        message = TEST_STRING + message
        self.send_message(message)

    def send_file(self, path):
        _, file_name = os.path.split(path)
        with open(path, 'rb') as f:
            self.socket.sendfile(f, 0)
