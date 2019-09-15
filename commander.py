from abc import ABC, abstractmethod
from command_line import CommandLine


class Commander(ABC):

    def __init__(self):
        super().__init__()
        self.command_line = self.setup_command_line()
        self.data_received = ''

    @staticmethod
    def unpack_command(data_received):
        lt = data_received.split(' ')
        return lt[0], lt[1:]

    def read_command(self):
        command, arg_list = self.unpack_command(self.data_received)
        self.command_line.execute_command(command, arg_list)

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
        return CommandLine(method_list)

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
