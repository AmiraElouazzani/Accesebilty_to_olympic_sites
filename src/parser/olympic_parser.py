import json
import os
from ..Olympic import Olympic
from ..Geopoint import Geopoint
from ..Site import Site

# A parser for olympic sites
def olympic_parser() -> list[Olympic]:
    # Define the path to the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), '../../data/paris-2024-sites-olympiques-et-paralympiques-franciliens.json')
    
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    olympic_sites = []
    
    # Parse the JSON data
    for site in data:
        geo_point = site.get('geo_point')
        name = site.get('nom')
        
        if geo_point and name:
            geopoint_obj = Geopoint(lat=geo_point['lat'], long=geo_point['lon'])
            olympic_site = Olympic(geopoint_obj, name)
            olympic_sites.append(olympic_site)
    
    return olympic_sites

