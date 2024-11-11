from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce
from src.resolve.Progress import Progress
import pickle

from src import Graph
from src import Edge

O = olympic_parser()
S = station_parser()

#restriction are made for testing purposes

# olympic_restriction = {"Stade Tour Eiffel",
#                        "Pont d'Iéna",
#                        "Arena Champs de Mars",
#                        "Invalides"}

# station_restriction = {"Champs de Mars",
#                        "Bir Hakeim",
#                        "École Militaire",
#                        "Dupleix",
#                        "Invalides"}

# O = [o for o in O if o.name in olympic_restriction]
# S = [s for s in S if s.name in station_restriction]

V = S + O

#IMPORTANT lines to un-comment in order to calcultae the graph the first time IMPORTANT

# G = Graph.Graph(V, [], name="test_graph")
# G.set_distance_threshold(1000)

#IMPORTANT lines to un-comment in order to create the pickle of the graph the first time(create one per different graph) IMPORTANT

# with open('graph.pickle', 'wb') as file:
#     pickle.dump(G, file)

# IMPORTANT lines to comment if the pickle object of the graph is not created yet IMPORTANT
with open('graph.pickle', 'rb') as file:
    G: Graph = pickle.load(file)


intermediaire = G.goodOlympics()

nbr_good_olymp = intermediaire[0]
bad_olymp = intermediaire[1]

print("nbr bon site olympique: ", nbr_good_olymp)
for i in bad_olymp:
    print(i.__str__())

#test brute force
#brute_force_solution = BruteForce.solve(G)
progress_solution = Progress.solve(G)

# uncomment to print station belonging to solution
for s in progress_solution:
    s.belongSolution()
#     print(s.__str__())


print("solution de taille: ", len(progress_solution))

G.draw() 
