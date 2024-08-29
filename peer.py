import threading, argparse
from src.network.node import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NodePeer P2P Network')
    parser.add_argument('--port', type=int, required=True, help='Port number for the NodePeer')
    args = parser.parse_args()

    peer = NodePeer('127.0.0.1', args.port)
    peer.connect()

    server_thread = threading.Thread(target=peer.serve)
    server_thread.daemon = True
    server_thread.start()

    main_thread = threading.Thread(target=main_menu, args=(peer,))
    main_thread.daemon = True
    main_thread.start()

    check_thread = threading.Thread(target=peer.check_external_files)
    check_thread.daemon = True
    check_thread.start()

    main_thread.join()