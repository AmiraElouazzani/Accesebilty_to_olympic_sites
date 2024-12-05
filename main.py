from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce
from src.resolve.Progress import Progress
from src.Olympic import Olympic
from src.Station import Station
from src.Graph import Graph
from src.resolve.BandB import ensemble_dominant, draw_minimum_dominating_set
import pickle
import time

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

# olympic_restriction = {"Stade Tour Eiffel",
#                        "Pont d'Iéna", "Terrain des Essences - La Courneuve","Village des médias",
#                        "Arena Champs de Mars", "Stade Pierre de Coubertin","Parc des Princes",
#                        "Invalides","Hôtel de ville de Paris",
#                        "Grand Palais","Stade de la Concorde",
#                        "Invalides","Arena Paris Sud 4 (Porte de Versailles)",
#                        "Arena Paris Sud 6 (Porte de Versailles)","Arena Paris Sud 1 (Porte de Versailles)"}

# station_restriction = {"Champs de Mars","Stains La Cerisaie",
#                        "Bir Hakeim","Dugny - La Courneuve",
#                        "École Militaire","Exelmans","Issy-Val-de-Seine","Porte de Saint-Cloud",
#                        "Dupleix", "Corentin Celton","Georges Brassens","Henri Farman",
#                        "Invalides","Châtelet","Pont Neuf","Porte de Versailles"}

# O = [o for o in O if o.name in olympic_restriction]
# S = [s for s in S if s.name in station_restriction]


V = S + O

G = Graph.Graph(V, O, S, [], name="test_graph")
#IMPORTANT lines to un-comment in order to calcultae the graph the first time IMPORTANT
while True:
    try:
        print("Walking distance can be time consuming, avoid putting big values")
        x = float(input("Walking time: "))
        if x <= 0: 
            print("Please enter a positive walking time")
        elif x > 20:
            print("Please enter a smaller walking time")
        else :
            break 
    except ValueError:
        print("Please enter a valid time")
#G.set_distance_threshold(2000)
G.set_restriction_minutes(x)

#  #IMPORTANT lines to un-comment in order to create the pickle of the graph the first time(create one per different graph) IMPORTANT

with open('fullgraph.pickle', 'wb') as file:
    pickle.dump(G, file)

# IMPORTANT lines to comment if the pickle object of the graph is not created yet IMPORTANT
# with open('graph.pickle', 'rb') as file:
#     G: Graph = pickle.load(file)


intermediaire = G.goodOlympics()

nbr_good_olymp = intermediaire[0]
bad_olymp = intermediaire[1]

print("nbr bon site olympique: ", nbr_good_olymp)
for i in G.getOlympics():
    print(i.__str__())

start_time = time.time()

#brute_force_solution = BruteForce.solve(G)

solution = Progress.solve(G)

#solution = Progress.kaizen(G)

end_time = time.time()
elapsed_time = end_time - start_time

if not solution:
    print("pas de solution ou erreur")
        # uncomment to print station belonging to solution
        # print(s.__str__())
        # print(len(solution))

print("solution obtenue en ", elapsed_time, " secondes")
print("solution de taille: " + len(solution).__str__())
for i in solution:
    print(i.getname())
   
    
# for i in solution:
#     adja = i.getadja()
#     for j in adja:
#         if isinstance(j, Olympic) and isinstance(i, Station):
#             namei = i.getname()
#             namej= j.getname()
#             print(namei + " 1 " + namej)


G.draw()

#Branch and Bound

# Example usage
# solution = ensemble_dominant(G,set(), k=32)
# if solution is not None:
#     print(f"Found solution with {len(solution)} stations")
#     # These stations form a minimum dominating set
#     for station in solution:
#         print(f"Selected station: {station.name}")

#     # Visualize if needed
#     draw_minimum_dominating_set(G, solution)
# else:
#     print("No solution found")



#print("solution de taille: ", len(progress_solution))
