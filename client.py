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
    INVALID, \
    ERROR_NOT_A_DIRECTORY
from hashlib import sha256 as sha
from commander import Commander
from file_manager import FileManager


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
        self.send_file_path = ''
        self.file_manager = FileManager(abs_root_folder=True)
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
        self.data_received = input(self.address[0] + ':' + str(self.address[1]) + ' > ' + self.current_path + '$ ')
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

    def is_error(self, message):
        return message.startswith(INVALID)

    def throw_error(self, message):
        message = message.replace(INVALID, '')
        self.print_invalid_message(message)

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
        if not args_list:
            message = "%s" % (COMMAND_LIST[1])
        else:
            message = "%s %s" % (COMMAND_LIST[1], args_list[0])
        answer = self.send_message(message).decode()
        if self.is_error(answer):
            self.throw_error(answer)
        else:
            lt = answer[1:-1].split(', ')
            for item in lt:
                print(item[1:-1])

    def pwd_command(self, args_list):
        print(self.current_path)

    def mkdir_command(self, args_list):
        if not args_list:
            print('Need to specify directory name')
        else:
            path = args_list[0]
            message = "%s %s" % (COMMAND_LIST[3], path)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                self.throw_error(answer)

    def rmdir_command(self, args_list):
        if not args_list:
            print('Need to specify directory name')
        else:
            path = args_list[0]
            message = "%s %s" % (COMMAND_LIST[4], path)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                self.throw_error(answer)

    def get_command(self, args_list):
        print('todo: implement this')
        pass

    def put_command(self, args_list):
        """
        It is possible to use with 1 or 2 arguments
        with 1 argument -> the single argument passed will be the file name(location) on the client side
        with 2 arguments -> the first first will be the same as with 1 and the second will be the location (the directory) to
                            put on the server side
        :param args_list: list of arguments
        """
        if not args_list:
            self.throw_error('Need to specify file name')
            return

        path_to_local_file, file_name = os.path.split(os.path.join(args_list[0]))
        error, simplified_path = self.file_manager.validate_relative_path(path_to_local_file)

        if error:
            self.throw_error(error)
            return

        # self.send_file_path = simplified_path +
        # _, file_name = path.split(simplified_path)

        if len(args_list) == 2:
            message = "%s %s" % (COMMAND_LIST[1], args_list[1])
            answer = self.send_message(message).decode()
            # print(answer)
            if self.is_error(answer):
                self.throw_error(answer)
                return

            message = "%s %s" % (COMMAND_LIST[1], args_list[1] + file_name)
            server_side_file = args_list[1] + file_name
        else:
            message = "%s %s" % (COMMAND_LIST[1], file_name)
            server_side_file = file_name

        answer = self.send_message(message).decode()
        if self.is_error(answer):
            answer = answer.replace(INVALID, '')
            # print(answer)
            if answer == ERROR_NOT_A_DIRECTORY:
                # problem
                self.throw_error('There already are a file on that directory with that name.')
                ans = ''
                while ans != 'no' and ans != 'yes':
                    ans = input('Do you want to replace the file? (Yes/No)').lower()
                if ans == 'no':
                    return
                else:
                    # Delete the file
                    self.delete_command([server_side_file])
        else:
            self.throw_error('There already are a folder on that directory with that name.')
            ans = ''
            while ans != 'no' and ans != 'yes':
                ans = input('Do you want to replace the folder with the file? (Yes/No)').lower()
            if ans == 'no':
                return
            else:
                # Delete the folder
                self.rmdir_command([server_side_file])

        if len(args_list) == 1:
            message = "%s %s" % (COMMAND_LIST[6], file_name)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                print(1)
                self.throw_error(answer)
        else:
            path = args_list[1] + file_name
            message = "%s %s" % (COMMAND_LIST[6], path)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                self.throw_error(answer)

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
