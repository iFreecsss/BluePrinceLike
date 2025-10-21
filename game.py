from player import *
from map import *
from room import *
import random

class Game:

    def __init__(self):
        self.player = Player()
        self.map = Map()
        self.data = {}

        # test implémentation tirage des pièces
        # il y aura 2 modes. celui qui permet de se déplcacer librement 'EXPLORING' et celui qui oblige
        #  à placer les pièces 'ROOM_DRAWING'
        self.game_state = 'EXPLORING'
        # stocke les 3 pièces à choisir
        self.current_choice_index = 0
        self.room_choices = []
        # mémorise la position où placer la pièce choisie
        self.pending_placement_position = None
        # pioche de salles
        self.room_deck = [
            Aquarium, Attic, Ballroom, Billiard_Room, 
            Boiler_Room, Chamber_of_Mirrors, Closet, 
            Coat_Check, Conference_Room
        ]

    def check_status(self):
        """
        Rof a voir
        """
        pass

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
        current_room_coords = self.player.position
        # on regarde dans quelle salle on est actuellement
        current_room = self.map.get_current_mapping()[current_room_coords] 

        # on check si la salle choisie a une sortie dans la direction du déplacement
        if not current_room.has_exits(direction):
            print("Pas de porte vers ici !")
            return

        direction = self.player.direction
        movement = (0,0)
        if direction == 0: # UP
            movement = (0,1)
        elif direction == 1: # LEFT
            movement = (-1,0)
        elif direction == 2: # DOWN
            movement = (0,-1)
        elif direction == 3: # RIGHT
            movement = (1,0)
        
        final_position = (self.player.position[0] + movement[0], self.player.position[1] - movement[1])
        new_x, new_y = final_position
        
        MIN_X, MAX_X = 0, 4
        MIN_Y, MAX_Y = 0, 8
        
        if (MIN_X <= new_x <= MAX_X) and (MIN_Y <= new_y <= MAX_Y): # Vérifie les limites de la map

            target_cell = self.map.get_current_mapping()[new_x, new_y]

            if target_cell is None:
                # si la case adjacente est vide on peut lancer le tirage
                print(f"Case vide à {final_position}. Lancement du tirage.")
                self.game_state = "DRAWING_ROOM"
                self.pending_placement_position = final_position
                self.draw_new_rooms()
            else:
                # si elle est déjà occupée avec une pièce on avance normalement
                print(f"Déplacement vers la case occupée {final_position}")
                self.player.move(final_position)
            # rajouter les vérifications de collisions etc plus tard

    def handle_room_selection(self, input):
        """
        Gère les inputs de la phase de sélection.
        """
        # même rôle que player movement mais pour la sélection de salle permet d'alléger un peu handle_inputs
        if input == "LEFT_ROOM":
            self.current_choice_index = (self.current_choice_index - 1) % 3 # permet de boucler (appuyer 1 fois sur droite revient à appuyer 2 fois sur gauche)
        elif input == "RIGHT_ROOM":
            self.current_choice_index = (self.current_choice_index + 1) % 3
        elif input == "ENTER":
            self.select_room_choice(self.current_choice_index)

    def handle_inputs(self, inputs):
        
        if self.game_state == "EXPLORING":
            direction_change=["UP","DOWN","LEFT","RIGHT"]
            movement_confirmation = ["SPACE"]

            for i in inputs:
                if i in direction_change:
                    self.player_orientation(i)
                
                if i in movement_confirmation:
                    self.player_movement(i)

        elif self.game_state == "DRAWING_ROOM":
            # marche de la même façon que pour l'exploration
            for i in inputs:
                if i in ["LEFT_ROOM", "RIGHT_ROOM", "ENTER"]:
                    self.handle_room_selection(i)
                    break

    def publish_data(self):
        """
        Donne toutes les données pertinnents pour l'affichage, a ajouter les nouvelles données ici.
        """
        self.data['position'] = self.player.position
        self.data['direction'] = self.player.direction
        self.data['mapping'] = self.map.get_current_mapping()
        # on rajoute game state pour que UI sache quel mode afficher
        self.data['game_state'] = self.game_state
        # on rajoute room choices (celles que le joueur peut choisir) pour l'affichage de l'UI
        self.data['room_choices'] = self.room_choices
        # on rajoute l'index de la salle actuellement sélectionnée pour l'affichage de l'UI (contours rouges)
        self.data['current_choice_index'] = self.current_choice_index
        return self.data
    
    def draw_new_rooms(self):
            """
            Tire 3 salles au hasard depuis le deck et les stocke.
            """
            # aléatoire très rudimentaire, à améliorer plus tard pour éviter les doublons, les cartes spéciales, 
            # pas toutes les cases payantes, les directions des cases bonnes ...
            chosen_room_classes = random.sample(self.room_deck, 3)
            self.room_choices = [RoomClass() for RoomClass in chosen_room_classes]
            # pour l'affichage dans l'UI
            self.data['room_choices'] = self.room_choices
            # mis à 0 pour commencer le choix depuis la salle de gauche
            self.current_choice_index = 0

    def select_room_choice(self, choice_index):
        # est appelée par handle_room_selection une fois que le joueur a fait son choix
        # chosen _room prend la valeur de la salle choisie
        chosen_room = self.room_choices[choice_index]
        self.map.place_room(chosen_room, self.pending_placement_position)
        self.player.move(self.pending_placement_position)
        # une fois la salle placée on remet l'état du jeu en exploration
        self.game_state = "EXPLORING"
        # on vide la liste pour les prochaines tirages
        self.room_choices = []
        self.pending_placement_position = None
    