from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce
from src.resolve.Progress import Progress
from src.resolve.BandB import ensemble_dominant, draw_minimum_dominating_set
from utils import *

def main():
    O = olympic_parser()
    S = station_parser()
    V = S + O

    x = get_walking_time()
    G = load_graph(x, filename="processed_graph.pkl")

    if not G:
        G = load_or_create_graph(V, O, S)
        G.usefull_edges_time(x)
        save_graph(G, x)  # Save graph with the current x


    # Analyze "good" and "bad" Olympic sites
    intermediaire = G.goodOlympics()
    nbr_good_olymp = intermediaire[0]
    bad_olymp = intermediaire[1]

    print(f"Number of good Olympic sites: {nbr_good_olymp}")
    if bad_olymp:
        print("Details of bad Olympic sites:")
        for i in bad_olymp:
            print(i.__str__())

    method = choose_method()
    solution = None
    if method == '1':
        print("Running Brute Force...")
        solution = BruteForce.solve(G)
        G.draw()
    elif method == '2':
        print("Running Progress...")
        solution = Progress.solve(G)
        G.draw()
        if not solution:
            print("No solution found or an error occurred.")
        else:
            print(f"Solution size: {len(solution)}")
            for i in solution:
                print(i.getname())

    if method == '3':
        print("Running Branch and Bound...")
        solution = ensemble_dominant(G, set(), k=32)

        if not solution:
            print("No valid solution found by Branch and Bound.")
        else:
            print(f"Solution size: {len(solution)}")
            print(f"Solution stations: {[station.name for station in solution]}")
            draw_minimum_dominating_set(G, solution)

    print("Graph has been drawn and saved to 'map.html'.")
    clear_osmnx_cache()

if __name__ == "__main__":
    main()
