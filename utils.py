DEFAULT_ADDRESS = ('0.0.0.0', 8080)
COMMAND_LIST = ['cd', 'ls', 'pwd', 'mkdir', 'rmdir', 'get', 'put', 'delete', 'close', 'open', 'quit', 'unknown']
CONNECTION_BYTES = 16*1024

# server states:
READING = 'reading'
TESTING = 'testing'
WRITING_FILE = 'writing_file'
USER_AUTH = 'user_auth'

# Messages
TEST_STRING = '-----/test/-----'
FILE_STRING = '-----/file/-----'
INVALID = '14e4894c30ec4ece91df949863a797'
CONNECTION_ACCEPTED = 'connection accepted'
CONNECTION_DENIED = 'connection denied'
DEFAULT_SEND_BACK_MESSAGE = 'I am server \n'

ROOT_DIR_NAME = 'root'
UNKNOWN_COMMAND = 'unknown'

ERROR_NOT_A_DIRECTORY = 'Not a directory'


def server_log(message):
    print(message)
