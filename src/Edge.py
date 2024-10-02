from .Vertex import Vertex
import matplotlib.pyplot as plt


class Edge:
    def __init__(self, v1: Vertex, v2: Vertex, w: float):
        self.vertex1 = v1
        self.vertex2 = v2
        self.weight = w

    def draw(self):
        x1,y1 = self.vertex1.get_position()
        x2,y2 = self.vertex2.get_position()
        plt.plot([x1, x2], [y1, y2], color='black')
