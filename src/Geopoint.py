class Geopoint:
    def __init__(self, lat, long) -> None:
        self.latitude = lat
        self.longitude = long

    def __str__(self):
        return f"Geopoint(latitude={self.latitude}, longitude={self.longitude})"