from abc import ABC, abstractmethod
from utils import COMMAND_LIST, UNKNOWN_COMMAND


class Commander(ABC):

    def __init__(self):
        super().__init__()
        self.data_received = ''
        self.method_hash = dict()
        self.command_list = list()

        self.setup_command_line()

    def initiate_command_line(self, method_list):
        self.command_list = COMMAND_LIST

        for idx, command in enumerate(self.command_list):
            self.method_hash[command] = method_list[idx]

    def execute_command(self, command, arg_list):
        if command in self.method_hash:
            self.method_hash[command](arg_list)
        else:
            self.method_hash[UNKNOWN_COMMAND](arg_list)

    @staticmethod
    def unpack_command(data_received):
        lt = data_received.split(' ')
        return lt[0], lt[1:]

    def read_command(self):
        command, arg_list = self.unpack_command(self.data_received)
        self.execute_command(command, arg_list)

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
            self.unknown_command,
            self.empty_command,
        ]
        self.initiate_command_line(method_list)

    @abstractmethod
    def cd_command(self, args_list):
        pass

    @abstractmethod
    def ls_command(self, args_list):
        pass

    @abstractmethod
    def pwd_command(self, args_list):
        pass

    @abstractmethod
    def mkdir_command(self, args_list):
        pass

    @abstractmethod
    def rmdir_command(self, args_list):
        pass

    @abstractmethod
    def get_command(self, args_list):
        pass

    @abstractmethod
    def put_command(self, args_list):
        pass

    @abstractmethod
    def delete_command(self, args_list):
        pass

    @abstractmethod
    def close_command(self, args_list):
        pass

    @abstractmethod
    def open_command(self, args_list):
        pass

    @abstractmethod
    def quit_command(self, args_list):
        pass

    @abstractmethod
    def unknown_command(self, args_list):
        pass

    @abstractmethod
    def empty_command(self, args_list):
        pass
