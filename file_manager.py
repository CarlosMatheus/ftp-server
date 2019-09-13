from utils import ROOT_DIR_NAME
from os import path
from os import mkdir


class FileManager:

    def __init__(self):
        self.initiate_root_folder()

    def initiate_root_folder(self):
        if not path.exists(ROOT_DIR_NAME):
            mkdir(ROOT_DIR_NAME)

    def write_file(self, file_data, file_path, file_name):
        file_path = path.join(ROOT_DIR_NAME, file_path)
        if not path.exists(file_path):
            raise Exception("File's path doesn't exist: %s" % file_path)
        else:
            file_path = path.join(file_path, file_name)
            f = open(file_path, 'wb+')
            f.write(file_data)
