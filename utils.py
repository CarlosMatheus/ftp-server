DEFAULT_ADDRESS = ('0.0.0.0', 8084)
COMMAND_LIST = ['cd', 'ls', 'pwd', 'mkdir', 'rmdir', 'get', 'put', 'delete', 'close', 'open', 'quit']
CONNECTION_BYTES = 4096

# server states:
READING = 'reading'
TESTING = 'testing'
WRITING_FILE = 'writing_file'
USER_AUTH = 'user_auth'

# Messages
TEST_STRING = '-----/test/-----'
FILE_STRING = '-----/file/-----'
CONNECTION_ACCEPTED = 'connection accepted'
CONNECTION_DENIED = 'connection denied'
DEFAULT_SEND_BACK_MESSAGE = 'I am server \n'

ROOT_DIR_NAME = 'root'
