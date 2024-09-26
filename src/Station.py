from .Geopoint import Geopoint
from .Site import Site

class Station(Site):
    def __init__(self, geopoint: Geopoint, name, line_index, accessible : bool = False, color='gray') -> None:
        if(accessible):color='green'
        super().__init__(geopoint, name, color)
        self.line_index = line_index
    
    def __str__(self):
        return f"{super().__str__()}, Line Index: {self.line_index}"