from .Geopoint import Geopoint
from .Vertex import Vertex

class Site(Vertex):
    def __init__(self, geopoint : 'Geopoint', name, color) -> None:
        super().__init__(color)
        self.geopoint = geopoint
        self.name = name

    def get_position(self):
        return [self.geopoint.latitude, self.geopoint.longitude]

    def __str__(self):
        return f"Site: {self.name}, {self.geopoint}"