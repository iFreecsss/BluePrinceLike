from player import *
from map import *
from room import *

class Game:

    def __init__(self):
        self.player = Player()
        self.map = Map()
        self.data = {}

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
        if input == "UP":
            self.player.face(0)
        elif input == "LEFT":
            self.player.face(1)
        elif input == "DOWN":
            self.player.face(2)
        elif input == "RIGHT":
            self.player.face(3)
    
    def player_movement(self,input):
        """
        Même cas que pour player orientation.
        """
        direction = self.player.direction
        movement = (0,0)
        if direction == 0:
            movement = (0,1)
        elif direction == 1:
            movement = (-1,0)
        elif direction == 2:
            movement = (0,-1)
        elif direction == 3: 
            movement = (1,0)
        
        final_position = (self.player.position[0] + movement[0], self.player.position[1] - movement[1])
        new_x, new_y = final_position
        
        MIN_X, MAX_X = 0, 4
        MIN_Y, MAX_Y = 0, 8
        
        if (MIN_X <= new_x <= MAX_X) and (MIN_Y <= new_y <= MAX_Y): # Vérifie les limites de la map
            self.player.move(final_position)
    
    def handle_inputs(self, inputs):
        #input types:

        #Direction
        direction_change=["UP","DOWN","LEFT","RIGHT"]
        #Movement_Confirmation
        movement_confirmation = ["SPACE"]

        for i in inputs:
            if i in direction_change:
                self.player_orientation(i)
            
            if i in movement_confirmation:
                self.player_movement(i)


    def publish_data(self):
        """
        Donne toutes les données pertinnents pour l'affichage, a ajouter les nouvelles données ici.
        """
        self.data['position'] = self.player.position
        self.data['direction'] = self.player.direction
        self.data['mapping'] = self.map.get_current_mapping()
        return self.data
    
    


    



