import tqdm
from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce
from src.resolve.Progress import Progress
from src.resolve.BandB import ensemble_dominant, draw_minimum_dominating_set
from utils import *
import time
import matplotlib.pyplot as plt


class Benchmark:
    def __init__(self):
        pass

    def setup(self):
        O = olympic_parser()
        S = station_parser()
        V = S + O

        self.x = get_walking_time()
        self.G = load_graph(self.x, filename="processed_graph.pkl")

        if not self.G:
            self.G = load_or_create_graph(V, O, S)
            self.G.usefull_edges_time(self.x)
            save_graph(self.G, self.x)
        
        # Analyze "good" and "bad" Olympic sites
        intermediaire = self.G.goodOlympics()
        nbr_good_olymp = intermediaire[0]
        bad_olymp = intermediaire[1]

        print(f"Number of good Olympic sites: {nbr_good_olymp}")
        if bad_olymp:
            print("Details of bad Olympic sites:")
            for i in bad_olymp:
                print(i.__str__())    


    def run(self):
        iterations = int(input("Enter the number of iterations: "))
        print("Starting benchmark...")

        # Progress
        print("Running Progress...")
        total_time = 0
        for i in tqdm.tqdm(range(iterations), desc="Progress"):
            start_time = time.time()
            solution = Progress.solve(self.G)
            end_time = time.time()
            iteration_time = end_time - start_time
            total_time += iteration_time

        average_time_progress = total_time / iterations

        # Branch and Bound
        print("Running Branch and Bound...")
        total_time = 0  
        for i in tqdm.tqdm(range(iterations), desc="Branch and Bound"):
            start_time = time.time()
            solution = ensemble_dominant(self.G, set(), k=32)
            end_time = time.time()
            iteration_time = end_time - start_time
            total_time += iteration_time

        average_time_bab = total_time / iterations


        print("Benchmark complete.")
        print("Size of the graph: ", len(self.G.vertices), "vertices and ", len(self.G.edges), "edges")
        print("walking time: ", self.x, "minutes")
        print(f"Average time per iteration for progress: {average_time_progress:.4f} seconds")
        print(f"Average time per iteration for branch and bound: {average_time_bab:.4f} seconds")
        # Print bar chart in terminal

        labels = ['Progress', 'Branch and Bound']
        times = [average_time_progress, average_time_bab]

        plt.bar(labels, times, color=['blue', 'green'])
        plt.xlabel('Algorithm')
        plt.ylabel('Average Time (seconds)')
        plt.title('Benchmark Results')
        plt.show()

if __name__ == "__main__":
    bm = Benchmark()
    bm.setup()
    bm.run()