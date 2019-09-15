from utils import \
    ROOT_DIR_NAME, \
    server_log, \
    ERROR_NOT_A_DIRECTORY, \
    ERROR_FILE_PATH_DOES_NOT_EXIST, \
    ERROR_FILE_ALREADY_EXIST
from os import path, mkdir, listdir, remove
import shutil


class FileManager:

    def __init__(self, abs_root_folder=False, no_root_folder=False):
        self.abs_root_folder = abs_root_folder
        self.no_root_folder = no_root_folder

        self.root_folder_abs_directory = ''
        self.current_path = ''

        if not abs_root_folder:
            self.initiate_root_folder()
        else:
            self.root_folder_abs_directory = ''
            self.current_path = self.get_current_folder()

    def get_current_folder(self):
        return path.dirname(path.abspath(__file__))

    def initiate_root_folder(self):
        if not path.exists(ROOT_DIR_NAME):
            mkdir(ROOT_DIR_NAME)
        if not self.no_root_folder:
            self.root_folder_abs_directory = path.join(self.get_current_folder(), ROOT_DIR_NAME)
        else:
            self.root_folder_abs_directory = self.get_current_folder()

    def resolve_path(self, relative_path):
        error, simplified_path = self.validate_relative_path(relative_path)
        if not error:
            self.current_path = simplified_path
        return error

    def validate_absolute_path(self, absolute_path):
        aux_path = self.current_path
        self.current_path = ''
        error, simplified_path = self.validate_relative_path(absolute_path)
        self.current_path = aux_path
        return error, simplified_path

    def validate_relative_path(self, relative_path):
        """
        Validates a path returning an error message and the simplified path
        :param relative_path:
        :return: error (in case there is an error), simplified path in case there is no error
        """
        if not relative_path:
            current_path = ''
            return '', current_path
        else:
            if relative_path.startswith('/'):
                complete_path = self.root_folder_abs_directory + relative_path
            elif relative_path.startswith('~') and self.abs_root_folder:
                complete_path = path.expanduser('~') + relative_path[1:]
            else:
                complete_path = path.join(self.root_folder_abs_directory, path.join(self.current_path, relative_path))
            complete_path = path.normpath(path.realpath(complete_path))
            server_log("Trying to access: %s" % complete_path)
            if not complete_path.startswith(self.root_folder_abs_directory):
                return 'Cannot go outside root folder', ''
            else:
                if not path.exists(complete_path):
                    return 'Directory not found', ''
                elif not path.isdir(complete_path):
                    return ERROR_NOT_A_DIRECTORY, ''
                else:
                    current_path = path.relpath(complete_path, self.root_folder_abs_directory)
                    if current_path == '.':
                        current_path = ''
                    return '', current_path

    def validate_file(self, relative_path):
        directory, file = path.split(relative_path)
        error, simplified_dir = self.validate_relative_path(directory)
        if error:
            return False, error
        else:
            abs_file_path = path.join(self.root_folder_abs_directory, path.join(simplified_dir, file))
            if not path.exists(abs_file_path):
                return False, 'File not found'
            elif not path.isfile(abs_file_path):
                return False, 'Not a file'
            else:
                return True, ''

    def create_directory(self, simplified_abs_path, dir_name):
        complete_path = path.join(self.root_folder_abs_directory, simplified_abs_path, dir_name)
        if not path.exists(complete_path):
            mkdir(complete_path)
            return ''
        else:
            return 'Directory already exist'

    def delete_directory(self, simplified_abs_path, dir_name):
        complete_path = path.join(self.root_folder_abs_directory, simplified_abs_path, dir_name)
        if path.exists(complete_path):
            shutil.rmtree(complete_path)
            return ''
        else:
            return 'Directory not found'

    def delete_file(self, simplified_abs_path, file_name):
        complete_path = path.join(self.root_folder_abs_directory, simplified_abs_path, file_name)
        if path.exists(complete_path):
            remove(complete_path)
            return ''
        else:
            return 'File not found'

    def list_items(self, directory=None):
        if directory is None:
            simplified_path = self.current_path
            error = ''
        else:
            error, simplified_path = self.validate_relative_path(directory)
        if error:
            return error, []
        else:
            abs_path = path.join(self.root_folder_abs_directory, simplified_path)
            lt = listdir(abs_path)
            return '', lt

    def read_file(self, simplified_abs_path, file_name, connection):
        complete_path = path.join(self.root_folder_abs_directory, simplified_abs_path, file_name)
        if path.exists(complete_path):
            connection.sendall('ok'.encode())
            with open(complete_path, 'rb') as f:
                connection.sendfile(f, 0)
            return ''
        else:
            return 'File does not exist'

    def write_file(self, simplified_abs_path, file_name, file_data=None):
        """
        Will return error in case the directory does not exist, or the file already exists
        Will write the file on the path (directory + file_name) if is passed the data
        in case no data is passed the function will only do some errors checks but nothing will be write
        :param simplified_abs_path: directory where file will be write
        :param file_name: the name of the file that will be created
        :param file_data: binary of the file
        :return:
        """

        if not self.abs_root_folder:
            complete_path = path.join(self.root_folder_abs_directory, simplified_abs_path, file_name)
            simplified_abs_path = path.join(self.root_folder_abs_directory, simplified_abs_path)
        else:
            complete_path = path.join(self.current_path, simplified_abs_path, file_name)
            simplified_abs_path = path.join(self.current_path, simplified_abs_path)

        if not path.exists(complete_path):
            if file_data is not None:
                if not path.exists(simplified_abs_path):
                    return ERROR_FILE_PATH_DOES_NOT_EXIST
                else:
                    f = open(complete_path, 'wb+')
                    f.write(file_data)
            return ''
        else:
            return ERROR_FILE_ALREADY_EXIST
