from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser

from src import Graph
from src import Edge

O = olympic_parser()
S = station_parser()

V = S + O

#test edge
e = Edge.Edge(V[0], V[1], 1)
E = [e]

G = Graph.Graph(V, E, name="test_graph")
G.draw()
G.show()