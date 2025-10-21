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
        
        chosen_room = self.room_choices[choice_index]
        placement_pos = self.pending_placement_position
        
        # la direction par laquelle on entre
        # par exmeple si le joueur va au Nord (0), il entre par le Sud (2) de la nouvelle pièce
        must_enter = (self.player.direction + 2) % 4
        
        valid_rotations = []
        
        # on cherche toutes les rotations valides puis on choisit la meilleure après
        for rotation_attempt in range(4):
            chosen_room.change_room_orientation(rotation_attempt)
            
            # si la pièce ne connecte pas, on passe à la rotation suivante
            if not chosen_room.has_exits(must_enter):
                continue 

            # la rotation est bonne avec la pièce d'origine mais il faut check les futurs voisins
            if self.is_placement_valid(chosen_room, placement_pos):
                valid_rotations.append(rotation_attempt) # si c'est le cas parfait, on l'ajoute aux rotations valides
        
        if not valid_rotations:
            # on pourra supprimer ça plus tard quand l'aléatoire sera mieux géré
            print(f"Échec: La pièce '{chosen_room.name}' ne peut pas être placée ici.")
            return
        
        # maintenant on choisit la 'meilleure' rotation parmi les valides c'est à dire une qui donne une porte vers le haut si possible
        best_rotation = valid_rotations[0]
        
        for rotation in valid_rotations:
            chosen_room.change_room_orientation(rotation)
            if chosen_room.has_exits(0): 
                best_rotation = rotation
                break # si on trouve une porte vers le nord on s'arrête là
        # sinon prend la première valide trouvée par défaut
        
        print(f"Placement valide trouvé (Rotation: {best_rotation})")
        chosen_room.change_room_orientation(best_rotation)
        
        self.map.place_room(chosen_room, placement_pos)
        self.player.move(placement_pos)
        
        # réinitialse l'état du jeu par défaut
        self.game_state = "EXPLORING"
        self.room_choices = []
        self.pending_placement_position = None

    def is_placement_valid(self, room_to_place, position):
        x, y = position
        current_mapping = self.map.get_current_mapping()
        
        neighbors_coords = [
            (0, (x, y - 1)),
            (1, (x - 1, y)), 
            (2, (x, y + 1)), 
            (3, (x + 1, y))  
        ]

        MIN_X, MAX_X = 0, 4
        MIN_Y, MAX_Y = 0, 8

        for (direction_vers_voisin, (nx, ny)) in neighbors_coords:
            
            # voisin = mur ?
            is_wall = not ((MIN_X <= nx <= MAX_X) and (MIN_Y <= ny <= MAX_Y))
            
            if is_wall:
                # si oui verifie que la pièce n'a pas de porte dans cette direction
                if room_to_place.has_exits(direction_vers_voisin):
                    return False
            else:
                # sinon c'est une case valide de la map
                neighbor_room = self.map.get_current_mapping()[nx, ny]
                
                if neighbor_room is not None:
                    # mais il peut s'agir d'une pièce existante, on doit vérifier la cohérence des portes
                    
                    # direction du voisin (opposée à celle de la pièce actuelle)
                    direction_du_voisin = (direction_vers_voisin + 2) % 4
                    
                    salle_actuelle_a_une_porte = room_to_place.has_exits(direction_vers_voisin)
                    voisin_a_une_porte = neighbor_room.has_exits(direction_du_voisin)
                    
                    if salle_actuelle_a_une_porte != voisin_a_une_porte:
                        return False
            
            # si le voisin est une case vide c'est toujours bon
            
        return True