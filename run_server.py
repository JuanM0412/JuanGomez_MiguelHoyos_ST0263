from src.network.server import *
from dotenv import load_dotenv
import os


load_dotenv()


if __name__ == '__main__':
    ip = os.getenv('SERVER_IP')
    port = os.getenv('SERVER_PORT')
    max_nodes = int(os.getenv('MAX_NODES'))
    sub_spaces = int(os.getenv('SUB_SPACES'))

    intervals_size = int(max_nodes / sub_spaces)
    intervals = []

    for i in range(sub_spaces):
        start = i * intervals_size + 1
        end = (i + 1) * intervals_size
        id_ranges = set(range(start, end + 1))
        intervals.append(id_ranges)

    serve(ip, port, intervals, sub_spaces, intervals_size)