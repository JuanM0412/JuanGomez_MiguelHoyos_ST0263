import socket
import random
import threading
import pickle
import sys
import time
import hashlib
import os
from collections import OrderedDict

# Valores predeterminados si no se proporcionan argumentos de línea de comandos
IP = "127.0.0.1"
PORT = 2000
BUFFER_SIZE = 4096

MAX_BITS = 2
MAX_NODES = 2 ** MAX_BITS

def getHash(key):
    """
    Toma una cadena de clave, utiliza SHA-1 para hashing y retorna un entero comprimido a 10 bits (1024).
    """
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % MAX_NODES

class Node:
    def __init__(self, ip, port):
        self.filenameList = []
        self.ip = ip
        self.port = port
        self.address = (ip, port)
        self.id = getHash(ip + ":" + str(port))
        self.pred = (ip, port)
        self.predID = self.id
        self.succ = (ip, port)
        self.succID = self.id
        self.fingerTable = OrderedDict()

        try:
            self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ServerSocket.bind((IP, PORT))
            self.ServerSocket.listen()
        except socket.error as e:
            print(f"Error al abrir el socket: {e}")

    def listenThread(self):
        """
        Almacena la IP y el puerto en address y guarda la conexión y subprocesos.
        """
        while True:
            try:
                connection, address = self.ServerSocket.accept()
                connection.settimeout(120)
                threading.Thread(target=self.connectionThread, args=(connection, address)).start()
            except socket.error as e:
                print(f"Error al aceptar la conexión: {e}")

    def connectionThread(self, connection, address):
        """
        Subproceso para cada conexión de par.
        """
        try:
            rDataList = pickle.loads(connection.recv(BUFFER_SIZE))
        except (EOFError, pickle.UnpicklingError) as e:
            print(f"Error al recibir datos: {e}")
            return

        connectionType = rDataList[0]
        if connectionType == 0:
            print(f"Conexión con: {address[0]}:{address[1]}")
            print("Solicitud de unión a la red recibida")
            self.joinNode(connection, address, rDataList)
            self.printMenu()
        elif connectionType == 1:
            print(f"Conexión con: {address[0]}:{address[1]}")
            print("Solicitud de carga/descarga recibida")
            self.transferFile(connection, address, rDataList)
            self.printMenu()
        elif connectionType == 2:
            connection.sendall(pickle.dumps(self.pred))
        elif connectionType == 3:
            self.lookupID(connection, address, rDataList)
        elif connectionType == 4:
            if rDataList[1] == 1:
                self.updateSucc(rDataList)
            else:
                self.updatePred(rDataList)
        elif connectionType == 5:
            self.updateFTable()
            connection.sendall(pickle.dumps(self.succ))
        else:
            print("Problema con el tipo de conexión")

    def joinNode(self, connection, address, rDataList):
        """
        Maneja la solicitud de unión a la red por otro nodo.
        """
        if rDataList:
            peerIPport = rDataList[1]
            peerID = getHash(peerIPport[0] + ":" + str(peerIPport[1]))
            oldPred = self.pred

            self.pred = peerIPport
            self.predID = peerID

            sDataList = [oldPred]
            connection.sendall(pickle.dumps(sDataList))

            time.sleep(0.1)
            self.updateFTable()
            self.updateOtherFTables()

    def transferFile(self, connection, address, rDataList):
        """
        Maneja la transferencia de archivos (carga/descarga) utilizando mensajes dummy.
        """
        choice = rDataList[1]
        filename = rDataList[2]
        
        if choice == 0:
            print(f"Solicitud de descarga para el archivo: {filename}")
            if filename not in self.filenameList:
                # Si el archivo no está aquí, buscar en la red
                successor = self.getSuccessor(self.succ, getHash(filename))
                sDataList = [1, 0, filename]  # Solicitud de descarga
                try:
                    sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sSocket.connect(successor)
                    sSocket.sendall(pickle.dumps(sDataList))
                    fileData = sSocket.recv(BUFFER_SIZE)
                    if fileData == b"NotFound":
                        connection.send("NotFound".encode('utf-8'))
                        print("Archivo no encontrado en la red")
                    else:
                        connection.send("Found".encode('utf-8'))
                        connection.sendall(fileData)
                except socket.error as e:
                    print(f"Error al conectar con el sucesor para descarga: {e}")
            else:
                connection.send("Found".encode('utf-8'))
                self.sendFile(connection, filename)
        elif choice == 1 or choice == -1:
            print(f"Recibiendo archivo: {filename}")
            self.filenameList.append(filename)
            self.receiveFile(connection, filename)
            print("Carga completa")
            if choice == 1 and self.address != self.succ:
                self.uploadFile(filename, self.succ, False)

    def sendFile(self, connection, filename):
        """
        Envía un archivo utilizando mensajes dummy.
        """
        print(f"Enviando archivo dummy: {filename}")
        try:
            dummy_message = f"Dummy data for {filename}"
            connection.sendall(dummy_message.encode('utf-8'))
            print(f"Archivo dummy enviado: {filename}")
        except Exception as e:
            print(f"Error al enviar el archivo dummy: {e}")

    def receiveFile(self, connection, filename):
        """
        Recibe un archivo utilizando mensajes dummy.
        """
        print(f"Recibiendo archivo dummy: {filename}")
        try:
            dummy_data = connection.recv(BUFFER_SIZE).decode('utf-8')
            print(f"Archivo dummy recibido: {dummy_data}")
        except Exception as e:
            print(f"Error al recibir el archivo dummy: {e}")

    def lookupID(self, connection, address, rDataList):
        keyID = rDataList[1]
        sDataList = []
        if self.id == keyID:  # Caso 0: Si keyId está en self
            sDataList = [0, self.address]
        elif self.succID == self.id:  # Caso 1: Si solo hay un nodo
            sDataList = [0, self.address]
        elif self.id > keyID:  # Caso 2: Node id mayor que keyId, preguntar pred
            if self.predID < keyID:  # Si pred es mayor que key, entonces self es el nodo
                sDataList = [0, self.address]
            elif self.predID > self.id:
                sDataList = [0, self.address]
            else:  # De lo contrario, enviar el pred de vuelta
                sDataList = [1, self.pred]
        else:  # Caso 3: node id menor que keyId USAR fingertable para buscar
            if self.id > self.succID:
                sDataList = [0, self.succ]
            else:
                value = ()
                for key, value in self.fingerTable.items():
                    if key >= keyID:
                        break
                value = self.succ
                sDataList = [1, value]
        connection.sendall(pickle.dumps(sDataList))

    def updateSucc(self, rDataList):
        newSucc = rDataList[2]
        self.succ = newSucc
        self.succID = getHash(newSucc[0] + ":" + str(newSucc[1]))

    def updatePred(self, rDataList):
        newPred = rDataList[2]
        self.pred = newPred
        self.predID = getHash(newPred[0] + ":" + str(newPred[1]))

    def stabilize(self):
        while True:
            time.sleep(5)  # Intervalo de estabilización
            if self.succ == self.address:
                continue

            try:
                # Conectar con el sucesor para preguntar por su predecesor
                sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sSocket.connect(self.succ)
                sSocket.sendall(pickle.dumps([2]))  # Solicitar el predecesor
                recvPred = pickle.loads(sSocket.recv(BUFFER_SIZE))
                sSocket.close()

                # Si el predecesor del sucesor es diferente a mí y está más cerca del nodo actual
                if recvPred != self.address and self.id < getHash(recvPred[0] + ":" + str(recvPred[1])) < self.succID:
                    self.succ = recvPred
                    self.succID = getHash(recvPred[0] + ":" + str(recvPred[1]))
                
                # Notificar al sucesor sobre el nodo actual como su posible predecesor
                notifySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                notifySocket.connect(self.succ)
                notifySocket.sendall(pickle.dumps([4, 1, self.address]))  # Enviar una notificación al sucesor
                notifySocket.close()

            except socket.error:
                print("Error al estabilizar la conexión con el sucesor")

    def notify(self, possiblePred):
        # Este método es invocado cuando otro nodo cree que debería ser el predecesor de este nodo
        possiblePredID = getHash(possiblePred[0] + ":" + str(possiblePred[1]))
        if self.pred is None or (self.predID < possiblePredID < self.id):
            self.pred = possiblePred
            self.predID = possiblePredID
            print(f"Actualizado predecesor a: {self.pred}")

    def start(self):
        threading.Thread(target=self.listenThread, args=()).start()
        threading.Thread(target=self.pingSucc, args=()).start()
        threading.Thread(target=self.stabilize, args=()).start()
        while True:
            print("Listening to other clients")   
            self.asAClientThread()

    def pingSucc(self):
        while True:
            time.sleep(2)
            if self.address == self.succ:
                continue
            try:
                pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pSocket.connect(self.succ)
                pSocket.sendall(pickle.dumps([2]))
                recvPred = pickle.loads(pSocket.recv(BUFFER_SIZE))
            except:
                print("\nNodo fuera de línea detectado!\nEstabilizando...")
                newSuccFound = False
                value = ()
                for key, value in self.fingerTable.items():
                    if value[0] != self.succID:
                        newSuccFound = True
                        break
                if newSuccFound:
                    self.succ = value[1]
                    self.succID = getHash(self.succ[0] + ":" + str(self.succ[1]))
                    pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pSocket.connect(self.succ)
                    pSocket.sendall(pickle.dumps([4, 0, self.address]))
                    pSocket.close()
                else:
                    self.pred = self.address
                    self.predID = self.id
                    self.succ = self.address
                    self.succID = self.id
                self.updateFTable()
                self.updateOtherFTables()
                self.printMenu()

    def asAClientThread(self):
        self.printMenu()
        userChoice = input()
        if userChoice == "1":
            ip = input("Enter IP to connect: ")
            port = input("Enter port: ")
            self.sendJoinRequest(ip, int(port))
        elif userChoice == "2":
            self.leaveNetwork()
        elif userChoice == "3":
            filename = input("Enter filename: ")
            fileID = getHash(filename)
            recvIPport = self.getSuccessor(self.succ, fileID)
            self.uploadFile(filename, recvIPport, True)
        elif userChoice == "4":
            filename = input("Enter filename: ")
            self.downloadFile(filename)
        elif userChoice == "5":
            self.printFTable()
        elif userChoice == "6":
            print(f"My ID: {self.id}, Predecessor: {self.predID}, Successor: {self.succID}")

    def sendJoinRequest(self, ip, port):
        try:
            recvIPPort = self.getSuccessor((ip, port), self.id)
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerSocket.connect(recvIPPort)
            sDataList = [0, self.address]
            
            peerSocket.sendall(pickle.dumps(sDataList))
            rDataList = pickle.loads(peerSocket.recv(BUFFER_SIZE))
            self.pred = rDataList[0]
            self.predID = getHash(self.pred[0] + ":" + str(self.pred[1]))
            self.succ = recvIPPort
            self.succID = getHash(recvIPPort[0] + ":" + str(recvIPPort[1]))

            sDataList = [4, 1, self.address]
            pSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket2.connect(self.pred)
            pSocket2.sendall(pickle.dumps(sDataList))
            pSocket2.close()
            peerSocket.close()
        except socket.error:
            print("Socket error. Recheck IP/Port.")

    def leaveNetwork(self):
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.succ)
        pSocket.sendall(pickle.dumps([4, 0, self.pred]))
        pSocket.close()

        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.pred)
        pSocket.sendall(pickle.dumps([4, 1, self.succ]))
        pSocket.close()
        print("I had files:", self.filenameList)

        for filename in self.filenameList:
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket.connect(self.succ)
            sDataList = [1, 1, filename]
            pSocket.sendall(pickle.dumps(sDataList))
            pSocket.recv(BUFFER_SIZE)
            self.sendFile(pSocket, filename)
            pSocket.close()
            print("File replicated")
        
        self.updateOtherFTables()
        
        self.pred = (self.ip, self.port)
        self.predID = self.id
        self.succ = (self.ip, self.port)
        self.succID = self.id
        self.fingerTable.clear()
        print(self.address, "has left the network")

    def uploadFile(self, filename, recvIPport, replicate):
        print("Uploading file", filename)
        sDataList = [1]
        if replicate:
            sDataList.append(1)
        else:
            sDataList.append(-1)
        try:
            dummy_message = f"Dummy data for {filename}"
            sDataList = sDataList + [filename]
            cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cSocket.connect(recvIPport)
            cSocket.sendall(pickle.dumps(sDataList))
            cSocket.sendall(dummy_message.encode('utf-8'))
            cSocket.close()
            print("File uploaded")
        except socket.error:
            print("Error in uploading file")

    def downloadFile(self, filename):
        print("Downloading file", filename)
        fileID = getHash(filename)
        recvIPport = self.getSuccessor(self.succ, fileID)  # Encuentra el sucesor responsable
        sDataList = [1, 0, filename]  # 1: solicitud de transferencia, 0: descarga
        try:
            cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cSocket.connect(recvIPport)
            cSocket.sendall(pickle.dumps(sDataList))
            fileData = cSocket.recv(BUFFER_SIZE)
            if fileData == b"NotFound":
                print("File not found:", filename)
            else:
                print("Receiving file:", filename)
                self.receiveFile(cSocket, filename)
            cSocket.close()
        except socket.error as e:
            print(f"Error en la descarga del archivo: {e}")

    def getSuccessor(self, address, keyID):
        rDataList = [1, address]
        recvIPPort = rDataList[1]
        while rDataList[0] == 1:
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                peerSocket.connect(recvIPPort)
                sDataList = [3, keyID]
                peerSocket.sendall(pickle.dumps(sDataList))
                rDataList = pickle.loads(peerSocket.recv(BUFFER_SIZE))
                recvIPPort = rDataList[1]
                peerSocket.close()
            except socket.error:
                print("Connection denied while getting Successor")
        return recvIPPort

    def updateFTable(self):
        for i in range(MAX_BITS):
            entryId = (self.id + (2 ** i)) % MAX_NODES
            if self.succ == self.address:
                self.fingerTable[entryId] = (self.id, self.address)
                continue
            recvIPPort = self.getSuccessor(self.succ, entryId)
            recvId = getHash(recvIPPort[0] + ":" + str(recvIPPort[1]))
            self.fingerTable[entryId] = (recvId, recvIPPort)

    def updateOtherFTables(self):
        here = self.succ
        while True:
            if here == self.address:
                break
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                pSocket.connect(here)
                pSocket.sendall(pickle.dumps([5]))
                here = pickle.loads(pSocket.recv(BUFFER_SIZE))
                pSocket.close()
                if here == self.succ:
                    break
            except socket.error:
                print("Connection denied")

    def printMenu(self):
        print("\n1. Join Network\n2. Leave Network\n3. Upload File\n4. Download File")
        print("5. Print Finger Table\n6. Print my predecessor and successor")

    def printFTable(self):
        print("Printing F Table")
        for key, value in self.fingerTable.items():
            print("KeyID:", key, "Value", value)

if len(sys.argv) < 3:
    print("Arguments not supplied (Defaults used)")
else:
    IP = sys.argv[1]
    PORT = int(sys.argv[2])

myNode = Node(IP, PORT)
print("My ID is:", myNode.id)
myNode.start()
myNode.ServerSocket.close()