import grpc
from concurrent import futures
import hashlib
import time
import threading
import p2p_pb2
import p2p_pb2_grpc
from collections import OrderedDict


MAX_BITS = 10        # 10-bit
MAX_NODES = 2 ** MAX_BITS


def getHash(key):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % MAX_NODES


class Peer(p2p_pb2_grpc.P2PServiceServicer):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.id = getHash(f"{ip}:{port}")
        self.pred = (ip, port)  # Predecesor
        self.predID = self.id
        self.succ = (ip, port)  # Sucesor
        self.succID = self.id
        self.fingerTable = OrderedDict()


    def start(self):
        # Iniciar el servicio gRPC en un hilo separado
        threading.Thread(target=self.serve).start()
        # Lógica de cliente para interactuar con otros peers
        self.clientOperations()


    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        p2p_pb2_grpc.add_P2PServiceServicer_to_server(self, server)
        server.add_insecure_port(f'{self.ip}:{self.port}')
        server.start()
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            server.stop(0)


    def clientOperations(self):
        while True:
            print("\n1. Join Network\n2. Leave Network\n3. Upload File\n4. Download File")
            print("5. Print Finger Table\n6. Print my predecessor and successor")
            choice = input("Enter choice: ")

            if choice == "1":
                ip = input("Enter IP to connect: ")
                port = int(input("Enter port: "))
                self.joinNetwork(ip, port)
            elif choice == "2":
                self.leaveNetwork()
            elif choice == "3":
                filename = input("Enter filename: ")
                self.uploadFile(filename)
            elif choice == "4":
                filename = input("Enter filename: ")
                self.downloadFile(filename)
            elif choice == "5":
                self.printFingerTable()
            elif choice == "6":
                print(f"My ID: {self.id}, Predecessor: {self.predID}, Successor: {self.succID}")


    def joinNetwork(self, ip, port):
        try:
            with grpc.insecure_channel(f'{ip}:{port}') as channel:
                stub = p2p_pb2_grpc.P2PServiceStub(channel)
                response = stub.JoinNetwork(p2p_pb2.JoinRequest(ip=self.ip, port=self.port))
                self.pred = (response.predecessor_ip, response.predecessor_port)
                self.predID = getHash(f"{response.predecessor_ip}:{response.predecessor_port}")
                self.succ = (ip, port)
                self.succID = getHash(f"{ip}:{port}")
                self.updateFTable()
        except grpc.RpcError as e:
            print(f"Failed to join network: {e}")


    def leaveNetwork(self):
        with grpc.insecure_channel(f'{self.succ[0]}:{self.succ[1]}') as channel:
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            stub.LeaveNetwork(p2p_pb2.LeaveRequest(ip=self.ip, port=self.port))
        self.pred = self.succ = (self.ip, self.port)
        self.predID = self.succID = self.id
        self.fingerTable.clear()
        print(f"{self.ip}:{self.port} has left the network")


    def uploadFile(self, filename):
        with open(filename, 'rb') as f:
            data = f.read()
        fileID = getHash(filename)
        recvIPport = self.getSuccessor(fileID)
        with grpc.insecure_channel(f'{recvIPport[0]}:{recvIPport[1]}') as channel:
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            stub.UploadFile(p2p_pb2.FileTransferRequest(filename=filename, data=data))
        print(f"File {filename} uploaded to {recvIPport}")


    def downloadFile(self, filename):
        fileID = getHash(filename)
        recvIPport = self.getSuccessor(fileID)
        with grpc.insecure_channel(f'{recvIPport[0]}:{recvIPport[1]}') as channel:
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            response = stub.DownloadFile(p2p_pb2.FileTransferRequest(filename=filename))
            with open(filename, 'wb') as f:
                f.write(response.data)
        print(f"File {filename} downloaded from {recvIPport}")


    def getSuccessor(self, keyID):
        recvIPport = self.succ
        with grpc.insecure_channel(f'{recvIPport[0]}:{recvIPport[1]}') as channel:
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            response = stub.LookupID(p2p_pb2.LookupRequest(keyID=keyID))
        return (response.ip, response.port)


    def updateFTable(self):
        entries = []
        for i in range(MAX_BITS):
            entryId = (self.id + (2 ** i)) % MAX_NODES
            recvIPport = self.getSuccessor(entryId)
            recvId = getHash(f"{recvIPport[0]}:{recvIPport[1]}")
            self.fingerTable[entryId] = (recvId, recvIPport)
            entries.append(p2p_pb2.FingerTableEntry(id=entryId, ip=recvIPport[0], port=recvIPport[1]))

        with grpc.insecure_channel(f'{self.succ[0]}:{self.succ[1]}') as channel:
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            stub.UpdateFTable(p2p_pb2.UpdateFTableRequest(entries=entries))


    def printFingerTable(self):
        print("Finger Table:")
        for key, value in self.fingerTable.items():
            print(f"ID: {key}, Successor ID: {value[0]}, IP: {value[1][0]}, Port: {value[1][1]}")


    def JoinNetwork(self, request, context):
        oldPred = self.pred
        self.pred = (request.ip, request.port)
        self.predID = getHash(f"{request.ip}:{request.port}")
        response = p2p_pb2.JoinResponse(predecessor_ip=oldPred[0], predecessor_port=oldPred[1])
        self.updateFTable()
        return response


    def LeaveNetwork(self, request, context):
        if (request.ip, request.port) == self.pred:
            self.pred = self.succ
            self.predID = self.succID
        elif (request.ip, request.port) == self.succ:
            self.succ = self.pred
            self.succID = self.predID
        self.updateFTable()
        return p2p_pb2.LeaveResponse(success=True)


    def UploadFile(self, request, context):
        with open(request.filename, 'wb') as f:
            f.write(request.data)
        return p2p_pb2.FileTransferResponse(success=True)


    def DownloadFile(self, request, context):
        try:
            with open(request.filename, 'rb') as f:
                data = f.read()
            return p2p_pb2.FileTransferResponse(success=True, data=data)
        except FileNotFoundError:
            return p2p_pb2.FileTransferResponse(success=False)


    def Ping(self, request, context):
        return p2p_pb2.PingResponse(predecessor_ip=self.pred[0], predecessor_port=self.pred[1])


    def LookupID(self, request, context):
        keyID = request.keyID
        if self.id == keyID or (self.id > keyID and self.predID < keyID):
            return p2p_pb2.LookupResponse(ip=self.ip, port=self.port)
        else:
            for key, value in self.fingerTable.items():
                if key >= keyID:
                    return p2p_pb2.LookupResponse(ip=value[1][0], port=value[1][1])
            return p2p_pb2.LookupResponse(ip=self.succ[0], port=self.succ[1])


    def UpdateFTable(self, request, context):
        for entry in request.entries:
            self.fingerTable[entry.id] = (entry.id, (entry.ip, entry.port))
        return p2p_pb2.UpdateFTableResponse(success=True)


if __name__ == '__main__':
    peer = Peer(ip="127.0.0.1", port=3000)
    
    # Ejecuta tanto el servidor gRPC como las operaciones del cliente
    peer.start()