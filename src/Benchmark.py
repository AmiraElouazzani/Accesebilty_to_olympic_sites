import tqdm
from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce
from src.resolve.Progress import Progress
from src.resolve.BandB import ensemble_dominant, draw_minimum_dominating_set
from utils import *
import time
from rich.console import Console
from rich.progress import track
from rich.text import Text

class Benchmark:
    def __init__(self):
        self.console = Console()

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

        self.console.print(f"[green]Number of good Olympic sites:[/green] {nbr_good_olymp}")
        if bad_olymp:
            self.console.print("[red]Details of bad Olympic sites:[/red]")
            for i in bad_olymp:
                self.console.print(i.__str__())    

    def print_bar_chart(self, labels, times, max_width=40):
        max_time = max(times)
        scale = max_width / max_time
        fastest_time = min(times)
        aligned_width = max_width + 10  # Extra padding for alignment

        for label, time in zip(labels, times):
            bar_width = int(time * scale)
            bar = "█" * bar_width
            color = "green" if time == fastest_time else "red"
            yield f"{label:>16}: [{color}]{bar.ljust(max_width)}[/] {time:.4f} seconds".ljust(aligned_width)

    def print_every_result(self, results):
        for result in results:
            self.console.print("\n[bold]Graph Results:[/bold]", justify="left")
            self.console.print(f"Vertices: {result['vertices']} | Edges: {result['edges']} | Walking Time: {result['walking_time']} min")

            bars = list(self.print_bar_chart(
                ["Progress", "Branch and Bound"],
                [result['average_time_progress'], result['average_time_bab']]
            ))

            for bar in bars:
                self.console.print(bar)

            self.console.print("\n" + "=" * 40 + "\n")

    def runAll(self, nb_different_graphs=2):
        iterations = int(input("Enter the number of iterations: "))
        self.console.print("[bold yellow]Starting benchmark...[/bold yellow]")
        results = []

        for i in range(nb_different_graphs):
            self.console.print(f"\n[bold]Running benchmark for graph {i + 1}...[/bold]")
            result = self.run(iterations)
            results.append(result)

        self.print_every_result(results)

    def run(self, iterations):
        # Progress
        self.console.print("[cyan]Running Progress...[/cyan]")
        total_time = 0
        for _ in track(range(iterations), description="Progress"):
            start_time = time.time()
            solution = Progress.solve(self.G)
            end_time = time.time()
            iteration_time = end_time - start_time
            total_time += iteration_time

        average_time_progress = total_time / iterations

        # Branch and Bound
        self.console.print("[cyan]Running Branch and Bound...[/cyan]")
        total_time = 0  
        for _ in track(range(iterations), description="Branch and Bound"):
            start_time = time.time()
            solution = ensemble_dominant(self.G, set(), k=32)
            end_time = time.time()
            iteration_time = end_time - start_time
            total_time += iteration_time

        average_time_bab = total_time / iterations

        self.console.print("\n[green bold]Benchmark complete.[/green bold]")
        self.console.print(f"Size of the graph: {len(self.G.vertices)} vertices and {len(self.G.edges)} edges")
        self.console.print(f"Walking time: {self.x} minutes")
        self.console.print(f"[blue]Average time per iteration for Progress:[/blue] {average_time_progress:.4f} seconds")
        self.console.print(f"[green]Average time per iteration for Branch and Bound:[/green] {average_time_bab:.4f} seconds")

        return {
            "vertices": len(self.G.vertices),
            "edges": len(self.G.edges),
            "walking_time": self.x,
            "average_time_progress": average_time_progress,
            "average_time_bab": average_time_bab,
        }

if __name__ == "__main__":
    bm = Benchmark()
    bm.setup()
    bm.runAll()
