from .Geopoint import Geopoint
from .Site import Site
from bitarray import bitarray
from bitarray.util import zeros



class Station(Site):
    def __init__(self, geopoint: Geopoint, name, line_index, accessible : bool = False, color='gray') -> None:
        #if(accessible):color='green'
        super().__init__(geopoint, name, color)
        self.line_index = line_index
        self.solution = False
        self.profile = zeros(1)
        
    
    def __str__(self):
        return f"{super().__str__()}, Line Index: {self.line_index}"
    
    def belongSolution(self):
        self.solution = True
        self.set_color('green')
        
    
    def getSolution(self):
        return self.solution
    
    def getprofile(self):
        copy_profile = bitarray.copy(self.profile)
        
        return copy_profile
    
    def setprofile(self, goodprofile):
        self.profile = goodprofile
    
    def changeprofile(self, index, value):
        self.profile[index] = value
    


    
    

