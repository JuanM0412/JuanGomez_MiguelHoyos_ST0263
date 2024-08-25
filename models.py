from pydantic import BaseModel

class Node(BaseModel):
    ip: str
    port: int
    
class NodeId(BaseModel):
    id: int