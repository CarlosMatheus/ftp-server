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
    ERROR_NOT_A_DIRECTORY, \
    ERROR_FILE_ALREADY_EXIST
from hashlib import sha256 as sha
from commander import Commander
from file_manager import FileManager


class Client(Commander):
    def __init__(self):
        super().__init__()
        self.address = ('','')
        self.state = USER_AUTH
        self.switch_function = self.initiate_switch_function()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.connect(self.address)
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
            USER_AUTH: self.execute_read_command_loop,
            READING: self.execute_read_command_loop,
        }

    def execute_read_command_loop(self):
        self.data_received = input(self.address[0] + ':' + str(self.address[1]) + ' > ' + self.current_path + '$ ')
        self.read_command()

    def authenticate_user(self):
        user_input = input('Please enter the password: ')

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
        """
        Will send the entire file using the socket function sendfile
        :param path: the client path to the file (dir+file_name)
        """
        _, file_name = os.path.split(path)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.socket.sendfile(f, 0)
        else:
            self.throw_error('File does not exist: %s' % path)

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
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

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
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

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
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        print(self.current_path)

    def mkdir_command(self, args_list):
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        if not args_list:
            print('Need to specify directory name')
        else:
            path = args_list[0]
            message = "%s %s" % (COMMAND_LIST[3], path)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                self.throw_error(answer)

    def rmdir_command(self, args_list):
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        if not args_list:
            print('Need to specify directory name')
        else:
            path = args_list[0]
            message = "%s %s" % (COMMAND_LIST[4], path)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                self.throw_error(answer)

    def get_file(self) -> "bytes":
        """
        Get files from server
        :return: the data
        """
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        received_byte_list = list()
        self.socket.settimeout(0.2)

        while True:
            try:
                data = self.socket.recv(CONNECTION_BYTES)
                if not data:
                    break
                received_byte_list.append(data)
            except:
                break

        self.socket.settimeout(None)
        return b''.join(received_byte_list)

    def get_command(self, args_list):
        """

        :param args_list:
        :return:
        """
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        if not args_list:
            print('Need to specify the file')
            return

        path = args_list[0]

        server_dir, file_name = os.path.split(path)

        message = "%s %s" % (COMMAND_LIST[5], path)
        answer = self.send_message(message).decode()
        if self.is_error(answer):
            self.throw_error(answer)
            return

        file_data = self.get_file()

        if len(args_list) > 1:
            path = args_list[1]
            error, simplified_abs_path = self.file_manager.validate_relative_path(path)
        else:
            error, simplified_abs_path = self.file_manager.validate_relative_path('')

        if error:
            return self.throw_error(error)

        error = self.file_manager.write_file(simplified_abs_path, file_name, file_data=file_data)

        if error:
            if error == ERROR_FILE_ALREADY_EXIST:
                self.throw_error('There already are a file on that directory with that name.')
                ans = ''
                while ans != 'no' and ans != 'yes':
                    ans = input('Do you want to replace the file? (Yes/No) ').lower()

                if ans == 'no':
                    return
                else:
                    error = self.file_manager.delete_file(simplified_abs_path, file_name)
                    if error:
                        return self.throw_error(error)
                    error = self.file_manager.write_file(simplified_abs_path, file_name, file_data=file_data)
                    if error:
                        return self.throw_error(error)
            else:
                return self.throw_error(error)

    def put_command(self, args_list):
        """
        usage:
            put <{file_directory_on_client}/{file_name_on_client}> [{file_directory_on_server}/]
        Example:
            put ITA_logo.png
            put ITA_logo.png test_folder/
            put folder/ITA_logo.png test_folder/
            put folder/ITA_logo.png

        It is possible to use with 1 or 2 arguments
        with 1 argument -> the single argument passed will be the file name(location) on the client side
        with 2 arguments -> the first first will be the same as with 1 and the second will be the location
                            (the directory) to put on the server side

        :param args_list: list of arguments
        """
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        if not args_list:
            self.throw_error('Need to specify file name')
            return

        path_to_local_file, file_name = os.path.split(os.path.join(args_list[0]))
        error, simplified_path = self.file_manager.validate_relative_path(path_to_local_file)

        if error:
            self.throw_error(error)
            return

        if len(args_list) == 2:

            # Check if the folder where you want to put the file exists
            message = "%s %s" % (COMMAND_LIST[1], args_list[1])
            answer = self.send_message(message).decode()

            if self.is_error(answer):
                self.throw_error(answer)
                return
            ########

            # Check if the file you want to put already exists
            message = "%s %s" % (COMMAND_LIST[1], os.path.join(args_list[1], file_name))
            server_side_file = os.path.join(args_list[1], file_name)
        else:
            # Check if the file you want to put already exists
            message = "%s %s" % (COMMAND_LIST[1], file_name)
            server_side_file = file_name

        answer = self.send_message(message).decode()
        # It is expected the answer to be an error,
        # but if it is "not a directory" means that the file already exists
        if self.is_error(answer):
            answer = answer.replace(INVALID, '')
            if answer == ERROR_NOT_A_DIRECTORY:
                self.throw_error('There already are a file on that directory with that name.')
                ans = ''
                while ans != 'no' and ans != 'yes':
                    ans = input('Do you want to replace the file? (Yes/No) ').lower()
                if ans == 'no':
                    return
                else:
                    self.delete_command([server_side_file])
        else:
            self.throw_error('There already are a folder on that directory with that name.')
            ans = ''
            while ans != 'no' and ans != 'yes':
                ans = input('Do you want to replace the folder with the file? (Yes/No) ').lower()
            if ans == 'no':
                return
            else:
                self.rmdir_command([server_side_file])

        if len(args_list) == 1:
            path = file_name
        else:
            path = os.path.join(args_list[1], file_name)

        message = "%s %s" % (COMMAND_LIST[6], path)
        answer = self.send_message(message).decode()

        if self.is_error(answer):
            self.throw_error(answer)
        else:
            self.send_file(os.path.join(simplified_path, file_name))

    def delete_command(self, args_list):
        if self.is_not_authenticated():
            return self.throw_not_auth_error()
        if not args_list:
            print('Need to specify the file name')
        else:
            path = args_list[0]
            message = "%s %s" % (COMMAND_LIST[7], path)
            answer = self.send_message(message).decode()
            if self.is_error(answer):
                self.throw_error(answer)

    def close_command(self, args_list):
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        self.socket.close()
        print('todo: implement this')

    def open_command(self, args_list):
        if not args_list:
            return self.throw_error('Need to specify the server. Example: open 0.0.0.0:8080')
        if len(args_list) > 1:
            return self.throw_error('Too many arguments')

        address = args_list[0].split(':')
        if len(address) < 2:
            return self.throw_error('Wrong address format')

        try:
            address = (address[0], int(address[1]))
            self.socket.connect(address)
        except Exception as err:
            self.throw_error('Connection failed %s' % err)
            return

        self.authenticate_user()
        if self.state == READING:
            self.address = address

    def quit_command(self, args_list):
        if self.is_not_authenticated():
            return self.throw_not_auth_error()

        self.close_command(args_list)
        exit()

    def unknown_command(self, args_list):
        print('Unknown command')

    def empty_command(self, args_list):
        pass

    def is_not_authenticated(self):
        return self.state == USER_AUTH

    def throw_not_auth_error(self):
        self.throw_error("You need to connect to a server first, use the 'open' command")
