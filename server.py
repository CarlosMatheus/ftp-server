from utils import \
    READING, \
    TEST_STRING, \
    TESTING, \
    CONNECTION_BYTES, \
    FILE_STRING, \
    WRITING_FILE, \
    USER_AUTH, \
    CONNECTION_ACCEPTED, \
    CONNECTION_DENIED, \
    INVALID, \
    server_log
import socket
from file_manager import FileManager
from commander import Commander
from os import path
from _thread import start_new_thread


class Server(Commander):

    def __init__(self, connection=None, address=None):
        super().__init__()

        self.connection = connection
        self.address = address

        self.data_received = ''
        self.function_switcher = self.setup_function_switcher()
        self.file_manager = FileManager()

        self.simplified_abs_path = ''
        self.item_name = ''
        self.state = USER_AUTH

        self.password_hash = 'b7e94be513e96e8c45cd23d162275e5a12ebde9100a425c4ebcdd7fa4dcd897c'

        if connection is None:
            self.address = ('0.0.0.0', int(input('Which port to open the server? ')))
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
            self.server.listen(5)
            self.execute_server_listener()
        else:
            self.server_loop()

    def server_loop(self):
        print('Waiting for user authentication')
        self.state = USER_AUTH
        while True:
            server_log('Awaiting message')
            received_byte_list = self.get_byte_list()
            server_log('Decoding received message')
            self.data_received = self.decode(received_byte_list)
            if not self.data_received:
                server_log('Connection lost')
                return
            server_log('Executing message')
            self.function_switcher[self.state]()
            server_log('Concluded')

    def execute_server_listener(self):
        print('Waiting for connections')
        while True:
            connection, address = self.server.accept()
            server_log('Connection %s established to %s' % (connection, address))
            # todo: open thread for new server loop (possibly new object)
            start_new_thread(Server, (connection, address))

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
            print('User authenticated')
            self.state = READING
        else:
            self.connection.sendall(CONNECTION_DENIED.encode())

    def write_file(self):
        server_log('writing file: %s' % self.item_name)
        error = self.file_manager.write_file(self.simplified_abs_path, self.item_name, self.data_received)
        if error:
            server_log('File write failed: ' + error)
        else:
            server_log('File write successfully')
        self.state = READING

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

    def get_byte_list(self):
        received_byte_list = list()
        if self.state != WRITING_FILE:
            data = self.connection.recv(CONNECTION_BYTES)
            received_byte_list.append(data)
            print("Received message: %s" % data.decode())
        else:
            self.connection.settimeout(0.2)
            while True:
                try:
                    data = self.connection.recv(CONNECTION_BYTES)
                    if not data:
                        break
                    received_byte_list.append(data)
                except:
                    break
            self.connection.settimeout(None)
        return received_byte_list

    def decode(self, received_byte_list):
        if self.state == WRITING_FILE:
            return b''.join(received_byte_list)
        else:
            return b''.join(received_byte_list).decode()

    def send_error(self, error):
        self.connection.sendall(('%s%s' % (INVALID, error)).encode())
        return '%s%s' % (INVALID, error)

    def send_response(self, response):
        self.connection.sendall(response.encode())

    def cd_command(self, args_list):
        if not args_list:
            self.connection.sendall('%sNo path sent' % INVALID)
        else:
            path = args_list[0]
            error = self.file_manager.resolve_path(path)
            if not error:
                self.pwd_command([])
            else:
                server_log('Access denied')
                self.connection.sendall(('%s%s' % (INVALID, error)).encode())

    def ls_command(self, args_list):
        if not args_list:
            error, lt = self.file_manager.list_items()
        else:
            error, lt = self.file_manager.list_items(args_list[0])
        if error:
            self.send_error(error)
        else:
            self.send_response(str(lt))

    def pwd_command(self, args_list):
        if self.file_manager.current_path == '':
            self.connection.sendall(' '.encode())
        else:
            self.connection.sendall(self.file_manager.current_path.encode())

    def interact(self, args_list, function, extra_arg=None):
        """
        Generic function to do something to a item (the item can be ether a directory or file)
        :param args_list: It is a list
                          1 Cannot be an empty
                          2 can contain ether a relative path or absolute path to the item
        :param function: Function that will perform an action on the item (being this item an directory or a file)
        :return: an error message in case of any error during the function or an empty string if no error
        """
        if not args_list:
            error = self.send_error('Need to specify the directory name')
        else:
            item_path = args_list[0]

            if not item_path.startswith('/'):
                item_path = path.join(self.file_manager.current_path, item_path)

            abs_path, item_name = path.split(item_path)
            error, simplified_item_path = self.file_manager.validate_absolute_path(abs_path)

            self.simplified_abs_path = simplified_item_path
            self.item_name = item_name

            if error:
                if not extra_arg:
                    error = self.send_error(error)
            else:
                if not extra_arg:
                    error = function(simplified_item_path, item_name)
                    if error:
                        error = self.send_error(error)
                    else:
                        self.connection.sendall('ok'.encode())
                else:
                    error = function(simplified_item_path, item_name, extra_arg)
        return error

    def mkdir_command(self, args_list):
        self.interact(args_list, self.file_manager.create_directory)

    def rmdir_command(self, args_list):
        self.interact(args_list, self.file_manager.delete_directory)

    def delete_command(self, args_list):
        self.interact(args_list, self.file_manager.delete_file)

    def get_command(self, args_list):
        error = self.interact(args_list, self.file_manager.read_file, extra_arg=self.connection)
        if error:
            self.send_error(error)

    def put_command(self, args_list):
        if not args_list:
            self.send_error('Need to specify the file')
        elif len(args_list) == 1:
            error = self.interact(args_list, self.file_manager.write_file)
            if not error:
                self.state = WRITING_FILE

    def close_command(self, args_list):
        pass

    def open_command(self, args_list):
        pass

    def quit_command(self, args_list):
        pass

    def unknown_command(self, args_list):
        pass

    def empty_command(self, args_list):
        pass


if __name__ == "__main__":
    Server()
