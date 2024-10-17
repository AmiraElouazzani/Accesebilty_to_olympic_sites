from ..Graph import Graph
from ..Station import Station
from ..Olympic import Olympic

class Progress:
    @staticmethod
    def solve(G:Graph):
        profiles = Progress.make_profiles(G)

    def make_profiles(G:Graph):
        stations = G.getStations()
        olympics = G.getOlympics()
        profiles = []

        for s in stations:
            profile = Progress.make_profile(G, s)
            profiles.append(profile)
        return profiles
    
    def make_profile(G:Graph, s:Station, olympics: list[Olympic]):
        profile = 0b0
        for o in olympics:
            if G.are_adjacent(s, 0):
                profile = profile | 0b1
            #