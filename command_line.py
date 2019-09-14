from utils import COMMAND_LIST, UNKNOWN_COMMAND


class CommandLine:

    def __init__(self, method_list):
        self.command_list = COMMAND_LIST
        self.method_hash = dict()

        for idx, command in enumerate(self.command_list):
            self.method_hash[command] = method_list[idx]

    def execute_command(self, command, arg_list):
        if command in self.method_hash:
            self.method_hash[command](arg_list)
        else:
            self.method_hash[UNKNOWN_COMMAND](arg_list)
            # raise Exception("Unknown command")
