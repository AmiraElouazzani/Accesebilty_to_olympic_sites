from .Edge import Edge
from .Vertex import Vertex
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, vertices : list[Vertex], edges : list[Edge], name = "default_name") -> None:
        self.vertices = vertices
        self.edges = edges

    def draw(self):

        for v in self.vertices:
            v.draw()

        for e in self.edges:
            e.draw()

        plt.title('Graph Vertices')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')

    def show(self):
        plt.show()