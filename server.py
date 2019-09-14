from utils import \
    DEFAULT_ADDRESS, \
    READING, \
    TEST_STRING, \
    TESTING, \
    DEFAULT_SEND_BACK_MESSAGE, \
    CONNECTION_BYTES, \
    FILE_STRING, \
    WRITING_FILE, \
    USER_AUTH, \
    CONNECTION_ACCEPTED, \
    CONNECTION_DENIED
import socket
from command_line import CommandLine
from file_manager import FileManager


class Server:

    def __init__(self, address=DEFAULT_ADDRESS):
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(5)
        self.command_line = self.setup_command_line()
        # self.state = WRITING_FILE
        # self.state = TESTING
        self.state = USER_AUTH
        self.data_received = ''
        self.function_switcher = self.setup_function_switcher()
        self.file_manager = FileManager()

        # todo: change this part:
        self.current_folder = ''
        self.file_name = 'ITA_logo.png'

        self.password_hash = 'b7e94be513e96e8c45cd23d162275e5a12ebde9100a425c4ebcdd7fa4dcd897c'

        self.execute_server_listener()

    def server_loop(self):
        while True:
            print('b')
            received_byte_list = self.get_byte_list()
            print('c')
            self.data_received = self.decode(received_byte_list)
            print('d')
            self.update_state()
            print('e')
            self.function_switcher[self.state]()
            print('f')

    def execute_server_listener(self):
        while True:
            print('a')
            self.connection, address = self.server.accept()
            # todo: open thread for new server loop (possibly new object)
            self.server_loop()

    def setup_function_switcher(self):
        return {
            READING: self.read_command,
            TESTING: self.execute_test,
            WRITING_FILE: self.write_file,
            USER_AUTH: self.authenticate_user,
        }

    def authenticate_user(self):
        if self.data_received == self.password_hash:
            self.connection.sendall(CONNECTION_ACCEPTED.encode())
        else:
            self.connection.sendall(CONNECTION_DENIED.encode())

    def write_file(self):
        # (file_name, file_data) = self.data_received.split(FILE_STRING)
        print('writing file: %s' % self.file_name)
        self.file_manager.write_file(self.data_received, self.current_folder, self.file_name)
        # todo: change state
        self.state = TESTING

    def read_command(self):
        command, arg_list = self.unpack(self.data_received)
        self.command_line.execute_command(command, arg_list)

    def execute_test(self):
        message = self.data_received.replace(TEST_STRING, '')
        print(message)

    def update_state(self):
        if self.state == WRITING_FILE:
            return
        if self.data_received.startswith(TEST_STRING): # todo remove this
            self.state = TESTING
        elif self.data_received.startswith(FILE_STRING):
            self.state = WRITING_FILE
        else:
            self.state = USER_AUTH

    def unpack(self, data_received):
        lt = data_received.split(' ')
        return lt[0], lt[1:]

    def get_byte_list(self):
        received_byte_list = list()
        data = self.connection.recv(CONNECTION_BYTES)
        received_byte_list.append(data)
        print(data.decode())
        if self.state == READING:
            self.connection.sendall(DEFAULT_SEND_BACK_MESSAGE.encode())
        return received_byte_list

    def decode(self, received_byte_list):
        if self.state == WRITING_FILE:
            return b''.join(received_byte_list)
        else:
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
