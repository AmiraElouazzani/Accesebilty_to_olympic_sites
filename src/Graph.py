from .Edge import Edge
from .Vertex import Vertex
from .Station import Station
from .Olympic import Olympic
from tqdm import tqdm
import folium
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic

class Graph:
    def __init__(self, vertices: list[Vertex], edges: list[Edge] = [], name="default_name"):
        self.vertices = vertices
        self.olympics = self.getOlympics()
        self.progressOlympics = []
        self.stations = self.getStations()
        self.edges = edges
        self.cached_edges = []

    #a set is Solution of Accessibility if it dominates the subgraph of Olympic sites
    #this function checks the vincinity of a potential solution A
    #if all olympic sites are in the vincinity of A, then A is a solution of Accessibility
    def isSolutionOfAccessibility(self, A):
        visited = set()
        for a in A:
            visited = visited.union(self.get_neighbors(a))
        return (set(self.olympics).issubset(visited))
    
    def are_adjacent(self, v1 : Vertex, v2 : Vertex):
        for e in self.edges:
            if (e.vertex1 == v1 and e.vertex2 == v2) or (e.vertex1 == v2 and e.vertex2 == v1):
                return True
        return False

    def get_neighbors(self, v : Vertex):
        neighbors = set()
        for e in self.edges:
            if e.vertex1 == v:
                neighbors.add(e.vertex2)
            if e.vertex2 == v:
                neighbors.add(e.vertex1)
        return neighbors

    def getStations(self):
        if(not hasattr(self, "stations")):
            self.stations = []
            for v in self.vertices:
                if isinstance(v, Station):
                    self.stations.append(v)
        return self.stations

    def getOlympics(self):
        if(not hasattr(self, "olympics")):
            self.olympics = []
            for v in self.vertices:
                if isinstance(v, Olympic):
                    self.olympics.append(v)
        return self.olympics
    
    def changeOlympics(self, new_olympics):

        self.olympics = new_olympics
    
    def goodOlympics(self):

        good_olympics =[]
        bad_olympics =[]
        for olymp in self.getOlympics():

            if self.get_neighbors(olymp):
                good_olympics.append(olymp)
            else:
                bad_olympics.append(olymp)

        self.changeOlympics(good_olympics)

        return (len(good_olympics), bad_olympics)
    
    def getprogressOlympics(self):
        
        #print(self.progressOlympics)
       # progressolympics = self.progressOlympics
        return self.progressOlympics

    def addprogressOlympics(self, newOlympics):
        self.progressOlympics.append(newOlympics)
                
    
    def calculate_edges(self, distance_threshold: float):
        """Calculate and cache edges between vertices based on walking paths."""
        self.cached_edges = []  
        existing_edges = set()  # Set to store edges to prevent duplicates

        # Get the road network (walking) for the area
        # This uses the coordinates of the vertices to get the network for the area
        graph_center = (
            sum(v.geopoint.latitude for v in self.vertices) / len(self.vertices),
            sum(v.geopoint.longitude for v in self.vertices) / len(self.vertices)
        )
        
        # Retrieve a walking network from OpenStreetMap for the area around the center point
        G = ox.graph_from_point(graph_center, dist=distance_threshold, network_type='walk')

        # tqdm for progress bar
        for i, v1 in tqdm(enumerate(self.vertices), total=len(self.vertices), desc="Calculating edges"):
            for j, v2 in enumerate(self.vertices):
                if i != j and not (isinstance(v1, Olympic) and isinstance(v2, Olympic)): 
                        # Find the nearest nodes in the OSM network for each vertex
                        try:
                            distance = geodesic(
                                (v1.geopoint.latitude, v1.geopoint.longitude),
                                (v2.geopoint.latitude, v2.geopoint.longitude)
                            ).meters

                            if distance <= distance_threshold:

                                origin_node = ox.distance.nearest_nodes(G, v1.geopoint.longitude, v1.geopoint.latitude)
                                destination_node = ox.distance.nearest_nodes(G, v2.geopoint.longitude, v2.geopoint.latitude)
                                walking_distance = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
                            
                                if walking_distance <= distance_threshold : 
                                    walking_time = Edge.walking_time_from_distance(walking_distance)
                                    edge_pair = (v1, v2)
                                    reverse_edge_pair = (v2, v1)
                                    if edge_pair not in existing_edges and reverse_edge_pair not in existing_edges: # Check if the edge or its reverse already exists
                                        # Create the edge with walking time as the weight
                                        edge = Edge(v1, v2, walking_time)
                                        self.cached_edges.append(edge)
                                        self.edges.append(edge)
                                        existing_edges.add(edge_pair)  
                        except Exception as e:
                            print(f"Error calculating path between {v1.name} and {v2.name}: {e}")


    def verify_station_olympic_link(self):
        """Check that at least one station is linked to an Olympic site."""
        station_to_olympic = False

        for edge in self.cached_edges:
            if isinstance(edge.vertex1, Station) and isinstance(edge.vertex2, Olympic):
                print(f"Station {edge.vertex1.name} is linked to Olympic site {edge.vertex2.name} with distance {edge.weight}")
                station_to_olympic = True
                break
            elif isinstance(edge.vertex1, Olympic) and isinstance(edge.vertex2, Station):
                print(f"Olympic site {edge.vertex1.name} is linked to Station {edge.vertex2.name} with distance {edge.weight}")
                station_to_olympic = True
                break

        if not station_to_olympic:
            print("No stations are linked to Olympic sites. Please check the distance threshold or data.")

    def draw(self):
        """Draw the graph using Folium instead of Matplotlib, showing walking time (weight) on edges."""
        if not self.vertices:
            print("No vertices to draw.")
            return

        # Initialize a folium map centered at the average point of the vertices
        lats = [v.geopoint.latitude for v in self.vertices]
        longs = [v.geopoint.longitude for v in self.vertices]
        center_point = [sum(lats) / len(lats), sum(longs) / len(longs)]

        # Create a folium map
        folium_map = folium.Map(location=center_point, zoom_start=13)

        # Plot vertices as markers on the map
        for v in self.vertices:
             
            if isinstance(v, Station):
                
                if v.getSolution():
                    color = 'green'
                    
                else:
                    color = 'blue'
                
            else:
                color = 'red'
            
            v.set_color(color)
            
            if(color in('red', 'green')): # verify that the vertex is an olympic site or a station to modify
                folium.Marker(
                    location=[v.geopoint.latitude, v.geopoint.longitude],
                    popup=v.name,
                    icon=folium.Icon(color=color)
                ).add_to(folium_map)

        # Plot edges as lines with walking time
        for edge in tqdm(self.cached_edges, desc="Drawing edges"):

            if(edge.vertex1.get_color() in('red', 'green') and edge.vertex2.get_color() in('red', 'green')): #verify if the edge connect an olympic site to a station to modify
                folium.PolyLine(
                    locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                            (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
                    color="black",
                    weight=2,
                    opacity=1,
                    tooltip=f"Walking time: {round(edge.weight, 2)} minutes"  # Display walking time as tooltip
                ).add_to(folium_map)

        folium_map.save("map.html")  
        return folium_map 

    def set_distance_threshold(self, distance_threshold: float):
        """Set distance threshold and calculate edges based on it."""
        self.calculate_edges(distance_threshold)