from fastapi import FastAPI, HTTPException
from server import Server
from models import Node, NodeId

app = FastAPI()

max_nodes = 128
sub_spaces = 1
intervals_size = int(max_nodes / sub_spaces)
intervals = []

for i in range(sub_spaces):
    start = i * intervals_size + 1
    end = (i + 1) * intervals_size
    id_ranges = set(range(start, end + 1))
    intervals.append(id_ranges)

server = Server(ip = '127.0.0.1', port = 2000, intervals = intervals, sub_spaces = sub_spaces, intervals_size = intervals_size)


@app.post('/register')
def register_node(node: Node):
    response = server.register(node.ip, node.port)
    return response


@app.post('/unregister')
def unregister_node(node_id: NodeId):
    response = server.unregister(node_id.id)
    return response


@app.get('/internal_table')
def get_internal_table(node_id: NodeId):
    response = server.get_internal_table(node_id.id)
    return response