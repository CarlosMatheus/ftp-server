import socket
from utils import DEFAULT_ADDRESS

class Server:

    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(5)
        self.execute_server_listener()

    def execute_server_listener(self):
        while True:
            connection, address = self.server.accept()
            received_byte_list = self.get_byte_list(connection, address)
            string_received = self.decode(received_byte_list)
            command, arg_list = self.unpack(string_received)

    def get_byte_list(self, connection, address):
        received_byte_list = list()
        data = connection.recv(4096)
        while data:
            received_byte_list.append(data)
            data = connection.recv(4096)
        return received_byte_list

    def decode(self, received_byte_list):
        return b''.join(received_byte_list).decode()




