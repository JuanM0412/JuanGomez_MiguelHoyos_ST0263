import time, random, os, signal
from concurrent import futures
from src.utils import get_hash
import grpc
from src.proto import peer_pb2, peer_pb2_grpc


class NodePeer(peer_pb2_grpc.PeerServiceServicer):
    def __init__(self, ip: str, port: int, server_ip: str, server_port: str):
        self.own_files = {}
        self.external_files = {}
        self.downloaded_files = []
        self.ip = ip
        self.port = port
        self.id = None
        self.upper_limit = None

        self.server_channel = grpc.insecure_channel(f'{server_ip}:{server_port}')
        self.server_stub = peer_pb2_grpc.PeerServiceStub(self.server_channel)


    def find_destination(self, id: int):
        peer_found = True
        node_list = self.request_interval(id)

        for node in node_list:
            if node[0] == id:
                return (node[1], True)
        peer_found = False

        if not peer_found:
            random_node = random.randint(0, len(node_list) - 1)
            return (node_list[random_node][1], False)


    def upload_file(self, file: str):
        file_hash = get_hash(file)
        peer, owner_file = self.find_destination(file_hash)

        peer_channel = grpc.insecure_channel(f'{peer[0]}:{peer[1]}')
        peer_stub = peer_pb2_grpc.PeerServiceStub(peer_channel)

        if owner_file:
            response = peer_stub.ReceiveOwnFile(peer_pb2.File(name=file, hash_value=file_hash))
        else:
            response = peer_stub.ReceiveExternalFile(peer_pb2.File(name=file, hash_value=file_hash))

        return {
            "success": response.status == "success",
            "is_owner": owner_file 
        }


    def find_node(self, id: int):
        flag = True
        node_list = self.request_interval(id)
        
        for node in node_list:
            if node[0] == id:
                return node[1]
            flag = False

        if flag == False:
            return node_list[0][1]


    def download_file(self, file: str):
        file_hash = get_hash(file)
        peer = self.find_node(file_hash)

        peer_channel = grpc.insecure_channel(f'{peer[0]}:{peer[1]}')
        peer_stub = peer_pb2_grpc.PeerServiceStub(peer_channel)

        response = peer_stub.SendFile(peer_pb2.File(name=file, hash_value=file_hash))
        if response.file_name != '0':
            self.downloaded_files.append(response.file_name)
            print(f'File {response.file_name} downloaded')
        else:
            print('File does not exist')


    def SendFile(self, request, context):
        file_name = request.name
        hash_value = request.hash_value
        
        if hash_value in self.own_files.keys():
            files = self.own_files[hash_value]
            for file in files:
                if file == file_name:
                    return peer_pb2.FileResponse(status="success", message="File found", file_name=file_name)
        elif hash_value in self.external_files.keys():
            files = self.external_files[hash_value]
            for file in files:
                if file == file_name:
                    return peer_pb2.FileResponse(status="success", message="File found", file_name=file_name)
        
        return peer_pb2.FileResponse(status="error", message="File not found", file_name='0')


    def ReceiveOwnFile(self, request, context):
        file = request.name
        hash_value = request.hash_value
        if hash_value in self.own_files:
            files = self.own_files[hash_value]
            files.add(file)
            self.own_files[hash_value] = files
        else:
            self.own_files[hash_value] = {file}
        return peer_pb2.FileResponse(status="success", message=f"File {file} received", file_name=file)


    def ReceiveExternalFile(self, request, context):
        file = request.name
        hash_value = request.hash_value
        if hash_value in self.external_files:
            files = self.external_files[hash_value]
            files.add(file)
            self.external_files[hash_value] = files
        else:
            self.external_files[hash_value] = {file}
        return peer_pb2.FileResponse(status="success", message=f"File {file} received", file_name=file)


    def request_node_list(self):
        response = self.server_stub.GetInternalTable(peer_pb2.InternalTableRequest(id=self.id))
        return [(node.id, (node.ip, node.port)) for node in response.nodes]
    

    def request_interval(self, node_id: int): 
        response = self.server_stub.GetInterval(peer_pb2.InternalTableRequest(id=node_id))
        return [(node.id, (node.ip, node.port)) for node in response.nodes]


    def connect(self):
        response = self.server_stub.Register(peer_pb2.RegisterRequest(ip=self.ip, port=str(self.port)))
        self.id = response.id
        self.upper_limit = response.upper_bound


    def disconnect(self):
        response = self.server_stub.Unregister(peer_pb2.UnregisterRequest(id=self.id))
        print(response.message)
        self.id = None
        os.kill(os.getpid(), signal.SIGTERM)


    def check_external_files(self):
        while True:
            time.sleep(10)
            if not self.external_files:
                continue
            else:
                files_to_remove = []
                for hash_value, files in self.external_files.items():
                    for file in files:
                        result = self.upload_file(file)
                        if result["success"] and result["is_owner"]:
                            files_to_remove.append((hash_value, file))
                
                for hash_value, file in files_to_remove:
                    self.external_files[hash_value].remove(file)
                    if not self.external_files[hash_value]:
                        del self.external_files[hash_value]


    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        peer_pb2_grpc.add_PeerServiceServicer_to_server(self, server)
        server.add_insecure_port(f'{self.ip}:{self.port}')
        server.start()
        server.wait_for_termination()


def main_menu(peer: NodePeer):
    try:
        while True:
            option = int(input('Choose an option: \n1. Disconnect \n2. Upload file \n3. Download file \n4. My attributes \n5. Update node list \n6. Exit\n'))

            if option == 1:
                peer.disconnect()
                break
            elif option == 2:
                file_name = input('Enter the file name to upload: ')
                peer.upload_file(file_name)
            elif option == 3:
                file_name = input('Enter the file name to download: ')
                peer.download_file(file_name)
            elif option == 4:
                print(f'ID: {peer.id}')
                print(f'Upper limit: {peer.upper_limit}')
                print(f'Own file list: {peer.own_files}')
                print(f'External file list: {peer.external_files}')
                print(f'Downloaded files: {peer.downloaded_files}')
            elif option == 5:
                node_list = peer.request_node_list()
                print(node_list)
            elif option == 6:
                peer.disconnect()
                break
            else:
                print("Invalid option. Please try again.")
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Disconnecting...")
    finally:
        peer.disconnect()