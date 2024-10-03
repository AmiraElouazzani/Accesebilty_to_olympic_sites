from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser

from src import Graph

O = olympic_parser()
S = station_parser()

V = S + O
E = []

G = Graph.Graph(V, E, name="test_graph")
G.set_distance_threshold(1000)
G.draw()