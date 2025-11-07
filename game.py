from player import *
from map import *
from room import *
from random_manager import * 
from item import *

class Game:

    def __init__(self):
        self.player = Player()
        self.map = Map()
        self.data = {}
        
        self.warning_message = None

        self.player.inventory.add_item(
            ConsumableItem("Diamond", "Images/Icons/diamond_icon.png", 10))
        self.player.inventory.add_item(
            ConsumableItem("Key", "Images/Icons/key_icon.png", 15))
        self.player.inventory.add_item(
            ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 70))
        self.player.inventory.add_item(
            ConsumableItem("Dice", "Images/Icons/dice_icon.png", 5))
        self.player.inventory.add_item(
            ConsumableItem("Coin", "Images/Icons/coin_icon.png", 20))
        
        
        # les pioches se retrouvent ici
        self.random_manager = RandomManager()

        # test implémentation tirage des pièces
        # il y aura 2 modes. celui qui permet de se déplcacer librement 'EXPLORING' et celui qui oblige
        #  à placer les pièces 'ROOM_DRAWING'
        self.game_state = 'EXPLORING'
        self._previous_game_state = 'EXPLORING'

        # stocke les 3 pièces à choisir
        self.current_choice_index = 0
        self.room_choices = []

        # mémorise la position où placer la pièce choisie
        self.pending_placement_position = None

        # mémorise la direction par laquelle on entre
        self.pending_entry_direction = None

        # pour la gestion des items au sol
        self.current_floor_item_index = 0

        # params audio
        self.sound_to_play = None
        self.music_volume = 0.4
        self.effects_volume = 0.7
        self.is_music_muted = False
        self.is_effects_muted = False

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
            self.warning_message = "Hey ! No door that way !"
            return
        
        # attention nécessaire de connaître la salle cible avant de vérifier la serrure
        # afin de déverrouiller les deux côtés de la porte
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
        
        target_room = None

        # On vérifie si la position cible est sur la carte
        if (MIN_X <= new_x <= MAX_X) and (MIN_Y <= new_y <= MAX_Y):
            # On récupère la salle cible (peut être None si la case est vide)
            target_room = self.map.get_current_mapping()[final_position]
        else:
            # Le joueur essaie de se déplacer hors de la carte.
            # has_exits devrait déjà bloquer ça, mais c'est une sécurité.
            self.warning_message = "You can't go that way."
            return
        
        # On vérifie le niveau de blocage de la porte dans cette direction
        lock_level = current_room.get_lock_level(direction)
        
        if lock_level == 1:
            # Porte fermée normale (Niveau 1)
            # Si assez de clés
            if self.player.inventory.use_consumable("Key", 1):
                self.warning_message = "You used 1 key to unlock the door."
                current_room.unlock_exit(direction)
                if target_room is not None:
                    opposite_direction = (direction + 2) % 4
                    target_room.unlock_exit(opposite_direction)
            else:
                self.warning_message = "This door is locked. You need 1 key."
                return # Bloqué
        
        elif lock_level == 2:
            # Porte fermée double tours (Niveau 2)
            if self.player.inventory.get_quantity("Key") >= 2:
                self.player.inventory.use_consumable("Key", 2)
                self.warning_message = "You used 2 keys to unlock the door."
                current_room.unlock_exit(direction) # On déverrouille
                if target_room is not None:
                    opposite_direction = (direction + 2) % 4
                    target_room.unlock_exit(opposite_direction)
            else:
                self.warning_message = "This door is double-locked. You need 2 keys."
                return # Bloqué
        
        # Si on arrive ici, c'est que la porte était de niveau 0 ou vient d'être déverrouillée
        
        if target_room is None:
            self.sound_to_play = 'new_room'
            # si la case adjacente est vide on peut lancer le tirage
            self.game_state = "DRAWING_ROOM"
            self.pending_placement_position = final_position

            # On mémorise la direction par laquelle le joueur va entrer
            # (Si le joueur va au Nord (0), il entre par le Sud (2) de la nouvelle pièce)
            self.pending_entry_direction = (self.player.direction + 2) % 4
            self.draw_new_rooms()
        else:
            self.sound_to_play = 'footsteps'
            if self.player.inventory.use_consumable("Footsteps", 1):
                # si elle est déjà occupée avec une pièce on avance normalement
                self.player.move(final_position)
                
                new_room = self.map.get_current_mapping()[self.player.position] # la salle où on vient d'arriver
                new_room.on_entry(self) # On déclenche son effet d'entrée (self = game_logic)
                
                self.check_game_status() # on vérifie si on a gagné ou perdu
            else:
                # Si plus de pas faudra implémenter le game over
                self.warning_message = "GAME OVER !"

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
        self.sound_to_play = None

        #si le jeu est gagné ou perdu ya pas d'inputs
        if self.game_state in ["VICTORY", "GAME_OVER"]:
            return
        


        if "TOGGLE_SETTINGS" in inputs:
            if self.game_state == "SETTINGS":
                self.game_state = self._previous_game_state # Retour au jeu
            else:
                self._previous_game_state = self.game_state
                self.game_state = "SETTINGS"
            return

        # Si on est en mode SETTINGS on utilise que les inputs de settings
        if self.game_state == "SETTINGS":
            for i in inputs:
                if isinstance(i, tuple): # Les inputs de settings sont des tuples (command, value)
                    command, value = i
                    if command == "SET_MUSIC_VOLUME":
                        self.music_volume = value
                        self.is_music_muted = False
                    elif command == "SET_EFFECTS_VOLUME":
                        self.effects_volume = value
                        self.is_effects_muted = False
                    elif command == "TOGGLE_MUSIC_MUTE":
                        self.is_music_muted = not self.is_music_muted
                    elif command == "TOGGLE_EFFECTS_MUTE":
                        self.is_effects_muted = not self.is_effects_muted
            return

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
                elif i == "REROLL":
                    self.handle_reroll()
                    break

        elif self.game_state == "COLLECTING_ITEMS":
            current_room = self.map.get_current_mapping()[self.player.position]
            items_on_floor = current_room.get_items_on_floor()

            # si on est dans cet état mais qu'il n'y a pas d'objets, on sort
            if not items_on_floor:
                self.game_state = "EXPLORING"
                return

            num_items = len(items_on_floor)

            for i in inputs:
                if i == "LEFT_ROOM":
                    self.current_floor_item_index = (self.current_floor_item_index - 1) % num_items
                elif i == "RIGHT_ROOM":
                    self.current_floor_item_index = (self.current_floor_item_index + 1) % num_items
                elif i == "ENTER":
                    # Retirer l'objet de la liste de la salle
                    # pop() le récupère ET le supprime de la liste en même temps
                    item_to_collect = items_on_floor.pop(self.current_floor_item_index)
                    
                    # Appliquer son effet
                    item_to_collect.collect(self)
                    
                    # Afficher le message de collecte
                    item_name = item_to_collect.name
                    if hasattr(item_to_collect, 'quantity') and item_to_collect.quantity > 1:
                        item_name = f"{item_to_collect.quantity} {item_to_collect.name}(s)"
                    elif item_to_collect.name in ["Apple", "Banana"]:
                         item_name = f"1 {item_to_collect.name}"
                    self.warning_message = f"You collected {item_name}!"
                    
                    # Vérifier s'il reste des objets
                    if not items_on_floor:
                        # S'il n'y en a plus retour à l'exploration
                        self.game_state = "EXPLORING"
                    else:
                        # S'il en reste on doit ajuster l'index
                        self.current_floor_item_index = min(self.current_floor_item_index, len(items_on_floor) - 1)
                    
                    # On arrête de traiter les inputs pour ce frame
                    break

    def handle_reroll(self):
        """Tente de relancer le tirage des pièces en utilisant un dé"""

        if self.player.inventory.use_consumable("Dice", 1):
            self.warning_message = "You used 1 Dice to reroll room choices."
            self.sound_to_play = 'reroll'
            self.draw_new_rooms()
        else:
            self.warning_message = "You don't have any Dice to reroll."

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
        self.data['warning_message'] = self.warning_message
        self.warning_message = None # on le réinitialise pour l'envoyé qu'une seule fois
        self.data['inventory_items'] = self.player.inventory.get_all_items()
        
        # items au sol dans la salle actuelle
        self.data['items_on_floor'] = []
        if self.data['game_state'] == "COLLECTING_ITEMS":
            current_room = self.map.get_current_mapping()[self.player.position]
            self.data['items_on_floor'] = current_room.get_items_on_floor()
            self.data['current_floor_item_index'] = self.current_floor_item_index
        # données audio
        self.data['sound_to_play'] = self.sound_to_play
        self.data['music_volume'] = self.music_volume
        self.data['effects_volume'] = self.effects_volume
        self.data['is_music_muted'] = self.is_music_muted
        self.data['is_effects_muted'] = self.is_effects_muted
        return self.data
    
    def draw_new_rooms(self):
            # on récupère la direction d'entrée mémorisée et on rappelle :
            # Calculer la direction par laquelle le joueur va entrer
            # (Si le joueur va au Nord (0), il entre par le Sud (2) de la nouvelle pièce)
            must_enter_direction = self.pending_entry_direction
            
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
                best_rot = self.find_best_rotation(
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
        room_cost = chosen_room.cost
        
        # On vérifie si le joueur a assez de diamants
        player_diamonds = self.player.inventory.get_quantity("Diamond")
        player_footsteps = self.player.inventory.get_quantity("Footsteps")

        # si plus de pas game over 
        if player_footsteps <= 0:
            # faudra implementer le game over et donc le changement d'état de jeu ici aussi 
            self.warning_message = "GAME OVER !"
            return
        if player_diamonds >= room_cost:
            # Le joueur peut payer en diamants et en pas
            self.player.inventory.use_consumable("Diamond", room_cost)
            self.player.inventory.use_consumable("Footsteps", 1)

            # On récupère la direction d'entrée mémorisée
            entry_dir = self.pending_entry_direction
            # On déverrouille cette porte sur la nouvelle pièce
            chosen_room.unlock_exit(entry_dir)

            self.map.place_room(chosen_room, placement_pos)
            self.player.move(placement_pos)
            
            # On déclenche l'effet d'entrée de la pièce qu'on vient de placer
            chosen_room.on_entry(self)
            
            self.check_game_status()
            
            if self.game_state != "VICTORY":
                self.check_for_room_items(chosen_room)
                if self.game_state != "COLLECTING_ITEMS":
                    # Si on n'est pas passé en mode collecte d'items

                    # réinitialse l'état du jeu par défaut
                    self.game_state = "EXPLORING"
                self.room_choices = []
                self.pending_placement_position = None
        else:
            # Le joueur ne peut pas payer
            self.warning_message = f"Not enough diamonds ! You need {room_cost - player_diamonds} more."
            # On ne change pas d'état, le joueur reste sur l'écran de choix

    def check_for_room_items(self, room):
        """
        Vérifie si la salle contient des objets au sol.
        Si oui, change l'état du jeu en mode collecte d'objets.
        """
        if room.name in ["Entrance_Hall", "AnteChamber"]:
            # Ces salles ne contiennent pas d'objets
            return
        if room.get_items_on_floor():
            # True si la salle contient des objets au sol
            self.game_state = "COLLECTING_ITEMS"
            self.current_floor_item_index = 0
    
    def find_best_rotation(self, room, position, must_enter_direction):
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
    
    def check_game_status(self):
        """
        Vérifie si le jeu est gagné ou perdu.
        """
        VICTORY_POSITION = (2, 0)
        
        if self.player.position == VICTORY_POSITION:
            self.game_state = "VICTORY"
            return
        
        # faudra rajouter la condition de défaite