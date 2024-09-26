from .Vertex import Vertex

class Edge:
    def __init__(self, v1: Vertex, v2: Vertex, w: float):
        self.vertex1 = v1
        self.vertex2 = v2
        self.weight = w