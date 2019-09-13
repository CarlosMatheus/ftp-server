import socket
from utils import DEFAULT_ADDRESS, READING, TEST_STRING, TESTING, DEFAULT_SEND_BACK_MESSAGE
from command_line import CommandLine


class Server:

    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(5)
        self.command_line = self.setup_command_line()
        self.state = READING
        self.data_received = ''
        self.function_switcher = self.setup_function_switcher()

        self.execute_server_listener()

    def execute_server_listener(self):
        while True:
            connection, address = self.server.accept()
            received_byte_list = self.get_byte_list(connection)
            data_received = self.decode(received_byte_list)
            self.update_state(data_received)
            self.function_switcher[self.state]()

    def setup_function_switcher(self):
        return {
            READING: self.read_command,
            TESTING: self.execute_test,
        }

    def read_command(self):
        command, arg_list = self.unpack(self.data_received)
        self.command_line.execute_command(command, arg_list)

    def execute_test(self):
        message = self.data_received.replace(TEST_STRING, '')
        print(message)

    def update_state(self, data_received):
        if data_received.startswith(TEST_STRING):
            self.state = TESTING
        else:
            self.state = READING
        self.data_received = data_received

    def unpack(self, data_received):
        lt = data_received.split(' ')
        return lt[0], lt[1:]

    def get_byte_list(self, connection):
        received_byte_list = list()
        while True:
            data = connection.recv(4096)
            if not data:
                break
            received_byte_list.append(data)
            connection.send(DEFAULT_SEND_BACK_MESSAGE.encode())
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
