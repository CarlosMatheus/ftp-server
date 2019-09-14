from utils import ROOT_DIR_NAME
from os import path
from os import mkdir


class FileManager:

    def __init__(self):
        self.initiate_root_folder()
        self.root_folder_abs_directory = ''
        self.current_path = ' '

    def initiate_root_folder(self):
        if not path.exists(ROOT_DIR_NAME):
            mkdir(ROOT_DIR_NAME)
        self.root_folder_abs_directory = path.join(path.dirname(path.abspath(__file__)), ROOT_DIR_NAME)
        # print(self.root_folder_abs_directory)

    def resolve_path(self, relative_path):
        if not relative_path:
            self.current_path = ' '
            return ''
        else:
            complete_path = path.join(self.root_folder_abs_directory, path.join(self.current_path, relative_path))
            complete_path = path.normpath(path.realpath(complete_path))
            if not complete_path.startswith(self.root_folder_abs_directory):
                return 'Cannot go outside root folder'
            else:
                if not path.exists(complete_path):
                    return 'Directory not found'
                elif not path.isdir(complete_path):
                    return 'Not a directory'
                else:
                    self.current_path = path.relpath(complete_path, self.root_folder_abs_directory)
                    return ''

    def write_file(self, file_data, file_path, file_name):
        file_path = path.join(ROOT_DIR_NAME, file_path)
        if not path.exists(file_path):
            raise Exception("File's path doesn't exist: %s" % file_path)
        else:
            file_path = path.join(file_path, file_name)
            f = open(file_path, 'wb+')
            f.write(file_data)
