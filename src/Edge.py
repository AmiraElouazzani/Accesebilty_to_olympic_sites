from .Vertex import Vertex

class Edge:
    def __init__(self, v1: Vertex, v2: Vertex, w: float = 1):
        self.vertex1 = v1
        self.vertex2 = v2
        self.weight = w

    def __str__(self):
        return f"Edge: {self.vertex1} -> {self.vertex2} ({self.weight})"