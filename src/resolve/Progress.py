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

        profiles = Progress.goodmakeprofiles(G, False)
        sorted_profiles = Progress.sort_profile(profiles)
        prime_profiles = Progress.eliminate_weak(sorted_profiles)
        station_to_modify = Progress.search_union(prime_profiles)
        return station_to_modify

    #progressive way, The graph doesn't contain "bad" olympic site
    @staticmethod
    def kaizen(G:Graph):

        all_olympics = G.getOlympics()
        olympics_notused = []

        for ao in all_olympics:
            olympics_notused.append(ao)

        G.addprogressOlympics(olympics_notused[0])
        olympics_notused.remove(olympics_notused[0])
        

        #print("taille good_olympics, supposéement 27 aussi", len(all_olympics))
        for i in range(len(all_olympics)):

            #(a)
            profiles = Progress.goodmakeprofiles(G,True)
            sorted_profiles = Progress.sort_profile(profiles)
            prime_profiles = Progress.eliminate_weak(sorted_profiles)
            station_to_modify = Progress.search_union(prime_profiles)

            #(c)
            if station_to_modify != False:
                #tester si la solution valide sur W est valide sur tt les sites olympique. Si oui break et return cette solution
                profiles_complets = []
                compteurtaille = 0 #debug only
                for s in station_to_modify: 

                    profil_to_add =(Progress.make_full_profile(G,s),s)
                    profiles_complets.append(profil_to_add)
                    compteurtaille +=1

                
                # for p in profiles_complets:
                #     print(p[0])
                full_stationtomodify = Progress.search_union(profiles_complets)
                
                if full_stationtomodify != False:
                    #print("taille solution",len(full_stationtomodify), "taille profiles", len(profiles_complets))
                    return full_stationtomodify
            else:
                
                return False
            
            #(d) add a non dominated vertex (olympic site), certainement le problème est la dedans

            if not olympics_notused: #check if this list is empty, if it's the case at this point it means there is no solution
                return False
            #print("olympic not used", olympics_notused)
            olympic_to_remove = []
            for o in olympics_notused:
                #if(len(profiles_complets)>20):
                    
                cpt_dominance = 0

                for sta in station_to_modify:
                    
                    if not G.are_adjacent( o,sta):
                        
                        cpt_dominance +=1
                    
                if cpt_dominance != len(station_to_modify):
                        #print("ajout d'un site dominé pour éviter un décalage")
                        G.addprogressOlympics(o)
                        olympic_to_remove.append(o)
                    
                if cpt_dominance == len(station_to_modify):
                    
                    #print("ajout d'un site non dominé")
                    G.addprogressOlympics(o)
                    olympic_to_remove.append(o)
                    break

            for otr in olympic_to_remove:
                olympics_notused.remove(otr)

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
            for s in tqdm(stations,desc="compute profiles k"):
                profile = Progress.make_profile(G, s, G.getprogressOlympics())
                profiles.append((profile, s))

        #print("tailles des profiles: ",len(profiles[0][0]))                debug line
        return profiles
    
    #returns a bitarray
    @staticmethod
    def goodmakeprofiles(G: Graph,kaizen: bool):

        if kaizen:
            olympics = G.getprogressOlympics()
        else:
            olympics = G.getOlympics()

        stationdict ={}
        profile_index = 0
        #print(len(olympics))

        #for o in tqdm(olympics,desc="compute profiles"):
        for o in olympics:
            
            profile0 = bitarray(len(olympics))    #problème est ici les premiers créé sont de longueur 1 et donc on ne peut pas accéder plus loin, il faut remplir de 0
            profile0.setall(0)

            for sta in G.get_neighbors(o):

                if sta.getprofile() == 0:

                    sta.setprofile(profile0)
                
                okprofile = sta.getprofile()

                while(len(okprofile) < len(olympics)):

                    okprofile.append(0)

                okprofile[profile_index] = 1

                sta.setprofile(okprofile)    
                
                stationdict[sta] = sta.getprofile()

            profile_index +=1

        actualprofiles = []
        #print("taille du dctionnaire de stations",len(stationdict))
        for i in stationdict:
            
            actualprofiles.append((i.getprofile(),i))
        
        return actualprofiles

    @staticmethod
    def make_full_profile(G:Graph, s:Station):
        
        olymp = G.getOlympics()
        profile_index = 0
        okprofile = s.getprofile()
        copy = bitarray.copy(okprofile)

        while(len(copy) < len(olymp)):
            copy.append(0)
            
        for o in olymp:
            if G.are_adjacent(s, o):
                copy[profile_index]=1
            profile_index +=1

        return copy
    
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
                    #print("prime", prime[0], "testé", sorted_p[0] )
                    if(subset(sorted_p[0], prime[0])):
                        break                               #si subset d'au moins un alors on ajoute pas à notre liste finale
                        
                    compteur_prime +=1                      # on compte de combien il n'est pas subset 
                    
                if compteur_prime == len(prime_profile):    #si il n'est subset d'aucun alors on ajoute a la liste finale
                    
                    prime_profile.append(sorted_p)
            
            #only for the first one, it has to be a prime profile
            else: 
                prime_profile.append(sorted_p)

        #print("sortir")    
        return prime_profile
        

        

    #search for the smallest union of profile equals to [11...11], the number of ones is the number of olympic site. And return the corresponding stations.
    @staticmethod
    def search_union(prime_profiles):

        taille_profile = len(prime_profiles[0][0])
        #print("taille du profil search union",taille_profile, "nombre de stations", len(prime_profiles))
        for i in tqdm(range(1,taille_profile+1),desc="searching union"):
        
            comb_prime = combinations(prime_profiles, i )
            
            for comb in comb_prime:
                
                bits_potential_union = zeros(taille_profile)
                station_potential_union =[]
                
                for j in range(i):
        
                    bits_potential_union = bits_potential_union | (comb[j][0])
            
                    station_potential_union.append(comb[j][1])
                
                if(bits_potential_union.all()):
                    
                    # if(len(prime_profiles[0][0]) == 11):
                    #     for pp in prime_profiles:

                    #         print("profiles 11",pp[0],pp[1].__str__())
                    #     for sta in station_potential_union:
                    #         print(sta.__str__())
                    return station_potential_union
                    
            
        return False
    


        