from bitarray import bitarray
from bitarray.utils import ba2int, subset, zeros
from itertools import combinations

from ..Graph import Graph
from ..Station import Station
from ..Olympic import Olympic

class Progress:
    @staticmethod
    def solve(G:Graph):
        profiles = Progress.make_profiles(G)
        sorted_profiles = Progress.sort_profile(profiles)
        prime_profiles = eliminate_weak(sorted_profiles)
        station_to_modify = search_union(prime_profiles)
        return station_to_modify

    #returns an array of bitarray
    def make_profiles(G:Graph):
        stations = G.getStations()
        olympics = G.getOlympics()
        profiles = []

        for s in stations:
            profile = Progress.make_profile(G, s)
            profiles.append((profile, s))
        return profiles
    
    #returns a bitarray
    def make_profile(G:Graph, s:Station, olympics: list[Olympic]):
        profile = bitarray(len(olympics))
        profile.setall(0)
        profile_index = 0
        for o in olympics:
            if G.are_adjacent(s, o):
                profile[profile_index]=1
        profile_index +=1
        return profile
    
    #sort profiles by decimal value small to big and eliminates duplicate, using counting sort.
    def sort_profile(Profiles:[(bitarray, Station)]):

        tab_strong = [0]*8192  #2^13
        sorted_profiles= []
    
        for i in Profiles:
            if tab_strong[ba2int(i[0])] == 0:
                tab_strong[ba2int(i[0])] = i
        for i in tab_strong:
            if i != 0:
                sorted_profiles.append(i)

        return sorted_profiles

    #eliminates "weaker" profile in the sorted list. [0110] is weaker than [0111] (included) maybe use subset(a, b, /) method from bitarray. 
    def eliminate_weak(Sorted_profiles:[(bitarray, Station)]):
        prime_profile = []

        for sorted_p in Sorted_profiles[::-1]:
            
            compteur_prime = 0
            
            if prime_profile != []:
                
                for prime in prime_profile:
                    
                    if(subset(sorted_p[0], prime[0])):
                        break
                        
                    compteur_prime +=1   
                    
                if compteur_prime == len(prime_profile):
                    
                    prime_profile.append(sorted_p)
            
            #only for the first one, it has to be a prime profile
            else: 
                prime_profile.append(sorted_p)
            
        return prime_profile
        

        

    #search for the smallest union of profile equals to [11...11], the number of ones is the number of olympic site. And return the corresponding stations.
    def search_union(prime_profiles:[(bitarray, Station)]):

        for i in range(2,len(prime_profiles[0][0])):
        
            comb_prime = combinations(prime_profiles, i )
            
            for comb in comb_prime:
                
                bits_potential_union = zeros(length)
                station_potential_union =[]
                
                for j in range(i):
        
                    bits_potential_union = bits_potential_union | (comb[j][0])
            
                    station_potential_union.append(comb[j][1])
                
                if(bits_potential_union.all()):
                    
                    return station_potential_union
            
        return False
    


        