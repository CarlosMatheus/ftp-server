from utils import ROOT_DIR_NAME, server_log
from os import path
from os import mkdir
from os import listdir


class FileManager:

    def __init__(self):
        self.root_folder_abs_directory = ''
        self.current_path = ''

        self.initiate_root_folder()

    def initiate_root_folder(self):
        if not path.exists(ROOT_DIR_NAME):
            mkdir(ROOT_DIR_NAME)
        self.root_folder_abs_directory = path.join(path.dirname(path.abspath(__file__)), ROOT_DIR_NAME)
        print(self.root_folder_abs_directory)

    def resolve_path(self, relative_path):
        error, simplified_path = self.validate_path(relative_path)
        if not error:
            self.current_path = simplified_path
        return error

    def validate_path(self, relative_path):
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
                    return 'Not a directory', ''
                else:
                    current_path = path.relpath(complete_path, self.root_folder_abs_directory)
                    if current_path == '.':
                        current_path = ''
                    return '', current_path

    def validate_file(self, relative_path):
        directory, file = path.split(relative_path)
        error, simplified_dir = self.validate_path(directory)
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

    def write_file(self, file_data, file_path, file_name):
        file_path = path.join(ROOT_DIR_NAME, file_path)
        if not path.exists(file_path):
            raise Exception("File's path doesn't exist: %s" % file_path)
        else:
            file_path = path.join(file_path, file_name)
            f = open(file_path, 'wb+')
            f.write(file_data)

    def create_directory(self, simplified_path, dir_name):
        complete_path = path.join(self.root_folder_abs_directory, simplified_path, dir_name)
        if not path.exists(complete_path):
            mkdir(complete_path)
            return ''
        else:
            return 'Directory already exist'

    def list_items(self, directory=None):
        if directory is None:
            directory = self.current_path
        error, simplified_path = self.validate_path(directory)
        if error:
            return error, []
        else:
            abs_path = path.join(self.root_folder_abs_directory, simplified_path)
            lt = listdir(abs_path)
            return '', lt
