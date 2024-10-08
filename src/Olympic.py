from .Geopoint import Geopoint
from .Site import Site

class Olympic(Site):
    def __init__(self, geopoint: Geopoint, name, color='blue') -> None:
        super().__init__(geopoint, name, color)
