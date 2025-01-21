from .Edge import Edge
from .Vertex import Vertex
from .Station import Station
from .Olympic import Olympic
import math
import osmnx as ox
import networkx as nx
import folium
import random
from tqdm import tqdm
import functools
from bitarray.util import zeros
from concurrent.futures import ProcessPoolExecutor, as_completed

MPS = 1.25

class Graph:  
  def __init__(self, vertices: list[Vertex], olympics: list[Olympic], stations: list[Station], edges: list[Edge] = [], name="default_name", threaded=False):
    self.vertices = vertices
    self.olympics = olympics
    self.stations = stations
    self.edges = edges
    self.cached_edges = []
    self.max_distance = 1000
    self.threaded = threaded
    self.name = name
    self.progressOlympics = []
    
  def getStations(self):
    if(not hasattr(self, "stations")):
      self.stations = []
      for v in self.vertices:
        if isinstance(v, Station):
          self.stations.append(v)
    return self.stations
  
  def getOlympics(self):
    if(not hasattr(self, "olympics")):
      self.olympics=[]
      for v in self.vertices:
        if isinstance(v, Olympic):        
          self.olympics.append(v)
    return self.olympics

  def isSolutionOfAccessibility(self, A):
    visited = set()
    for a in A:
      visited = visited.union(self.get_neighbors(a))
    return (set(self.olympics).issubset(visited))
  
  def are_adjacent(self, v1 : Vertex, v2 : Vertex):
    for e in self.edges:
      if (e.vertex1 == v1 and e.vertex2 == v2) or (e.vertex1 == v2 and e.vertex2 == v1):
        return True
    return False

  def get_neighbors(self, v : Vertex):
    return v.getadja()
  
  def getprogressOlympics(self):
    return self.progressOlympics

  def addprogressOlympics(self, newOlympics):
    self.progressOlympics.append(newOlympics)

  
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
  
  #remove olympic sites from the graph that are not connected to any station
  #it means we will find a solution for the accessibility problem but not for these stations
  def goodOlympics(self):
    good_olympics =[]
    bad_olympics =[]
    for olymp in self.getOlympics():
      if self.has_neighbours_station(olymp):
        good_olympics.append(olymp)
      else:
        bad_olympics.append(olymp)
    self.changeOlympics(good_olympics)

    return (len(good_olympics), bad_olympics)
  
  def changeOlympics(self, new_olympics):
    self.olympics = new_olympics
  
  def has_neighbours_station(self,v: Vertex):
    neighbors = v.getadja()

    if neighbors != False:
      for ver in neighbors:
        if isinstance(ver, Station):
          return True
    
    return False
  
  def set_distance_threshold(self, max_distance):
    self.max_distance = max_distance
    
  def get_distance_threshold(self):
    return self.max_distance
  
  def set_restriction_minutes(self, minutes):
    self.max_distance = minutes * 60 * MPS
    print("Max distance: ", self.max_distance)
  
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
          executor.submit(self.calculate_olympic_site, o, graph): o for o in self.getOlympics()
        }

        for future in as_completed(future_to_olympic):
          o = future_to_olympic[future]
          try:
            result = future.result()
            edges.extend(result)
          except Exception as e:
            print(f"Exception for {o}: {e}")
        self.cached_edges = edges
        self.edges = self.edges + edges
    else:
      for o in tqdm(enumerate(self.getOlympics()), desc="Processing Olympic sites"):
        edges += self.calculate_olympic_site(o, graph)
      self.cached_edges = edges
      self.edges = self.edges + edges
  
  def usefull_edges_time(self, minutes):
    self.set_restriction_minutes(minutes)
    edges = []
    if(self.threaded):
      with ProcessPoolExecutor() as executor:
        future_to_olympic = {
          executor.submit(
            self.calculate_olympic_site, o, ox.graph_from_point(
              (o.geopoint.latitude, o.geopoint.longitude),
              dist=self.get_distance_threshold(),
              network_type='walk')
            ): o for o in tqdm(enumerate(self.getOlympics()), desc="Processing Olympic sites")
        }

        for future in as_completed(future_to_olympic):
          o = future_to_olympic[future]
          try:
            result = future.result()
            edges.extend(result)
          except Exception as e:
            print(f"Exception for {o}: {e}")
        self.cached_edges = edges
        self.edges = self.edges + edges
    else:
      for o in tqdm(enumerate(self.getOlympics()), desc="Processing Olympic sites"):
        olympic = o[1].geopoint
        graph = ox.graph_from_point((olympic.latitude, olympic.longitude), dist=self.get_distance_threshold(), network_type='walk')
        edges += self.calculate_olympic_site(o, graph)
      self.cached_edges = edges
      self.edges = self.edges + edges
    
  def calculate_olympic_site(self, o, graph):
      olympic = o[1].geopoint
      source_node = ox.distance.nearest_nodes(graph, olympic.longitude, olympic.latitude)
      distances, paths = nx.single_source_dijkstra(graph, source_node, weight="length")
      edges = []
      
      for s in self.getStations():
        station = s.geopoint
        distance_harversine = self.haversine(olympic.longitude, olympic.latitude, station.longitude, station.latitude)
        # print('distance vol d"oiseau: ', distance_harversine)
        if distance_harversine <= self.get_distance_threshold():
          # print('distance vol d"oiseau inf max')
          node = ox.distance.nearest_nodes(graph, station.longitude, station.latitude)
          if node in distances and distances[node] <= self.get_distance_threshold():
            walking_time = distances[node] / (MPS * 60)
            # print('Création du lien avec la station : ', selected_stations[selected_stations_ids.index(node)].name, distances[node])
            edge = Edge(s, o[1], walking_time)
            edges.append(edge)
            s.addadja(o[1])
            o[1].addadja(s)
        
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

    # Plot vertices as markers on the map
    for v in self.vertices:
      if isinstance(v, Station):
        if v.getSolution():
            color = 'green'
            v.set_color(color)
        else:
            color = 'blue'
            v.set_color(color)
      else:
        color = 'red'
        v.set_color(color)
      
      #  color in('red', 'green', 'blue')
      
      if(isinstance(v, Olympic)): # verify that the vertex is an olympic site or a station to modify
        folium.Marker(
            location=[v.geopoint.latitude, v.geopoint.longitude],
            popup=v.name,
            icon=folium.Icon(color=color)
        ).add_to(folium_map)
      elif(isinstance(v, Station)):
        if(v.getSolution()):
          folium.Marker(
            location=[v.geopoint.latitude, v.geopoint.longitude],
            popup=v.name,
            icon=folium.Icon(color=color)
          ).add_to(folium_map)

    for edge in tqdm(self.cached_edges, desc="Drawing edges"):
      if((edge.vertex1.get_color() in('red', 'green') and edge.vertex2.get_color() in('red', 'green'))): #verify if the edge connect an olympic site to a station to modify
        total_seconds = round(edge.weight * 60)  # Convert minutes to total seconds
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        folium.PolyLine(
          locations=[(edge.vertex1.geopoint.latitude, edge.vertex1.geopoint.longitude),
                  (edge.vertex2.geopoint.latitude, edge.vertex2.geopoint.longitude)],
          color="black",
          weight=2,
          opacity=1,
          tooltip=f"Walking time: {minutes} mins {seconds} secs").add_to(folium_map)
    folium_map.save("map.html")  
    return folium_map 
  
  def makeprofile(self, station: Station):
    olympics = self.getOlympics()
    profile_index = 0
    copy = zeros(len(olympics))

    for olymp in olympics:
        if station.isadja(olymp):
            copy[profile_index]=1
        profile_index +=1
    station.setprofile(copy)

  def makeprofiles(self):
    stations = self.getStations()
    for stat in stations:
        self.makeprofile(stat)

  def random_peel(self, n):

    if len(self.stations)==0:
      print("You peeled all the stations !")
    elif len(self.olympics)==0:
      print("You peeled all the olympic sites !")

    V = self.vertices
    removed = []
    for i in range(n):
      random_vertex = random.choice(V)
      removed.append(random_vertex)
      V.remove(random_vertex)

      if random_vertex in self.olympics:
        self.olympics.remove(random_vertex)
      if random_vertex in self.stations:
        self.stations.remove(random_vertex)

    for v in removed:
      for edge in self.edges:
        if edge.isIncident(v):
          self.edges.remove(edge)

    self.goodOlympics()


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
