import matplotlib.pyplot as plt

class Vertex:
    def __init__(self, color) -> None:
        self.color = color

    def get_position(self):
        pass

    def get_color(self):
        return self.color
    
    def draw(self):
        x,y = self.get_position()
        plt.scatter(x,y,c=self.get_color())



