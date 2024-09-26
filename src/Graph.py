from .Edge import Edge
from .Vertex import Vertex
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, vertices : list[Vertex], edges : list[Edge], name = "default_name") -> None:
        self.vertices = vertices
        self.edges = edges

    def draw(self):
        coords = [v.get_position()+[v.get_color()] for v in self.vertices]

        x_coords = [p[0] for p in coords]
        y_coords = [p[1] for p in coords]
        colors = [p[2] for p in coords]

        plt.scatter(x_coords, y_coords, c=colors)
        plt.title('Graph Vertices')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.show()