from src import Graph
import folium
from tqdm import tqdm
from src.Station import Station


def ensemble_dominant(graph: Graph, S=set(), k=None, processed=None, dominated_edges=None):
    """
    Recursive function to find the minimum dominating set with backtracking, ensuring no edge is doubly dominated.
    Args:
        graph: The graph instance.
        S: Current partial dominating set (set of stations).
        k: Maximum number of remaining stations to add.
        processed: Set of already processed vertices to avoid revisiting.
        dominated_edges: Set of edges that have already been dominated.
    Returns:
        A valid dominating set or None if no solution exists.
    """
    if processed is None:
        processed = set()

    if dominated_edges is None:
        dominated_edges = set()

    if k is not None and k == 0:
        if graph.isSolutionOfAccessibility(S):
            print(f"Found solution: {S}")
            return S
        return None

    # Check if the partial solution S already dominates all Olympic sites
    if graph.isSolutionOfAccessibility(S):
        print(f"Solution found with {len(S)} stations: {S}")
        return remove_double_dominated_stations(graph, S)

    # Identify undominated Olympic sites
    uncovered_sites = [o for o in graph.getOlympics() if not any(station in S for station in graph.get_neighbors(o))]
    if not uncovered_sites:  # All Olympic sites are covered
        print(f"Solution found with {len(S)} stations: {S}")
        # Final check to ensure no double domination
        return remove_double_dominated_stations(graph, S)

    #heuristic
    u = min(uncovered_sites, key=lambda v: len(graph.get_neighbors(v)))

    #avoid revisiting
    processed.add(u)

    #adding each neighbor of u to the solution set
    for v in graph.get_neighbors(u):
        if v not in S:
            # Check if adding v would dominate an edge that hasn't been dominated yet
            new_dominated_edges = {edge for edge in graph.cached_edges if (edge.vertex1 == v or edge.vertex2 == v) and edge not in dominated_edges}
            
            if new_dominated_edges:
                new_solution = S | {v}
                dominated_edges.update(new_dominated_edges)
                if k is not None and k > 0:
                    result = ensemble_dominant(graph, new_solution, k - 1, processed, dominated_edges)
                else:
                    result = ensemble_dominant(graph, new_solution, processed=processed, dominated_edges=dominated_edges)

                if result is not None:
                    return result

    # Backtrack: Remove u from processed set to allow other branches
    processed.remove(u)
    return None

def remove_double_dominated_stations(graph: Graph, solution: set):

    #track the edges dominated by each station
    station_dominated_edges = {}

    # set of dominated edges for each station
    for station in solution:
        station_dominated_edges[station] = {
            edge for edge in graph.cached_edges if (edge.vertex1 == station or edge.vertex2 == station)
        }

    #keep only stations that have unique coverage
    refined_solution = set()
    all_dominated_edges = set()

    for station in solution:
        # Check if edges of station are already covered
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

    # Plot stations and Olympic sites
    for v in vertices:
        color = 'blue' if isinstance(v, Station) else 'red'
        folium.Marker(
            location=[v.geopoint.latitude, v.geopoint.longitude],
            popup=v.name,
            icon=folium.Icon(color=color)
        ).add_to(folium_map)

    # Plot only edges in `cached_edges` connecting selected stations to Olympic sites
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
