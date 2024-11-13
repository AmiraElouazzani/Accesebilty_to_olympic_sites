from src import Graph
import folium
from tqdm import tqdm
from src.Station import Station

def ensemble_dominant(graph, partial_dominating_set=None, best_solution=None, covered_sites=None):
    """
    Recursive function to find a minimum dominating set with backtracking.
    """
    #initialisation
    if partial_dominating_set is None:
        partial_dominating_set = set()
    if best_solution is None:
        best_solution = set(graph.getStations())  # all stations are the initial best solution
    if covered_sites is None:
        covered_sites = set()  #to keep track of all the sites that are already covered by the current solution

    if len(partial_dominating_set) >= len(best_solution):     #(upper bound)
        return best_solution

    uncovered_sites = [o for o in graph.getOlympics() if o not in covered_sites]     # Find uncovered Olympic sites
    # All Olympic sites should be covered
    # update the best solution if current set is smaller
    if not uncovered_sites:
        return partial_dominating_set if len(partial_dominating_set) < len(best_solution) else best_solution
    # Select an uncovered site arbitrarily
    #could be improved by heuristic ( most neighbors - facile à couvrir , least neighbors - difficile à couvrir ... )
    u = uncovered_sites[0]
    #adding each neighboring station that can cover `u`
    for station in get_relevant_neighbors(graph, u, partial_dominating_set):
        new_partial_dominating_set = partial_dominating_set | {station}
        new_covered_sites = covered_sites | get_unique_coverage(graph, station, covered_sites)

        # Recurse with updated partial set and covered sites
        candidate_solution = ensemble_dominant(graph, new_partial_dominating_set, best_solution, new_covered_sites)

        # Update the best solution if the candidate solution is smaller
        if candidate_solution is not None and len(candidate_solution) < len(best_solution):
            best_solution = candidate_solution

    return best_solution if best_solution is not None else set()


def get_unique_coverage(graph, station, covered_sites):
    """
    Get Olympic sites that a given station covers, ensuring they are not already covered.
    """
    return {
        edge.vertex1 if edge.vertex2 == station else edge.vertex2
        for edge in graph.cached_edges
        if (edge.vertex1 == station or edge.vertex2 == station)
        and (edge.vertex1 not in covered_sites and edge.vertex2 not in covered_sites)
    }


def get_relevant_neighbors(graph, olympic_site, partial_dominating_set):
    """
    Get relevant neighboring stations of an Olympic site within the distance threshold,
    excluding stations already in the partial solution.
    """
    relevant_neighbors = set()

    # For each edge involving the Olympic site, find its neighboring stations that are not yet in the partial dominating set
    for edge in graph.cached_edges:
        if (edge.vertex1 == olympic_site or edge.vertex2 == olympic_site):
            neighbor = edge.vertex1 if edge.vertex2 == olympic_site else edge.vertex2
            if neighbor not in partial_dominating_set:
                relevant_neighbors.add(neighbor)

    return relevant_neighbors


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
