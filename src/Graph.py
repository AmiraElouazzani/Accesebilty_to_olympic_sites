from .Edge import Edge
from .Vertex import Vertex
from .Station import Station
from .Olympic import Olympic
from geopy.distance import geodesic
from tqdm import tqdm
import folium
from shapely.geometry import LineString

class Graph:
    def __init__(self, vertices: list[Vertex], edges: list[Edge] = [], name="default_name"):
        self.vertices = vertices
        self.edges = edges
        self.cached_edges = []

    def isStation(self,vertex): 
        isinstance(vertex, Station)

    def isOlympic(self,vertex):
        isinstance(vertex, Olympic)

    def calculate_edges(self, distance_threshold: float):
        """Calculate and cache edges between vertices based on distance."""
        self.cached_edges = []  # Clear previous edges

        # Use tqdm to show progress

        for i, v1 in tqdm(enumerate(self.vertices), total=len(self.vertices), desc="Calculating edges"):
            for j, v2 in enumerate(self.vertices):
                if i != j and (self.isOlympic(v1) == self.isStation(v2))  :
                    distance = geodesic(
                        (v1.geopoint.latitude, v1.geopoint.longitude),
                        (v2.geopoint.latitude, v2.geopoint.longitude)
                    ).meters
                    if distance <= distance_threshold:
                        edge = Edge(v1, v2, distance)
                        self.cached_edges.append(edge)

        # Verification step
        self.verify_station_olympic_link()

    def verify_station_olympic_link(self):
        """Check that at least one station is linked to an Olympic site."""
        station_to_olympic = False

        for edge in self.cached_edges:
            if self.isStation(edge.vertex1) and self.isOlympic(edge.vertex2):
                print(f"Station {edge.vertex1.name} is linked to Olympic site {edge.vertex2.name} with distance {edge.weight}")
                station_to_olympic = True
                break
            elif self.isOlympic(edge.vertex1) and self.isStation(edge.vertex2):
                print(f"Olympic site {edge.vertex1.name} is linked to Station {edge.vertex2.name} with distance {edge.weight}")
                station_to_olympic = True
                break

        if not station_to_olympic:
            print("No stations are linked to Olympic sites. Please check the distance threshold or data.")

    def draw(self):
        """Draw the graph using Folium instead of Matplotlib."""
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
            color = 'blue' if isinstance(v, Station) else 'red'
            folium.Marker(
                location=[v.geopoint.latitude, v.geopoint.longitude],
                popup=v.name,
                icon=folium.Icon(color=color)
            ).add_to(folium_map)

        # Plot edges as lines
        for edge in tqdm(self.cached_edges, desc="Drawing edges"):
            line = LineString([
                (edge.vertex1.geopoint.longitude, edge.vertex1.geopoint.latitude),
                (edge.vertex2.geopoint.longitude, edge.vertex2.geopoint.latitude)
            ])
            folium.PolyLine(
                locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                           (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
                color="black",
                weight=2,
                opacity=1
            ).add_to(folium_map)

        # Save or display the folium map
        folium_map.save("map.html")  # This will save the map to an HTML file
        folium_map  # Display in Jupyter Notebook (if you use one)

    def set_distance_threshold(self, distance_threshold: float):
        """Set distance threshold and calculate edges based on it."""
        self.calculate_edges(distance_threshold)
