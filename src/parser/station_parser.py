import json
import os
from ..Station import Station
from ..Geopoint import Geopoint

# A parser for station sites
def station_parser() -> list[Station]:
    # Define the path to the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), '../../data/emplacement-des-gares-idf.json')
    
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    stations = []
    
    # Parse the JSON data
    for site in data:
        geo_point = site.get('geo_point_2d')
        name = site.get('nom_gares')
        line_index = site.get('indice_lig')
        
        if geo_point and name and line_index is not None:
            geopoint_obj = Geopoint(lat=geo_point['lat'], long=geo_point['lon'])
            station = Station(geopoint_obj, name, line_index)
            stations.append(station)
    
    return stations