import threading, argparse
from src.network.node import *
from bootstrap import get_server_info


if __name__ == '__main__':
    server_ip, server_port = get_server_info()

    parser = argparse.ArgumentParser(description='NodePeer P2P Network')
    parser.add_argument('--port', type=int, required=True, help='Port number for the NodePeer')
    args = parser.parse_args()

    peer = NodePeer('127.0.0.1', args.port, server_ip, server_port)
    peer.connect()
    
    try:
        # Start server in a separate thread
        server_thread = threading.Thread(target=peer.serve)
        server_thread.start()

        # Start the main menu in a separate thread
        main_thread = threading.Thread(target=main_menu, args=(peer,))
        main_thread.start()

        # Start checking external files in a separate thread
        check_thread = threading.Thread(target=peer.check_external_files)
        check_thread.start()

        # Wait for threads to complete
        main_thread.join()
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Shutting down...")
    finally:
        peer.disconnect()

        # Ensure all threads have finished
        server_thread.join()
        check_thread.join()