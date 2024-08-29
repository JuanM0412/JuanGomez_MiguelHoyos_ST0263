from src.network.server import *
from bootstrap import *


if __name__ == '__main__':
    ip, port = get_server_info()
    max_nodes, sub_spaces = get_intervals_info()

    intervals_size = int(max_nodes / sub_spaces)
    intervals = []

    for i in range(sub_spaces):
        start = i * intervals_size + 1
        end = (i + 1) * intervals_size
        id_ranges = set(range(start, end + 1))
        intervals.append(id_ranges)

    serve(ip, port, intervals, sub_spaces, intervals_size)