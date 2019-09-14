import socket
import os
from utils import \
    TEST_STRING, \
    DEFAULT_ADDRESS, \
    CONNECTION_BYTES, \
    USER_AUTH, \
    CONNECTION_ACCEPTED, \
    CONNECTION_DENIED, \
    READING, \
    COMMAND_LIST, \
    INVALID
from hashlib import sha256 as sha
from commander import Commander


class Client(Commander):
    def __init__(self, address=DEFAULT_ADDRESS):
        super().__init__()
        self.address = address
        self.socket = None
        self.state = USER_AUTH
        self.switch_function = self.initiate_switch_function()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        self.current_path = '/'
        self.client_loop()

        self.socket.close()

    def client_loop(self):
        while True:
            self.switch_function[self.state]()

    def initiate_switch_function(self):
        return {
            USER_AUTH: self.authenticate_user,
            READING: self.execute_read_command_loop,
        }

    def execute_read_command_loop(self):
        self.data_received = input(self.address[0] + ':' + str(self.address[1]) + ' > ' + self.current_path + '$')
        self.read_command()

    def authenticate_user(self):
        user_input = input('Please enter the password:')
        password_hash = sha(user_input.encode()).hexdigest()
        answer = self.send_message(password_hash).decode()
        if answer == CONNECTION_ACCEPTED:
            self.state = READING
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

    def print_invalid_message(self, message=''):
        if not message:
            print('Error')
        else:
            print('Error: %s' % message)

    def cd_command(self, args_list):
        if not args_list:
            path = ''
        else:
            if args_list[0] == '/':
                path = ''
            else:
                path = args_list[0]

        message = "%s %s" % (COMMAND_LIST[0], path)
        answer = self.send_message(message).decode()
        if answer.startswith(INVALID):
            answer = answer.replace(INVALID, '')
            self.print_invalid_message(answer)
        else:
            if answer == ' ':
                answer = '/'
            self.current_path = answer

    def ls_command(self, args_list):
        print('todo: implement this')
        pass

    def pwd_command(self, args_list):
        print(self.current_path)

    def mkdir_command(self, args_list):
        print('todo: implement this')
        pass

    def rmdir_command(self, args_list):
        print('todo: implement this')
        pass

    def get_command(self, args_list):
        print('todo: implement this')
        pass

    def put_command(self, args_list):
        print('todo: implement this')
        pass

    def delete_command(self, args_list):
        print('todo: implement this')
        pass

    def close_command(self, args_list):
        print('todo: implement this')
        pass

    def open_command(self, args_list):
        print('todo: implement this')
        pass

    def quit_command(self, args_list):
        print('todo: implement this')
        pass

    def unknown_command(self, args_list):
        print('todo: implent this')
        pass
