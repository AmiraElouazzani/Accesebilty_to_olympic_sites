class Vertex:
    def __init__(self, color="gray") -> None:
        self.color = color
        self.adja = set()

    def get_position(self):
        pass

    def get_color(self):
        return self.color
    
    def set_color(self,color):
        self.color = color

    def getadja(self):
        adjalist = self.adja
        return adjalist
    
    def addadja(self, neighbour ):
        self.adja.add(neighbour)
    
    def isadja(self, potential_neighbour):
        
        if self.getadja().__contains__(potential_neighbour):
            return True
        return False
