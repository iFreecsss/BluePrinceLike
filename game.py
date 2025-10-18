from player import *
from map import *
from room import *

class Game:

    def __init__(self):
        self.player = Player()
        self.map = Map()


    def check_status(self):
        """
        Rof a voir
        """
        pass

    def draw_room(self):
        """
        Hardcodé de façon à tester l'ajout de chambres sur l'ui
        """
        return Parlor()
    
    def player_orientation(self, input):
        """
        Appel de fonction pour appeler une fontion dans player, pas ouf,
        peut être modifié de façon à ce que player ne soit qu'un contenaire et Game intégres les getters/setters pour ses valeurs,
        mais a des fins de demo ça reste acceptable.
        """
        self.player.face(input)
    

    def player_movement(self,input):
        """
        Même cas que pour player orientation.
        """
        self.player.position(input)
    

    def map_list(self):
        return self.map
    
    


    



