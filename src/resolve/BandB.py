from src import Graph
import folium
from tqdm import tqdm
from src.Station import Station

def ensemble_dominant(graph: Graph, S=set(), k=None, processed=None, dominated_edges=None, best_solution=None):
    """
    Recursive function to find the minimum dominating set with backtracking.
    Ensures full exploration of all possibilities to find the minimal solution.
    """
    if processed is None:
        processed = set()
    if dominated_edges is None:
        dominated_edges = set()
    if best_solution is None:
        best_solution = [None]  

    if k is not None and k == 0:
        if graph.isSolutionOfAccessibility(S):
            if best_solution[0] is None or len(S) < len(best_solution[0]):
                best_solution[0] = set(S) 
        return None

    # If S is already a valid solution, update best_solution and continue searching
    if graph.isSolutionOfAccessibility(S):
        if best_solution[0] is None or len(S) < len(best_solution[0]):
            best_solution[0] = set(S) 

    uncovered_sites = [o for o in graph.getOlympics() if not any(station in S for station in graph.get_neighbors(o))]
    if not uncovered_sites: 
        if best_solution[0] is None or len(S) < len(best_solution[0]):
            best_solution[0] = set(S)  
        return None  

    # Heuristic: Choose the uncovered site with the fewest neighbors
    u = min(uncovered_sites, key=lambda v: len(graph.get_neighbors(v)))
    processed.add(u)

    for v in graph.get_neighbors(u):
        if v not in S:
            new_dominated_edges = {edge for edge in graph.cached_edges if (edge.vertex1 == v or edge.vertex2 == v) and edge not in dominated_edges}

            if new_dominated_edges:
                new_solution = S | {v}
                dominated_edges.update(new_dominated_edges)
                if k is not None and k > 0:
                    ensemble_dominant(graph, new_solution, k - 1, processed, dominated_edges, best_solution)
                else:
                    ensemble_dominant(graph, new_solution, processed=processed, dominated_edges=dominated_edges, best_solution=best_solution)

    # Backtrack: Remove u from processed set
    processed.remove(u)

    return best_solution[0]


def remove_double_dominated_stations(graph: Graph, solution: set):
    station_dominated_edges = {}
    for station in solution:
        station_dominated_edges[station] = {
            edge for edge in graph.cached_edges if (edge.vertex1 == station or edge.vertex2 == station)
        }
    #keep only stations that have unique coverage
    refined_solution = set()
    all_dominated_edges = set()
    for station in solution:
        if not station_dominated_edges[station].issubset(all_dominated_edges):
            refined_solution.add(station)
            all_dominated_edges.update(station_dominated_edges[station])
    return refined_solution





def draw_minimum_dominating_set(graph: Graph, selected_stations):
    """
    Draws the graph using Folium, showing only the selected stations and relevant edges.
    """
    vertices = list(selected_stations) + graph.getOlympics()  # Only selected stations and Olympic sites
    lats = [v.geopoint.latitude for v in vertices]
    longs = [v.geopoint.longitude for v in vertices]
    center_point = [sum(lats) / len(lats), sum(longs) / len(longs)]

    folium_map = folium.Map(location=center_point, zoom_start=13)
    for v in vertices:
        color = 'blue' if isinstance(v, Station) else 'red'
        folium.Marker(
            location=[v.geopoint.latitude, v.geopoint.longitude],
            popup=v.name,
            icon=folium.Icon(color=color)
        ).add_to(folium_map)
    for edge in  tqdm(graph.cached_edges, desc="Drawing edges"):
        if edge.vertex1 in selected_stations and edge.vertex2 in graph.getOlympics() or \
           edge.vertex2 in selected_stations and edge.vertex1 in graph.getOlympics():
            folium.PolyLine(
                locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                           (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
                color="black",
                weight=2,
                opacity=1,
                tooltip=f"Walking time: {round(edge.weight, 2)} minutes"
            ).add_to(folium_map)

    folium_map.save("map.html")
    return folium_map
