import threading, os
from src.network.node import *
from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    server_ip = os.getenv('SERVER_IP')
    server_port = os.getenv('SERVER_PORT')

    peer = NodePeer(os.getenv('PEER_IP'), os.getenv('PEER_PORT'), server_ip, server_port, os.getenv("DOWNLOADS_DIR"))
    peer.connect()
    
    try:
        server_thread = threading.Thread(target=peer.serve)
        server_thread.start()

        main_thread = threading.Thread(target=main_menu, args=(peer,))
        main_thread.start()

        check_thread = threading.Thread(target=peer.check_external_files)
        check_thread.start()

        main_thread.join()
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Shutting down...")
    finally:
        peer.disconnect()

        server_thread.join()
        check_thread.join()