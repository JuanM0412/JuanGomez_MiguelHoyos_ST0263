SERVER_IP = '127.0.0.1'
SERVER_PORT = 50051
MAX_NODES = 128
SUB_SPACES = 4


def get_server_info():
    return SERVER_IP, SERVER_PORT


def get_intervals_info():
    return MAX_NODES, SUB_SPACES