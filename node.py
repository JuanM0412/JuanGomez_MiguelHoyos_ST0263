import hashlib
import threading
import requests
import argparse
import time
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import signal
import grpc
import peer_pb2
import peer_pb2_grpc


def get_hash(key):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % 128


class NodePeer:
    def __init__(self, ip: str, port: int):
        self.own_files = {}
        self.external_files = {}
        self.downloaded_files = []
        self.ip = ip
        self.port = port
        self.id = None
        self.upper_limit = None

        self.channel = grpc.insecure_channel(f'127.0.0.1:50051')
        self.stub = peer_pb2_grpc.PeerServiceStub(self.channel)


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
        # print("HASH DEL ARCHIVO:", file_hash)
        '''
            peer = [ip: str, port: int]
        '''
        peer, owner_file = self.find_destination(file_hash)
        # Enviar archivo al nodo correspondiente (o intervalo) dado el hash
        if owner_file:
            response = requests.post(
                f'http://{peer[0]}:{peer[1]}/receive_own_file',
                json={'name': file, 'hash_value': file_hash}
            )
            return True
        else:
            response = requests.post(
                f'http://{peer[0]}:{peer[1]}/receive_external_file',
                json={'name': file, 'hash_value': file_hash}
            )
            return False


    def find_node(self, id: int):
        flag = True
        node_list = self.request_interval(id)
        
        for node in node_list:
            if node[0] == id:
                return node[1]
            flag = False

        # Maneja cuando el archivo si está en el intervalo pero no existe el nodo
        if flag == False:
            return node_list[0][1]


    def download_file(self, file: str):
        file_hash = get_hash(file)
        peer = self.find_node(file_hash)

        response = requests.get(
            f'http://{peer[0]}:{peer[1]}/send_file',
            json={'name': file, 'hash_value': file_hash}
        )
        response = response.json()
        
        if response != '0':
            self.downloaded_files.append(response)
            print(f'Archivo {response} descargado')
        else:
            print('File does not exist')


    def send_file(self, file_name: str, hash_value: int):
        # Change names
        if hash_value in self.own_files.keys():
            files = self.own_files[hash_value]
            for file in files:
                if file == file_name:
                    return file_name
        elif hash_value in self.external_files.keys():
            files = self.external_files[hash_value]
            for file in files:
                if file == file_name:
                    return file_name
        else:
            return '0'


    def receive_own_file(self, file: str, hash_value: int):
        if hash_value in self.own_files:
            files = self.own_files[hash_value]
            files.add(file)
            self.own_files[hash_value] = files
        else:
            self.own_files[hash_value] = {file}

        #print('Archivo propio recibido')

    
    def receive_external_file(self, file: str, hash_value: int):
        if hash_value in self.external_files:
            files = self.external_files[hash_value]
            files.add(file)
            self.external_files[hash_value] = files
        else:
            self.external_files[hash_value] = {file}

        #print('Archivo externo recibido')


    def request_node_list(self):
        response = self.stub.GetInternalTable(peer_pb2.InternalTableRequest(id=self.id))
        return [(node.id, (node.ip, node.port)) for node in response.nodes]
    

    def request_interval(self, node_id): 
        response = self.stub.GetInterval(peer_pb2.InternalTableRequest(id=node_id))
        return [(node.id, (node.ip, node.port)) for node in response.nodes]


    def connect(self):
        response = self.stub.Register(peer_pb2.RegisterRequest(ip=self.ip, port=str(self.port)))
        self.id = response.id
        self.upper_limit = response.upper_bound


    def disconnect(self):
        response = self.stub.Unregister(peer_pb2.UnregisterRequest(id=self.id))
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
                        # Intentar subir el archivo al nodo correspondiente
                        response = self.upload_file(file)
                        if response:
                            # Si el archivo llegó a su destino, marcarlo para eliminarlo del peer actual
                            files_to_remove.append((hash_value, file))
                
                # Eliminar los archivos que ya llegaron a su nodo correspondiente
                for hash_value, file in files_to_remove:
                    self.external_files[hash_value].remove(file)
                    if not self.external_files[hash_value]:  # Si no quedan archivos para ese hash, eliminar la clave
                        del self.external_files[hash_value]



def start_api_server(peer: NodePeer):
    app = FastAPI()

    class File(BaseModel):
        name: str
        hash_value: int

    @app.post('/receive_own_file')
    def receive_own_file(file: File):
        try:
            peer.receive_own_file(file.name, file.hash_value)
            return {"status": "success", "message": f"File {file.name} received with hash {file.hash_value}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    @app.post('/receive_external_file')
    def receive_external_file(file: File):
        try:
            peer.receive_external_file(file.name, file.hash_value)
            return {"status": "success", "message": f"File {file.name} received with hash {file.hash_value}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    @app.get('/send_file')
    def send_file(file: File):
        try:
            response = peer.send_file(file.name, file.hash_value)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    uvicorn.run(app, host=peer.ip, port=peer.port)
 

def main_menu(peer: NodePeer):
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
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NodePeer P2P Network')
    parser.add_argument('--port', type=int, required=True, help='Port number for the NodePeer')
    args = parser.parse_args()

    # Instanciar el nodo
    peer = NodePeer('127.0.0.1', args.port)

    # Conectar el nodo
    peer.connect()

    # Iniciar el servidor API en un thread separado
    api_thread = threading.Thread(target=start_api_server, args=(peer,))
    api_thread.daemon = True
    api_thread.start()

    # Iniciar el menú principal
    main_thread = threading.Thread(target=main_menu, args=(peer,))
    main_thread.daemon = True
    main_thread.start()

    check_thread = threading.Thread(target=peer.check_external_files)
    check_thread.daemon = True
    check_thread.start()

    main_thread.join()