from .Edge import Edge
from .Vertex import Vertex
from .Station import Station
from .Olympic import Olympic
import math
import osmnx as ox
import networkx as nx
import folium
from tqdm import tqdm
import functools
from concurrent.futures import ProcessPoolExecutor, as_completed

MPS = 1.25

class Graph:  
  def __init__(self, vertices: list[Vertex], max_distance=1000, name="default_name", threaded=False, saved=False, cached=False):
    self.vertices = vertices
    self.olympics = self.getOlympics()
    self.stations = self.getStations()
    self.cached_edges = []
    self.max_distance = max_distance
    self.threaded = threaded
    self.saved = saved
    self.name = name
    self.cached = cached
    
  def getStations(self):
    stations=[]
    stations_name = []
    for v in self.vertices:
      # if isinstance(v, Station) and v.name not in stations_name:
      if isinstance(v, Station):
        stations.append(v)
        stations_name.append(v.name)
    return stations
  
  def getOlympics(self):
    olympics=[]
    olympics_name = []
    for v in self.vertices:
      if isinstance(v, Olympic) and v.name not in olympics_name:        
        olympics.append(v)
        olympics_name.append(v.name)
    return olympics
  
  def haversine(self, lng1, lat1, lng2, lat2):
    """
    Calculate the Haversine distance between two points on the Earth specified by longitude and latitude and return true if the distance is less than 10 meters.

    Parameters:
    lng1, lat1: Longitude and latitude of the first point in degrees.
    lng2, lat2: Longitude and latitude of the second point in degrees.

    Returns:
    Distance in meters between the two points.
    """
    # Radius of Earth in meters
    R = 6371000  

    # Convert latitude and longitude from degrees to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Distance in meters
    distance = R * c
    return distance
  
  def goodOlympics(self):
    olympics = []
    olympics_name = []
    for e in self.cached_edges:
      if isinstance(e.vertex1, Olympic) and e.vertex1.name not in olympics_name:
        olympics.append(e.vertex1)
        olympics_name.append(e.vertex1.name)
    return olympics
  
  def save(self, save):
    self.saved = save
  
  def save(self):
    return None
  
  def set_distance_threshold(self, max_distance):
    self.max_distance = max_distance
    
  def get_distance_threshold(self):
    return self.max_distance
  
  def set_restriction_minutes(self, minutes):
    self.max_distance = minutes * 60 * MPS
  
  def set_restriction_seconds(self, seconds):
    self.max_distance = seconds * MPS

  def set_multi_threading(self, threaded):
    self.threaded = threaded
    
  def calculate(self):
    graph_center = (
            sum(v.geopoint.latitude for v in self.vertices) / len(self.vertices),
            sum(v.geopoint.longitude for v in self.vertices) / len(self.vertices)
        )
    graph = ox.graph_from_point(graph_center, dist=self.get_distance_threshold(), network_type='walk')
    edges = []
    if self.threaded:
      with ProcessPoolExecutor() as executor:
        future_to_olympic = {
          executor.submit(self.calculate_olympic_site, o, graph): o for o in enumerate(self.olympics)
        }

        for future in tqdm(as_completed(future_to_olympic), total=len(future_to_olympic)):
          o = future_to_olympic[future]
          try:
            result = future.result()
            edges.extend(result)
          except Exception as e:
            print(f"Exception for {o}: {e}")
        self.cached_edges = edges
    else:
      for o in tqdm(enumerate(self.olympics), total=len(self.olympics)):
        edges += self.calculate_olympic_site(o, graph)
      self.cached_edges = edges
  
  def calculate_each_olympic_graph(self):
    edges = []
    if(self.threaded):
      with ProcessPoolExecutor() as executor:
        future_to_olympic = {
          executor.submit(
            self.calculate_olympic_site, o, ox.graph_from_point(
              (o[1].geopoint.latitude, o[1].geopoint.longitude),
              dist=self.get_distance_threshold(),
              network_type='walk')
            ): o for o in enumerate(self.olympics)
        }

        for future in tqdm(as_completed(future_to_olympic), total=len(future_to_olympic)):
          o = future_to_olympic[future]
          try:
            result = future.result()
            edges.extend(result)
          except Exception as e:
            print(f"Exception for {o}: {e}")
        self.cached_edges = edges
    else:
      for o in tqdm(enumerate(self.olympics), total=len(self.olympics)):
        olympic = o[1].geopoint
        graph = ox.graph_from_point((olympic.latitude, olympic.longitude), dist=self.get_distance_threshold(), network_type='walk')
        edges += self.calculate_olympic_site(o, graph)
      self.cached_edges = edges
    
  def calculate_olympic_site(self, o, graph):
      # print("Station olympic: ", o[1].name)
      olympic = o[1].geopoint
      selected_stations = []
      selected_stations_ids = []
      
      for s in tqdm(enumerate(self.stations), total=len(self.stations)):
        station = s[1].geopoint
        distance_harversine = self.haversine(olympic.longitude, olympic.latitude, station.longitude, station.latitude)
        # print('distance vol d"oiseau: ', distance_harversine)
        if distance_harversine <= self.get_distance_threshold():
          # print('distance vol d"oiseau inf max')
          # print('Pré-selection de la station : ' + s.name, distance_harversine)
          selected_stations.append(s)
          selected_stations_ids.append(ox.distance.nearest_nodes(graph, station.longitude, station.latitude))
        
      source_node = ox.distance.nearest_nodes(graph, olympic.longitude, olympic.latitude)
      
      distances, paths = nx.single_source_dijkstra(graph, source_node, weight="length")
      
      # target_distances = {node: distances[node] for node in selected_stations_ids if node in distances and distances[node] <= self.get_distance_threshold()}
      # target_paths = {node: paths[node] for node in target_nodes if node in paths and distances[node] <= self.get_distance_threshold()}
      edges = []
      for node in selected_stations_ids:
        if node in distances and distances[node] <= self.get_distance_threshold():
          # print('Création du lien avec la station : ', selected_stations[selected_stations_ids.index(node)].name, distances[node])
          s = selected_stations[selected_stations_ids.index(node)]
          edge = Edge(o[1], s[1], distances[node])
          edges.append(edge)
      return edges

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
        
    for v in self.stations:
        color = 'blue'
        folium.Marker(
            location=[v.geopoint.latitude, v.geopoint.longitude],
            popup=v.name,
            icon=folium.Icon(color=color)
        ).add_to(folium_map)

    for v in self.olympics:
        color = 'red'
        folium.Marker(
            location=[v.geopoint.latitude, v.geopoint.longitude],
            popup=v.name,
            icon=folium.Icon(color=color)
        ).add_to(folium_map)

    # Plot edges as lines with walking time
    for edge in tqdm(self.cached_edges, desc="Drawing edges"):
        # print('edge: ', edge)
        # convert edge.weight to minutes / seconds
        distance = edge.weight
        time = distance / MPS
        minutes = int(time // 60)
        seconds = int(time % 60)
        folium.PolyLine(
            locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                    (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
            color="black",
            weight=2,
            opacity=1,
            tooltip=f"Walking time: {minutes}m {seconds}s"  # Display walking time as tooltip
        ).add_to(folium_map)

    folium_map.save("map2.html")  
    return folium_map 

# one line copy graph.nodes into nodes_ids
# max_distance = 1500
# stations_ids_list = []
# olympics_ids = []
# graphs = []

# stations_visited = 0
# olympics_visited = 0


# for o in O:
#   olympic = o.geopoint
#   graph = ox.graph_from_point((olympic.latitude, olympic.longitude), dist=max_distance, network_type='walk')
#   source_node = ox.distance.nearest_nodes(graph, olympic.longitude, olympic.latitude)
#   target_nodes = [ox.distance.nearest_nodes(graph, s.geopoint.longitude, s.geopoint.latitude) for s in S]
  
#   distances, paths = nx.single_source_dijkstra(graph, source_node, weight="length")
  
#   target_distances = {node: distances[node] for node in target_nodes if node in distances and distances[node] <= max_distance}
#   target_paths = {node: paths[node] for node in target_nodes if node in paths and distances[node] <= max_distance}
  
#   print(target_distances)

# print("fin")

# # for o in O:
# #   olympic = o.geopoint
# #   graph = ox.graph_from_point((olympic.latitude, olympic.longitude), dist=max_distance, network_type='walk')
# #   graphs.append(graph)
# #   olympic_node = ox.distance.nearest_nodes(graph, olympic.longitude, olympic.latitude)
# #   olympics_ids.append(olympic_node)
  
# #   stations_ids = []
# #   for s in S:
# #     station = s.geopoint
# #     station_node = ox.distance.nearest_nodes(graph, station.longitude, station.latitude)
# #     print(station_node)
# #     stations_ids.append(station_node)
# #   stations_ids_list.append(stations_ids)

# # # print(olympics_visited, len(O))
# # # print(stations_visited, len(S))
# # # exit()

# # for i, o in enumerate(O):
# #   stations_id = stations_ids_list[i]
# #   olympics_id = olympics_ids[i]
# #   black_list = []
# #   visited = []
# #   graph = graphs[i]
  
# #   nodes_ids = list(graph.nodes)
# #   dists = [float('inf') for _ in range(len(nodes_ids))]
# #   previous = [None for _ in range(len(nodes_ids))]
# #   unvisited = [olympics_id]
  
# #   dists[nodes_ids.index(olympics_id)] = 0
  
# #   print('nodes count: ', len(nodes_ids))
# #   print('stations count: ', len(stations_id))
# #   print('olympics id:', olympics_id)
  
# #   while len(unvisited) > 0:
# #     print('stations visited:', stations_visited)

# #     # get minimum distance node index in unvisited nodes
# #     index_of_min = dists.index(min([dists[nodes_ids.index(node)] for node in unvisited]))
    
# #     print('index of min:', index_of_min)
# #     print('node:', nodes_ids[index_of_min])

# #     if dists[index_of_min] == float('inf') or dists[index_of_min] > max_distance:
# #       print('break')
# #       break
    
# #     u = nodes_ids[index_of_min]
# #     if u in visited:
# #       print('already visited')
# #     visited.append(u)
# #     if u in unvisited:
# #       print('remove from unvisited')
# #     unvisited.remove(u)

    
# #     if u in stations_ids:
# #       print('station found')
# #       stations_visited += 1
    
# #     for edge in graph.edges(u, data=True):
# #       print('---')
# #       v = edge[1]
# #       print('edge:', v)
# #       alt = dists[nodes_ids.index(u)] + edge[2]['length']
# #       print('distances :', dists[nodes_ids.index(v)], alt)
  
# #       if alt < dists[nodes_ids.index(v)]:
# #         print('new distance is better')
# #         dists[nodes_ids.index(v)] = alt
# #         previous[nodes_ids.index(v)] = u
      
# #       if v not in visited and v not in unvisited:
# #         print('add to unvisited')
# #         unvisited.append(v)
        
# #     print('--------------------')
      
# #   break
# #   # print(selected_stations)
# #   # print(olympics_id)

# # print(olympics_visited, len(O))
# # print(stations_visited, len(S))

# # # # # for station in selected_stations:
# # # # #   print(station)
