import itertools
from tqdm import tqdm


#INPUT : A graph G of Olympics and Stations
#OUTPUT : A substet of the graph's vertices that are a solution of ACCESSIBILITY
# ie : a dominant set of  G's vertices, only composed of Stations

from ..Graph import Graph
from ..Station import Station
from ..Olympic import Olympic

class BruteForce:

    @staticmethod
    def solve(G:Graph):

        stations = G.getStations()
        olympics = G.getOlympics()

        #First it is easy to check if no solution exists
        for o in olympics:
            if not G.get_neighbors(o):
                print("No solution found")
                return False

        #Main loop over the number of vertices we try to include in the solution
        #Basically we will try every 1 sized solutions, 2 sized_solution ... 
        #until G.nOlympic sized solutions
        #We don't try until G.nStations sized solutions because we know that if we can't find a
        #solution with G.nOlympic vertices, we won't be able to find one with G.nStations vertices
        #complexity is 0(2^G.nOlympic) (verification of each certificate)
        for i in tqdm(range(len(G.vertices)-len(stations)), desc="Brute force computation"):
            r = BruteForce.solve_for_i_stations(stations, len(stations), i, G)
            if(r):
                return r
            
        print("No solution found")
        return False

    @staticmethod
    def solve_for_i_stations(stations, n, i, G):
        #every possible sublist of i elements
        combinations = itertools.combinations(range(n),i)

        for combo in combinations:
            certificate = [stations[k] for k in combo]

            if(G.isSolutionOfAccessibility(certificate)):
                return certificate
        return False
        