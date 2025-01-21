from .Vertex import Vertex

class Edge:
    def __init__(self, v1: Vertex, v2: Vertex, w: float = 1):
        self.vertex1 = v1
        self.vertex2 = v2
        self.weight = w
        
    @staticmethod
    def walking_time_from_distance(distance_meters: float) -> float:
        walking_speed_kmph = 5.5  # Average walking speed (can be 5-6 km/h)
        walking_speed_mpm = (walking_speed_kmph * 1000) / 60.0  # meters per minute
        return distance_meters / walking_speed_mpm
    
    def isIncident(self, v: Vertex) -> bool:
        return self.vertex1 == v or self.vertex2 == v
    
    def __str__(self):
        return f"Edge: {self.vertex1} -> {self.vertex2} ({self.weight})"