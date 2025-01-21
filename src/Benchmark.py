import tqdm
from src.parser.olympic_parser import olympic_parser
from src.parser.station_parser import station_parser
from src.resolve.BruteForce import BruteForce
from src.resolve.Progress import Progress
from src.resolve.BandB import ensemble_dominant, draw_minimum_dominating_set
from utils import *
import time
import csv
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

        intermediaire = self.G.goodOlympics()
        nbr_good_olymp, bad_olymp = intermediaire

        self.console.print(f"[green]Number of good Olympic sites:[/green] {nbr_good_olymp}")
        if bad_olymp:
            self.console.print("[red]Details of bad Olympic sites:[/red]")
            for site in bad_olymp:
                self.console.print(site.__str__())

    def print_bar_chart(self, labels, times, max_width=40):
        max_time = max((t for t in times if t != -1), default=1)
        scale = max_width / max_time if max_time > 0 else 1
        fastest_time = min((t for t in times if t != -1), default=max_time)

        for label, time in zip(labels, times):
            if time == -1:
                bar = "X".center(max_width)
                color = "yellow"
                yield f"{label:>16}: [{color}]{bar}[/] N/A seconds"
            else:
                bar_width = int(time * scale)
                bar = "█" * bar_width
                color = "green" if time == fastest_time else "red"
                yield f"{label:>16}: [{color}]{bar.ljust(max_width)}[/] {time:.4f} seconds"

    def save_results_to_csv(self, results, filename="benchmark_results.csv"):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["number of vertices", "Progress", "Branch and Bound", "Brute Force"])
            for result in results:
                writer.writerow([
                    result["vertices"],
                    result["average_time_progress"],
                    result["average_time_bab"],
                    result.get("average_time_bf", "N/A")
                ])

    def print_every_result(self, results):
        for result in results:
            self.console.print("\n[bold]Graph Results:[/bold]", justify="left")
            self.console.print(f"Vertices: {result['vertices']} | Edges: {result['edges']} | Walking Time: {result['walking_time']} min")

            bars = list(self.print_bar_chart(
                ["Progress", "Branch and Bound", "Brute Force"],
                [result['average_time_progress'], result['average_time_bab'], result.get('average_time_bf', -1)]
            ))

            for bar in bars:
                self.console.print(bar)

            self.console.print("\n" + "=" * 40 + "\n")

    def runAll(self):
        try:
            iterations = int(input("Enter the number of iterations: "))
        except ValueError:
            self.console.print("[red]Invalid number of iterations.[/red]")
            return

        self.console.print("[bold yellow]Starting benchmark...[/bold yellow]")
        results = []

        i = 1
        peel_nb = 10
        while len(self.G.vertices) > peel_nb:
            self.console.print(f"\n[bold]Running benchmark for graph {i}...[/bold]")
            result = self.run(iterations, brute_force=(len(self.G.vertices) < 100))
            results.append(result)
            self.G.random_peel(peel_nb)
            i += 1

        self.print_every_result(results)
        self.save_results_to_csv(results)

    def run(self, iterations, brute_force=False):
        def measure_time(label, function, *args):
            total_time = 0
            exception_raised = False

            for _ in track(range(iterations), description=label):
                try:
                    start_time = time.time()
                    function(*args)
                    total_time += time.time() - start_time
                except Exception as e:
                    self.console.print(f"[red]{label} failed with error: {e}[/red]")
                    exception_raised = True
                    break

            return -1 if exception_raised else total_time / iterations

        average_time_progress = measure_time("Progress", Progress.solve, self.G)
        average_time_bab = measure_time("Branch and Bound", ensemble_dominant, self.G, set(), 32)

        average_time_bf = -1
        if brute_force:
            average_time_bf = measure_time("Brute Force", BruteForce.solve, self.G)

        result = {
            "vertices": len(self.G.vertices),
            "edges": len(self.G.edges),
            "walking_time": self.x,
            "average_time_progress": average_time_progress,
            "average_time_bab": average_time_bab
        }

        if brute_force:
            result["average_time_bf"] = average_time_bf

        return result

if __name__ == "__main__":
    bm = Benchmark()
    bm.setup()
    bm.runAll()
