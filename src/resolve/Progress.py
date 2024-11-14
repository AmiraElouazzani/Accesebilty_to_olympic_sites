from bitarray import bitarray
from bitarray.util import ba2int, subset, zeros
from itertools import combinations
from tqdm import tqdm

from ..Graph import Graph
from ..Station import Station
from ..Olympic import Olympic

class Progress:
    @staticmethod
    def solve(G:Graph):

        #first we try if a solution exist
        for o in G.getOlympics():
            if not G.get_neighbors(o):
                print("No solution found")
                return False

        profiles = Progress.make_profiles(G, False)
        sorted_profiles = Progress.sort_profile(profiles)
        prime_profiles = Progress.eliminate_weak(sorted_profiles)
        station_to_modify = Progress.search_union(prime_profiles)
        return station_to_modify

    #progressive way, The graph doesn't contain "bad" olympic site
    def kaizen(G:Graph):

        W = []
        for o in G.getOlympics():
            W.append(o)
            profiles = Progress.make_profiles(G,True)
            sorted_profiles = Progress.sort_profile(profiles)
            prime_profiles = Progress.eliminate_weak(sorted_profiles)
            station_to_modify = Progress.search_union(prime_profiles)

            if station_to_modify != False:
                #tester si la solution valide sur W est valide sur tt les sites olympique. Si oui break et return cette solution
                profiles_complets = []
                for s in station_to_modify:

                    profil_to_add =(Progress.make_profile(G,s,G.getOlympics),s)
                    profiles_complets.append(profil_to_add)

                full_stationtomodify = Progress.search_union(profiles_complets)
                if full_stationtomodify != False:
                    return full_stationtomodify

        return False    
                
    #returns an array of bitarray
    @staticmethod
    def make_profiles(G:Graph, kaizen: bool):
        stations = G.getStations()
        profiles = []

        if not kaizen:

            for s in tqdm(stations,desc="compute profiles"):
                profile = Progress.make_profile(G, s, G.getOlympics())
                profiles.append((profile, s))
        else:
            for s in tqdm(stations,desc="compute profiles"):
                profile = Progress.make_profile(G, s, G.getprogressOlympics())
                profiles.append((profile, s))

        #print("tailles des profiles: ",len(profiles[0][0]))                debug line
        return profiles
    
    #returns a bitarray
    @staticmethod
    def make_profile(G:Graph, s:Station, olympics: list[Olympic]):
        profile = bitarray(len(olympics))
        profile.setall(0)
        profile_index = 0
        for o in olympics:
            if G.are_adjacent(s, o):
                profile[profile_index]=1
            profile_index +=1

        return profile
    
    #sort profiles by decimal value small to big.
    @staticmethod
    def sort_profile(Profiles):
        
        sorted_profiles = sorted(Profiles, key=lambda Profiles: ba2int(Profiles[0]))
        
        return sorted_profiles

    #eliminates "weaker" profile in the sorted list. [0110] is weaker than [0111] (included) maybe use subset(a, b, /) method from bitarray. 
    @staticmethod
    def eliminate_weak(Sorted_profiles):
        prime_profile = []

        for sorted_p in tqdm(Sorted_profiles[::-1],desc="eliminating weak profiles"):
            
            compteur_prime = 0
            
            if prime_profile != []:
                
                for prime in prime_profile:
                    
                    if(subset(sorted_p[0], prime[0])):
                        break                               #si subset d'au moins un alors on ajoute pas à notre liste finale
                        
                    compteur_prime +=1                      # on compte de combien il n'est pas subset 
                    
                if compteur_prime == len(prime_profile):    #si il n'est subset d'aucun alors on ajoute a la liste finale
                    
                    prime_profile.append(sorted_p)
            
            #only for the first one, it has to be a prime profile
            else: 
                prime_profile.append(sorted_p)
            
        return prime_profile
        

        

    #search for the smallest union of profile equals to [11...11], the number of ones is the number of olympic site. And return the corresponding stations.
    @staticmethod
    def search_union(prime_profiles):

        for i in tqdm(range(2,len(prime_profiles[0][0])),desc="searching union"):
        
            comb_prime = combinations(prime_profiles, i )
            
            for comb in comb_prime:
                
                bits_potential_union = zeros(len(prime_profiles[0][0]))
                station_potential_union =[]
                
                for j in range(i):
        
                    bits_potential_union = bits_potential_union | (comb[j][0])
            
                    station_potential_union.append(comb[j][1])
                
                if(bits_potential_union.all()):
                    
                    return station_potential_union
                    
            
        return False
    


        