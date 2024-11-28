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

    # Base case: If k == 0, check if S is a valid solution
    if k is not None and k == 0:
        if graph.isSolutionOfAccessibility(S):
            print(f"Found solution: {S}")
            return S
        return None

    # Check if the partial solution S already dominates all Olympic sites
    if graph.isSolutionOfAccessibility(S):
        print(f"Solution found with {len(S)} stations: {S}")
        # Final check to ensure no double domination
        return remove_double_dominated_stations(graph, S)

    # Identify undominated Olympic sites
    uncovered_sites = [o for o in graph.getOlympics() if not any(station in S for station in graph.get_neighbors(o))]
    if not uncovered_sites:  # All Olympic sites are covered
        print(f"Solution found with {len(S)} stations: {S}")
        # Final check to ensure no double domination
        return remove_double_dominated_stations(graph, S)

    # Choose a vertex with the minimum degree among the uncovered vertices
    u = min(uncovered_sites, key=lambda v: len(graph.get_neighbors(v)))

    # Add u to the processed set to avoid revisiting
    processed.add(u)

    # Recursively try adding each neighbor of u to the solution set
    for v in graph.get_neighbors(u):
        if v not in S:
            # Check if adding v would dominate an edge that hasn't been dominated yet
            new_dominated_edges = {edge for edge in graph.cached_edges if (edge.vertex1 == v or edge.vertex2 == v) and edge not in dominated_edges}
            
            if new_dominated_edges:
                new_solution = S | {v}
                # Update the set of dominated edges
                dominated_edges.update(new_dominated_edges)

                # Avoid exploring branches where k is zero or negative
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
    """
    Removes redundant stations from the solution that contribute to double domination.
    Args:
        graph: The graph instance.
        solution: The current solution set of stations.
    Returns:
        A refined solution set where each edge is only dominated once.
    """
    # Create a set to track edges already dominated
    dominated_edges = set()
    refined_solution = set()

    for station in solution:
        # Check if adding this station results in dominating any edge not already dominated
        new_dominated_edges = {edge for edge in graph.cached_edges if (edge.vertex1 == station or edge.vertex2 == station) and edge not in dominated_edges}
        
        if new_dominated_edges:
            # Add the station if it covers new edges
            refined_solution.add(station)
            # Mark these edges as dominated
            dominated_edges.update(new_dominated_edges)

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
