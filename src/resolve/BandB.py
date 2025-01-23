from src.Graph2 import Graph
import folium
from tqdm import tqdm
from src.Station import Station

def ensemble_dominant(graph: Graph, S=set(), k=None, processed=None, dominated_edges=None, best_solution=None, visited_states=None):
    """
    Recursive function to find the minimum dominating set with backtracking.
    Fully explores the solution space and compares sizes to ensure minimal solution.
    """
    if processed is None:
        processed = set()
    if dominated_edges is None:
        dominated_edges = set()
    if best_solution is None:
        best_solution = [None]
    if visited_states is None:
        visited_states = set()

    # Efficient termination: If current solution is worse than best solution, stop exploring
    if best_solution[0] is not None and len(S) >= len(best_solution[0]):
        return

    # If this is a valid solution, compare and potentially update the best solution
    if graph.isSolutionOfAccessibility(S):
        if best_solution[0] is None or len(S) < len(best_solution[0]):
            best_solution[0] = set(S)

    # Identify uncovered Olympic sites
    uncovered_sites = [o for o in graph.getOlympics() if not any(station in S for station in graph.get_neighbors(o))]
    if not uncovered_sites:
        # If all sites are covered, check if this solution is minimal
        if best_solution[0] is None or len(S) < len(best_solution[0]):
            best_solution[0] = set(S)
        return

    # Heuristic: Explore stations that cover uncovered sites (still general)
    u = min(uncovered_sites, key=lambda v: len(graph.get_neighbors(v)))
    processed.add(u)

    # Try adding neighbors of uncovered sites to the solution
    for v in graph.get_neighbors(u):
        if v not in S:
            new_solution = S | {v}
            ensemble_dominant(graph, new_solution, k, processed, dominated_edges, best_solution, visited_states)

    # Backtrack by removing `u` from the processed set
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
            walking_time_minutes = int(edge.weight)
            walking_time_seconds = int((edge.weight - walking_time_minutes) * 60)
            walking_time_str = f"{walking_time_minutes} minutes {walking_time_seconds} seconds"

            folium.PolyLine(
                locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                           (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
                color="black",
                weight=2,
                opacity=1,
                tooltip=f"Walking time: {walking_time_str}").add_to(folium_map)

    folium_map.save("map.html")
    return folium_map
