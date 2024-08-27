import random
from concurrent import futures
import grpc
import peer_pb2
import peer_pb2_grpc


class Server(peer_pb2_grpc.PeerServiceServicer):
    def __init__(self, ip: str, port: int, intervals: list, sub_spaces: int, intervals_size: int):
        self.ip = ip
        self.port = port
        self.free_ids = intervals
        self.sub_spaces = {}
        for i in range(sub_spaces):
            end = (i + 1) * intervals_size
            self.sub_spaces[end] = []


    def Register(self, request, context):
        ip = request.ip
        port = request.port
        sub_interval = 0
        for upper_bound, nodes in self.sub_spaces.items():
            if not nodes:
                available_id = min(self.free_ids[sub_interval])
                self.free_ids[sub_interval].remove(available_id)
                self.sub_spaces[upper_bound].append((available_id, (ip, port)))
                return peer_pb2.RegisterResponse(id=available_id)
            sub_interval += 1

        rand = random.randint(0, sub_interval - 1)
        upper_bounds = list(self.sub_spaces.keys())
        available_id = min(self.free_ids[rand])
        self.free_ids[rand].remove(available_id)
        self.sub_spaces[upper_bounds[rand]].append((available_id, (ip, port)))

        return peer_pb2.RegisterResponse(id=available_id)


    def Unregister(self, request, context):
        node_id = request.id
        upper_bounds = list(self.sub_spaces.keys())
        sub_interval = 0
        while sub_interval < len(upper_bounds):
            if node_id <= upper_bounds[sub_interval]:
                break
            sub_interval += 1
        
        peers = self.sub_spaces[upper_bounds[sub_interval]]
        index_to_remove = 0
        founded = False
        for peer in peers:
            if peer[0] == node_id:
                founded = True
                break
            index_to_remove += 1

        if founded:
            self.free_ids[sub_interval].add(node_id)
            self.sub_spaces[upper_bounds[sub_interval]].pop(index_to_remove)
            return peer_pb2.UnregisterResponse(message="Successfully disconnected")
        
        return peer_pb2.UnregisterResponse(message="Error. Ese id de mierda no existe")


    def GetInternalTable(self, request, context):
        node_id = request.id
        upper_bounds = list(self.sub_spaces.keys())
        sub_interval = 0
        while sub_interval < len(upper_bounds):
            if node_id <= upper_bounds[sub_interval]:
                break
            sub_interval += 1
        
        peers = self.sub_spaces[upper_bounds[sub_interval]]
        response = peer_pb2.InternalTableResponse()
        for peer in peers:
            node_info = peer_pb2.NodeInfo(id=peer[0], ip=peer[1][0], port=peer[1][1])
            response.nodes.append(node_info)
        
        return response
    

    def GetInterval(self, request, context):
        node_id = request.id  # Extract the node_id from the request object

        upper_bounds = list(self.sub_spaces.keys())
        sub_interval = 0
        while sub_interval < len(upper_bounds):
            if node_id <= upper_bounds[sub_interval]:
                break
            sub_interval += 1

        peers = self.sub_spaces[upper_bounds[sub_interval]]

        while not peers:
            peers = self.sub_spaces[upper_bounds[sub_interval]]
            sub_interval -= 1    

        response = peer_pb2.InternalTableResponse()
        for peer in peers:
            node_info = peer_pb2.NodeInfo(id=peer[0], ip=peer[1][0], port=peer[1][1])
            response.nodes.append(node_info) 

        return response


def serve():
    print('Server is running')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    peer_pb2_grpc.add_PeerServiceServicer_to_server(Server(ip='127.0.0.1', port=2000, intervals=intervals, sub_spaces=sub_spaces, intervals_size=intervals_size), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    max_nodes = 128
    sub_spaces = 4
    intervals_size = int(max_nodes / sub_spaces)
    intervals = []

    for i in range(sub_spaces):
        start = i * intervals_size + 1
        end = (i + 1) * intervals_size
        id_ranges = set(range(start, end + 1))
        intervals.append(id_ranges)

    serve()