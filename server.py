import socket
from utils import DEFAULT_ADDRESS
from command_line import CommandLine


class Server:

    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(5)
        self.execute_server_listener()
        self.command_line = self.setup_command_line()
        self.reading_command = True

    def execute_server_listener(self):
        while True:
            connection, address = self.server.accept()
            received_byte_list = self.get_byte_list(connection, address)
            data_received = self.decode(received_byte_list)
            if self.reading_command:
                command, arg_list = self.unpack(data_received)
                self.command_line.execute_command(command, arg_list)

    def unpack(self, data_received):
        lt = data_received.split(' ')
        return lt[0], lt[1:]

    def get_byte_list(self, connection, address):
        received_byte_list = list()
        data = connection.recv(4096)
        while data:
            received_byte_list.append(data)
            data = connection.recv(4096)
        return received_byte_list

    def decode(self, received_byte_list):
        return b''.join(received_byte_list).decode()

    def setup_command_line(self):
        method_list = [
            self.cd_command,
            self.ls_command,
            self.pwd_command,
            self.mkdir_command,
            self.rmdir_command,
            self.get_command,
            self.put_command,
            self.delete_command,
            self.close_command,
            self.open_command,
            self.quit_command,
        ]
        return CommandLine(method_list)

    def cd_command(self, args_list):
        pass

    def ls_command(self, args_list):
        pass

    def pwd_command(self, args_list):
        pass

    def mkdir_command(self, args_list):
        pass

    def rmdir_command(self, args_list):
        pass

    def get_command(self, args_list):
        pass

    def put_command(self, args_list):
        pass

    def delete_command(self, args_list):
        pass

    def close_command(self, args_list):
        pass

    def open_command(self, args_list):
        pass

    def quit_command(self, args_list):
        pass
