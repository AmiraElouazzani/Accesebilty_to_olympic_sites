from .Edge import Edge
from .Vertex import Vertex
from .Station import Station
from .Olympic import Olympic
from tqdm import tqdm
import folium
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
from bitarray import bitarray
from bitarray.util import ba2int, subset, zeros
ox.settings.timeout = 180  
ox.settings.overpass_rate_limit = True
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"
class Graph:
    def __init__(self, vertices: list[Vertex], olympics: list[Olympic], stations: list[Station], edges: list[Edge] = [], name="default_name"):
        self.vertices = vertices
        self.olympics = olympics
        self.progressOlympics = []
        self.stations = stations
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
        neighbors = v.getadja()
        
        return neighbors
    
    def has_neighbours_station(self,v: Vertex):
        neighbors = v.getadja()

        if neighbors != False:
            for ver in neighbors:
                if isinstance(ver, Station):
                    return True
       
        return False


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

            if self.has_neighbours_station(olymp):
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
    
    def usefull_edges_time(self, minutes_de_marches):
        """
        Calculate edges between stations and Olympic sites based on a double threshold:
        1. Geodesic distance filter.
        2. Walking distance using `osmnx`.
        """
        walking_speed = 75  # Meters per minute
        geodesic_threshold = walking_speed * minutes_de_marches  # Max geodesic distance in meters

        olympics = self.getOlympics()
        stations = self.getStations()
        for olymp in tqdm(olympics, desc="Processing Olympic sites"):
            # Create a walking network graph for each Olympic site
            G = ox.graph_from_point(
                (olymp.geopoint.latitude, olymp.geopoint.longitude),
                dist=geodesic_threshold,
                network_type='walk'
            )

            for station in stations:
                # Step 1: Geodesic distance filter
                geodesic_distance = geodesic(
                    (station.geopoint.latitude, station.geopoint.longitude),
                    (olymp.geopoint.latitude, olymp.geopoint.longitude)
                ).meters

                if geodesic_distance > geodesic_threshold:
                    continue  # Skip if outside the geodesic threshold

                try:
                    # Step 2: Walking distance filter using `osmnx`
                    origin_node = ox.distance.nearest_nodes(G, station.geopoint.longitude, station.geopoint.latitude)
                    destination_node = ox.distance.nearest_nodes(G, olymp.geopoint.longitude, olymp.geopoint.latitude)
                    walking_distance = nx.shortest_path_length(G, origin_node, destination_node, weight='length')

                    if walking_distance <= geodesic_threshold:
                        # Calculate walking time and create edge
                        walking_time = walking_distance / walking_speed
                        edge = Edge(station, olymp, walking_time)
                        self.edges.append(edge)
                        self.cached_edges.append(edge) 
                        station.addadja(olymp)
                        olymp.addadja(station)

                except (nx.NetworkXNoPath, KeyError):
                    # Skip if no valid walking path exists
                    continue




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
                    v.set_color(color)
                
                else:
                    color = 'blue'
                    v.set_color(color)
                    
            else:
                color = 'red'
                v.set_color(color)
                
            
            #  color in('red', 'green', 'blue')
            
            if(isinstance(v, Olympic)): # verify that the vertex is an olympic site or a station to modify
                folium.Marker(
                    location=[v.geopoint.latitude, v.geopoint.longitude],
                    popup=v.name,
                    icon=folium.Icon(color=color)
                ).add_to(folium_map)
            elif(isinstance(v, Station)):
                if(v.getSolution()):

                    folium.Marker(
                        location=[v.geopoint.latitude, v.geopoint.longitude],
                        popup=v.name,
                        icon=folium.Icon(color=color)
                    ).add_to(folium_map)


        # Plot edges as lines with walking time
        for edge in tqdm(self.cached_edges, desc="Drawing edges"):

            # what to put in the if() in order to print all stations: (edge.vertex1.get_color() in('red', 'blue') and edge.vertex2.get_color() in('red', 'blue')) or (edge.vertex1.get_color() in('red', 'green') and edge.vertex2.get_color() in('red', 'green'))
            # what to put in the if() in order to print only solution stations: (edge.vertex1.get_color() in('red', 'green') and edge.vertex2.get_color() in('red', 'green'))
            if((edge.vertex1.get_color() in('red', 'green') and edge.vertex2.get_color() in('red', 'green'))): #verify if the edge connect an olympic site to a station to modify
                total_seconds = round(edge.weight * 60)  # Convert minutes to total seconds
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                #print(f"Drawing edge between {edge.vertex1.name} and {edge.vertex2.name} with color {edge.vertex1.get_color()}")
                folium.PolyLine(
                    locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                            (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
                    color="black",
                    weight=2,
                    opacity=1,
                    tooltip=f"Walking time: {minutes} mins {seconds} secs"  # Updated tooltip format
                                                ).add_to(folium_map)

        folium_map.save("map.html")  
        return folium_map 

    
    def set_restriction_minutes(self,minutes_de_marches):

        self.usefull_edges_time(minutes_de_marches)
    
    def makeprofile(self, station: Station):
        olympics = self.getOlympics()
        profile_index = 0
        copy = zeros(len(olympics))

        for olymp in olympics:
            if station.isadja(olymp):
                copy[profile_index]=1
            profile_index +=1
        station.setprofile(copy)
    
    def makeprofiles(self):
        stations = self.getStations()
        for stat in stations:
            self.makeprofile(stat)
