from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce

from src import Graph
from src import Edge

O = olympic_parser()
S = station_parser()

#restriction are made for testing purposes

olympic_restriction = {"Stade Tour Eiffel",
                       "Pont d'Iéna",
                       "Arena Champs de Mars",
                       "Invalides"}

station_restriction = {"Champs de Mars",
                       "Bir Hakeim",
                       "École Militaire",
                       "Dupleix",
                       "Invalides"}

O = [o for o in O if o.name in olympic_restriction]
S = [s for s in S if s.name in station_restriction]

V = S + O

G = Graph.Graph(V, [], name="test_graph")
G.set_distance_threshold(1000)
G.draw()

#test brute force
A = BruteForce.solve(G)
