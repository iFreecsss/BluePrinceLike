from player import *
from map import *
from room import *
from random_manager import * 

class Game:

    def __init__(self):
        self.player = Player()
        self.map = Map()
        self.data = {}

        # les pioches se retrouvent ici
        self.random_manager = RandomManager()

        # test implémentation tirage des pièces
        # il y aura 2 modes. celui qui permet de se déplcacer librement 'EXPLORING' et celui qui oblige
        #  à placer les pièces 'ROOM_DRAWING'
        self.game_state = 'EXPLORING'
        # stocke les 3 pièces à choisir
        self.current_choice_index = 0
        self.room_choices = []
        # mémorise la position où placer la pièce choisie
        self.pending_placement_position = None

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

        # On regarde dans quelle salle on est actuellement
        current_room = self.map.get_current_mapping()[current_room_coords] 

        # On check si la salle choisie a une sortie dans la direction du déplacement
        if not current_room.has_exits(direction):
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
                self.game_state = "DRAWING_ROOM"
                self.pending_placement_position = final_position
                self.draw_new_rooms()
            else:
                # si elle est déjà occupée avec une pièce on avance normalement
                self.player.move(final_position)

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
            # Calculer la direction par laquelle le joueur va entrer
            # (Si le joueur va au Nord (0), il entre par le Sud (2) de la nouvelle pièce)
            must_enter_direction = (self.player.direction + 2) % 4
            
            # Utiliser le random_manager pour obtenir 3 pièces valides
            self.room_choices = self.random_manager.draw_placable_rooms(
                self.map, 
                self.pending_placement_position, 
                must_enter_direction
            )
            
            # Ne devrait jamais arriver mais on sait jamais
            if not self.room_choices:
                print(f"ERREUR: Aucune pièce du deck ne peut être placée à {self.pending_placement_position}!")
                self.game_state = "EXPLORING"
                self.pending_placement_position = None
                return
            
            # On pré-calcule la meilleure orientation pour chaque pièce
            # et on l'applique directement à l'instance.
            for room in self.room_choices:
                best_rot = self._find_best_rotation(
                    room, 
                    self.pending_placement_position, 
                    must_enter_direction
                )
                # On applique cette orientation
                room.change_room_orientation(best_rot)

            # Mise à jour pour l'UI
            self.data['room_choices'] = self.room_choices
            self.current_choice_index = 0

    def select_room_choice(self, choice_index):
        
        chosen_room = self.room_choices[choice_index]
        placement_pos = self.pending_placement_position
        
        self.map.place_room(chosen_room, placement_pos)
        self.player.move(placement_pos)
        
        # réinitialse l'état du jeu par défaut
        self.game_state = "EXPLORING"
        self.room_choices = []
        self.pending_placement_position = None
        
    def _find_best_rotation(self, room, position, must_enter_direction):
        """
        Trouve la meilleure rotation pour une pièce.
        Retourne l'entier de la rotation (0-3).
        C est une copie de l'ancienne fonction select_room_choice 
        mais elle retourne seulement la rotation.
        """
        valid_rotations = []
        
        # Ici on sait qu'au moins une rotation est valide mais mainteannt il s'agit de choisir la meilleure
        for rotation_attempt in range(4):
            room.change_room_orientation(rotation_attempt) # Modifie temporairement
            
            if not room.has_exits(must_enter_direction):
                continue 
            
            if self.map.is_placement_valid(room, position):
                valid_rotations.append(rotation_attempt) 
        
        # Réinitialise pour être propre avant de choisir
        room.change_room_orientation(0) 

        if not valid_rotations:
            # Normalement c'est pas possible mais on sait jamais
            print(f"Erreur critique: La pièce '{room.name}' n'a pas de rotation valide.")
            self.game_state = "EXPLORING"
            self.room_choices = []
            self.pending_placement_position = None
            return 0

        # Choix de la meilleure rotation
        best_rotation = valid_rotations[0] 
        has_found_north_exit = False

        for rotation in valid_rotations:
            room.change_room_orientation(rotation) # Re-modifie temporairement
            
            if room.has_exits(0): # Priorité au Nord (0)
                best_rotation = rotation
                has_found_north_exit = True
                break # On a trouvé le top
            elif not room.has_exits(2) and not has_found_north_exit: 
                # Sinon, on évite le Sud (2), mais on continue de chercher un Nord
                best_rotation = rotation
        
        room.change_room_orientation(0) # Réinitialise à nouveau
        return best_rotation