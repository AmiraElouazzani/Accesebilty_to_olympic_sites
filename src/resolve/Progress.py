from bitarray import bitarray

from ..Graph import Graph
from ..Station import Station
from ..Olympic import Olympic

class Progress:
    @staticmethod
    def solve(G:Graph):
        profiles = Progress.make_profiles(G)

    #returns an array of bitarray
    def make_profiles(G:Graph):
        stations = G.getStations()
        olympics = G.getOlympics()
        profiles = []

        for s in stations:
            profile = Progress.make_profile(G, s)
            profiles.append(profile)
        return profiles
    
    #returns a bitarray
    def make_profile(G:Graph, s:Station, olympics: list[Olympic]):
        profile = bitarray(len(olympics))
        profile.setall(0)
        for o in olympics:
            if G.are_adjacent(s, 0):
                profile[o]=1
        return profile
        