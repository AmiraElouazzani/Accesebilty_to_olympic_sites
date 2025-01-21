import os
import pickle
from src.Graph import Graph


def get_walking_time():
    """Prompt the user for a valid walking time in minutes."""
    while True:
        try:
            print("Walking distance can be time consuming, avoid putting big values")
            x = float(input("Enter walking time in minutes: "))
            if x <= 0:
                print("Please enter a positive walking time.")
            elif x > 20:
                print("Please enter a smaller walking time.")
            else:
                return x
        except ValueError:
            print("Invalid input. Please enter a number.")

def choose_method():
    """Prompt the user to choose a method for solving."""
    print("\nSelect a solution method:")
    print("1. Brute Force")
    print("2. Progress")
    print("3. Branch and Bound")
    while True:
        method = input("Enter your choice (1/2/3): ").strip()
        if method in {'1', '2', '3'}:
            return method
        print("Invalid choice. Please enter 1, 2, or 3.")

def load_or_create_graph(vertices, olympics, stations, graph_file='fullgraph.pickle'):
    """
    Handle loading or creating a graph with pickle.
    
    Parameters:
        vertices (list): Combined list of stations and Olympics.
        olympics (list): List of Olympic sites.
        stations (list): List of stations.
        graph_file (str): Path to the pickle file for saving/loading the graph.
    
    Returns:
        Graph: The graph object.
    """
    if os.path.exists(graph_file):
        regenerate = input("Do you want to regenerate the graph? (yes/no): ").strip().lower() == 'yes'
        if regenerate:
            # Create a new graph
            G = Graph(vertices, olympics, stations, [], name="test_graph")
            with open(graph_file, 'wb') as file:
                pickle.dump(G, file)
            print(f"Graph regenerated and saved to {graph_file}.")
        else:
            # Load the graph from the pickle file
            with open(graph_file, 'rb') as file:
                G = pickle.load(file)
            print(f"Graph loaded from {graph_file}.")
    else:
        # Create a new graph if no pickle file exists
        print("No existing graph found. Creating a new graph...")
        G = Graph(vertices, olympics, stations, [], name="test_graph")
        with open(graph_file, 'wb') as file:
            pickle.dump(G, file)
        print(f"Graph saved to {graph_file}.")
    return G

def clear_osmnx_cache():
    """
    Clear the OSMnx cache folder to remove temporary files created during processing.
    """
    import shutil
    import osmnx as ox

    cache_dir = ox.settings.cache_folder
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"Cleared OSMnx cache at: {cache_dir}")


import pickle

def save_graph(graph, x, filename="processed_graph.pkl"):
    with open(filename, "wb") as f:
        pickle.dump({"graph": graph, "x": x}, f)
    print(f"Graph and walking time ({x} minutes) saved to {filename}.")

def load_graph(x, filename="processed_graph.pkl"):
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            saved_x = data["x"]
            graph = data["graph"]

            if saved_x == x:
                print(f"Graph with walking time ({x} minutes) loaded from {filename}.")
                return graph
            else:
                print(f"Saved graph uses walking time ({saved_x} minutes), not {x}. Recalculating.")
                return None
    except FileNotFoundError:
        print(f"No saved graph found. Proceeding with fresh calculations.")
        return None


def load_graph(x, filename="processed_graph.pkl"):
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            saved_x = data["x"]
            graph = data["graph"]

            if saved_x == x:
                print(f"Graph with walking time ({x} minutes) loaded from {filename}.")
                return graph
            else:
                print(f"Saved graph uses walking time ({saved_x} minutes), not {x}. Recalculating.")
                return None
    except FileNotFoundError:
        print(f"No saved graph found. Proceeding with fresh calculations.")
        return None


#restriction are made for testing purposes

# olympic_restriction = {"Stade Tour Eiffel",
#                        "Pont d'Iéna",
#                        "Arena Champs de Mars",
#                        "Invalides"}

# station_restriction = {"Champs de Mars",
#                        "Bir Hakeim",
#                        "École Militaire",
#                        "Dupleix",
#                        "Invalides"}

# O = [o for o in O if o.name in olympic_restriction]
# S = [s for s in S if s.name in station_restriction]

# olympic_restriction = {"Stade Tour Eiffel",
#                        "Pont d'Iéna", "Terrain des Essences - La Courneuve","Village des médias",
#                        "Arena Champs de Mars", "Stade Pierre de Coubertin","Parc des Princes",
#                        "Invalides","Hôtel de ville de Paris",
#                        "Grand Palais","Stade de la Concorde",
#                        "Invalides","Arena Paris Sud 4 (Porte de Versailles)",
#                        "Arena Paris Sud 6 (Porte de Versailles)","Arena Paris Sud 1 (Porte de Versailles)"}

# station_restriction = {"Champs de Mars","Stains La Cerisaie",
#                        "Bir Hakeim","Dugny - La Courneuve",
#                        "École Militaire","Exelmans","Issy-Val-de-Seine","Porte de Saint-Cloud",
#                        "Dupleix", "Corentin Celton","Georges Brassens","Henri Farman",
#                        "Invalides","Châtelet","Pont Neuf","Porte de Versailles"}

# O = [o for o in O if o.name in olympic_restriction]
# S = [s for s in S if s.name in station_restriction]
