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