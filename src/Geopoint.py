import math
import osmnx as ox 
class Geopoint:
    def __init__(self, lat, long) -> None:
        self.latitude = lat
        self.longitude = long

    def __str__(self):
        return f"Geopoint(latitude={self.latitude}, longitude={self.longitude})"
        
    def distance(self, other: 'Geopoint') -> float:
        """Calculate the distance in kilometers between this Geopoint and another Geopoint."""
        # Haversine formula
        R = 6371.0  # Earth radius in kilometers
        lat1_rad = math.radians(self.latitude)
        lon1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(other.latitude)
        lon2_rad = math.radians(other.longitude)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c  # Distance in kilometers
        return distance
    

    # def walking_distance(self, other: 'Geopoint') -> float:
    #     """Calculate walking distance between this Geopoint and another Geopoint using OSMnx."""
    #     # Create the graph for walking
    #     G = ox.graph_from_point((self.latitude, self.longitude), dist=2000, network_type='walk')

    #     # Find the nearest nodes on the graph to the two geopoints
    #     orig_node = ox.nearest_nodes(G, self.longitude, self.latitude)
    #     dest_node = ox.nearest_nodes(G, other.longitude, other.latitude)

    #     # Calculate the shortest path distance between the two nodes (in meters)
    #     distance_meters = ox.distance.shortest_path_length(G, orig_node, dest_node, weight='length')

    #     # Convert the distance from meters to kilometers
    #     distance_km = distance_meters / 1000
    #     return distance_km