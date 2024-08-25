import random

class Server:
    def __init__(self, ip: str, port: int, intervals: list, sub_spaces: int, intervals_size: int):
        self.ip = ip
        self.port = port
        self.free_ids = intervals
        self.sub_spaces = {}
        for i in range(sub_spaces):
            end = (i + 1) * intervals_size
            self.sub_spaces[end] = []


    def register(self, ip: str, port: str):
        sub_interval = 0
        for upper_bound, nodes in self.sub_spaces.items():
            if not nodes: 
                available_id = min(self.free_ids[sub_interval])
                self.free_ids[sub_interval].remove(available_id)
                self.sub_spaces[upper_bound].append((available_id, (ip, port)))
                return available_id
            sub_interval += 1

        rand = random.randint(0, sub_interval - 1)
        upper_bounds = list(self.sub_spaces.keys())
        available_id = min(self.free_ids[rand])
        self.free_ids[rand].remove(available_id)
        self.sub_spaces[upper_bounds[rand]].append((available_id, (ip, port)))

        return available_id


    def unregister(self, node_id: int):
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

            return{"Successfully disconnected"}
        
        return{"Error. Ese id de mierda no existe"}


    def get_internal_table(self, node_id: str):
        upper_bounds = list(self.sub_spaces.keys())
        sub_interval = 0
        while sub_interval < len(upper_bounds):
            if node_id <= upper_bounds[sub_interval]:
                break
            sub_interval += 1
        
        peers = self.sub_spaces[upper_bounds[sub_interval]]

        return peers
