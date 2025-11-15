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

        self.player.inventory.add_item(player_Diamond.return_item_with_amount(10))
        self.player.inventory.add_item(player_Key.return_item_with_amount(150))
        self.player.inventory.add_item(player_Footsteps.return_item_with_amount(70))
        self.player.inventory.add_item(player_Dice.return_item_with_amount(6))
        self.player.inventory.add_item(player_Coin.return_item_with_amount(100))
        #self.player.inventory.add_item(
            #ConsumableItem("Dice", "Images/Icons/dice_icon.png", 5))
        #self.player.inventory.add_item(shovel.return_item_with_amount(1))
        
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

        # pour la gestion des confirmations d'actions (ex: ouvrir un coffre)
        self.pending_confirmation = None
        # rajout de la gestion des confirmations d'ouverture de porte
        self.pending_door_confirmation = None

        # pour la gestion des items au sol
        self.current_floor_item_index = 0
        #index de l'action choisie
        self.action_index = 0
        self.possible_actions = 0
        self.action_messages = []

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
        
        if lock_level !=0:
            
            if self.player.inventory.get_quantity("Lock Picking Kit")>0:
                lock_level -= 1
        
            # si le kit suffit à ouvrir la porte
            if lock_level == 0:
                self.warning_message = "You picked the lock with your Lock Picking Kit!"
                current_room.unlock_exit(direction)
                if target_room is not None:
                    opposite_direction = (direction + 2) % 4
                    target_room.unlock_exit(opposite_direction)
            else:
                # on vérifie si le joueur a assez de clés sans les utiliser tout de suite
                keys_needed = player_Key.return_item_with_amount(lock_level)
                if self.player.use(keys_needed, test=True):
                    # Demande de confirmation
                    self.game_state = "DOOR_CONFIRMATION"
                    # On stocke les infos pour quand le joueur dira "Oui"
                    self.pending_door_confirmation = {
                        "direction": direction,
                        "lock_level": lock_level,
                        "target_room": target_room,
                        "final_position": final_position
                    }
                    return
                else:
                    # le joueur n'a pas de clé
                    if lock_level == 1:
                        self.warning_message = f"This door is locked. You need {lock_level} key."
                    elif lock_level == 2:
                        self.warning_message = f"This door is double-locked. You need {lock_level} keys."
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
            if self.player.use(player_Footsteps.return_item_with_amount(1)):
                # si elle est déjà occupée avec une pièce on avance normalement
                self.player.move(final_position)
                
                new_room = self.map.get_current_mapping()[self.player.position] # la salle où on vient d'arriver
                new_room.on_entry(self) # On déclenche son effet d'entrée (self = game_logic)
                
                self.check_game_status() # on vérifie si on a gagné ou perdu
            else:
                self.check_game_over()

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

    def handle_action_index(self, given_input):
        if given_input == "ARROW_UP":
            self.action_index = max(0,self.action_index-1)
        
        if given_input == "ARROW_DOWN":
            self.action_index = min(self.possible_actions - 1,self.action_index+1)
        
        if given_input == "SPACE":
            self.action_index = 0
        
        if given_input == "ENTER":
            if self.action_index > self.possible_actions - 1:
                self.action_index = self.possible_actions - 1

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
            #self.handle_possible_actions() #Regarde le nombre d'action possibles

            direction_change=["UP","DOWN","LEFT","RIGHT"]
            movement_confirmation = ["SPACE"]

            for i in inputs:
                if i in direction_change:
                    self.player_orientation(i)
                
                if i in movement_confirmation:
                    self.player_movement(i)
                    self.handle_action_index(i)
            
            
            #Rajout de handle des objets et des inventaires.
            action_selection=["ARROW_UP","ARROW_DOWN"]
            action_confirmation = ["ENTER"]

            current_room = self.map.get_current_mapping()[self.player.position]
            inventory = current_room.inventories
            self.possible_actions = inventory.get_action_number()

            for i in inputs:
                if i in action_selection:
                    self.handle_action_index(i) #Modifie l'index de l'action
                if i in action_confirmation:
                    action_result = inventory.handle_action(self.player,self.action_index) # force à false par défaut
                    if isinstance(action_result, tuple) and action_result[0] == "CONFIRM":
                        # L'action a besoin d'une confirmation
                        self.game_state = "ACTION_CONFIRMATION"
                        # On stocke l'index de l'action et le message
                        self.pending_confirmation = {
                            "index": self.action_index,
                            "message": action_result[1]
                        }
                        self.current_choice_index = 0 # Par défaut sur oui
                    else:
                        # Sinon c'est que c'est une action normale donc pas de confirmation nécessaire
                        self.warning_message = action_result
                        self.possible_actions = inventory.get_action_number()
                        self.handle_action_index(i) # Reset l'index
                        
            if "ROTATE_ROOM" in inputs:
                # on récupère la salle actuelle
                current_room = self.map.get_current_mapping()[self.player.position]
                
                # on vérifie si c'est bien une Rotunda
                if isinstance(current_room, Rotunda):
                    # on effectue la rotation
                    current_room.rotate_walls()
                    self.warning_message = "The gears grind... The room rotates clockwise!"
                    # on joue un son mécanique si vous en avez un, sinon on peut réutiliser footsteps ou dice
                    self.sound_to_play = 'rotate'
                else:
                    # Feedback si le joueur appuie sur T dans une autre salle
                    self.warning_message = "Nothing happens."
            
        elif self.game_state == "DRAWING_ROOM":
            # marche de la même façon que pour l'exploration
            for i in inputs:
                if i in ["LEFT_ROOM", "RIGHT_ROOM", "ENTER", "SPACE"]:
                    self.handle_room_selection(i)
                    break
                elif i == "REROLL":
                    self.handle_reroll()
                    break
        elif self.game_state == "DOOR_CONFIRMATION":
            for i in inputs:
                if i in ["LEFT_ROOM", "RIGHT_ROOM", "ENTER", "SPACE"]:
                    self.handle_door_confirmation(i)
                    break # On ne traite qu'un input de confirmation à la fois

        elif self.game_state == "ACTION_CONFIRMATION":
            for i in inputs:
                if i in ["LEFT_ROOM", "RIGHT_ROOM", "ENTER", "SPACE"]:
                    self.handle_confirmation(i)
                    break # On ne traite qu'un input de confirmation à la fois



        elif self.game_state == "COLLECTING_ITEMS":
            #Pour le débug, on apparente le game_state COLLECTING_ITEMS à EXPLORING
            self.game_state = "EXPLORING"
            pass
        
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

        if self.player.use(player_Dice.return_item_with_amount(1)):
            self.warning_message = "You used 1 Dice to reroll room choices."
            self.sound_to_play = 'reroll'
            self.draw_new_rooms()
        else:
            self.warning_message = "You don't have any Dice to reroll."

    def handle_confirmation(self, input):
        """Gère les confirmations d'actions (ex: ouvrir un coffre)"""
        if input == "LEFT_ROOM":
            self.current_choice_index = 0 # oui
        elif input == "RIGHT_ROOM":
            self.current_choice_index = 1 # Non
        elif input == "ENTER":
            # Le joueur a confirmé son choix
            
            if self.current_choice_index == 0: # oui
                action_index = self.pending_confirmation["index"]
                current_room = self.map.get_current_mapping()[self.player.position]
                # On appelle à nouveau handle_action mais en forçant l'exécution
                self.warning_message = current_room.inventories.handle_action(self.player, action_index, force=True)
            else: # "NON"
                self.warning_message = "Chest opening aborted"

            # On nettoie et on retourne à l'exploration
            self.game_state = "EXPLORING"
            self.pending_confirmation = None
            current_room = self.map.get_current_mapping()[self.player.position]
            self.possible_actions = current_room.inventories.get_action_number()
            self.action_index = 0

    def handle_door_confirmation(self, input):
        """Gère les confirmations d'ouverture de porte"""
        if input == "LEFT_ROOM":
            self.current_choice_index = 0 # oui
        elif input == "RIGHT_ROOM":
            self.current_choice_index = 1 # Non
        elif input in ["ENTER", "SPACE"]:
            # Le joueur a confirmé son choix
            pending_data = self.pending_door_confirmation
            
            if self.current_choice_index == 0: # oui
                # Récupérer les données stockées 
                direction = pending_data["direction"]
                lock_level = pending_data["lock_level"]
                target_room = pending_data["target_room"]
                final_position = pending_data["final_position"]
                current_room = self.map.get_current_mapping()[self.player.position]

                #Essayer d'utiliser les clés
                key_to_use = player_Key.return_item_with_amount(lock_level)
                if self.player.use(key_to_use, test=False):
                    self.warning_message = f"You used {lock_level} key(s) to unlock the door."
                    
                    # Déverrouiller les portes
                    current_room.unlock_exit(direction)
                    if target_room is not None:
                        opposite_direction = (direction + 2) % 4
                        target_room.unlock_exit(opposite_direction)

                    # déplacer ou tirer la nouvelle pièce
                    if target_room is None:
                        # La case est vide => tire une nouvelle salle.
                        self.sound_to_play = 'new_room'
                        self.game_state = "DRAWING_ROOM"
                        self.pending_placement_position = final_position
                        # On calcule la direction d'entrée (opposée à la direction de mouvement)
                        self.pending_entry_direction = (direction + 2) % 4
                        self.draw_new_rooms()
                        # On ne déplace pas le joueur car select_room_choice s'en chargera.
                    
                    else:
                        # La case contient une salle existante donc on se déplace normalement
                        self.sound_to_play = 'footsteps'
                        if self.player.use(player_Footsteps.return_item_with_amount(1)):
                            self.player.move(final_position)
                            # new_room est simplement le target_room qu'on connait déjà
                            new_room = target_room
                            new_room.on_entry(self)
                            self.check_game_status()
                        else:
                            self.check_game_over()
                else:
                    # normalement ne devrait jamais arriver car on a déjà testé avant la confirmation
                    self.warning_message = "You don't have enough keys after all."
            
            else: # non
                self.warning_message = "You decided not to open the door."

            # Si on n'est pas passé en mode tirage, on retourne à l'exploration
            if self.game_state not in ["DRAWING_ROOM", "VICTORY", "GAME_OVER"]:
                self.game_state = "EXPLORING"
                
            self.pending_door_confirmation = None   
            self.action_index = 0
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

        # confirmation d'action
        self.data['pending_confirmation'] = self.pending_confirmation
        self.data['pending_door_confirmation'] = self.pending_door_confirmation
        # items dans la salle
        current_room = self.map.get_current_mapping()[self.player.position]
        self.data['roomactions'] = current_room.inventories.get_action_messages()
        self.data['action_index'] = self.action_index
        self.data['inventory_items'] = self.player.inventory.get_all_items()
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
                print(f"ERROR: No room from the deck can be placed at {self.pending_placement_position}!")
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
            self.check_game_over()
            return
        if player_diamonds >= room_cost:
            # Le joueur peut payer en diamants et en pas

            self.player.use(player_Diamond.return_item_with_amount(room_cost))
            # On applique l'effet "on_draft" AVANT de payer le pas
            chosen_room.on_draft(self)
            self.player.use(player_Footsteps.return_item_with_amount(1))

            # On récupère la direction d'entrée mémorisée
            entry_dir = self.pending_entry_direction
            # On déverrouille cette porte sur la nouvelle pièce
            chosen_room.unlock_exit(entry_dir)
            
            #AJOUT DE l'INVENTAIRE
            self.random_manager.assign_inventories_to_room(chosen_room, self.player)
            ######################

            self.map.place_room(chosen_room, placement_pos)
            self.player.move(placement_pos)
            
            # on retire cette pièce de la pioche si allow_duplicates est False
            self.random_manager.remove_room_from_deck(chosen_room.__class__)
            
            # On déclenche l'effet d'entrée de la pièce qu'on vient de placer
            chosen_room.on_entry(self)
            
            self.check_game_status()
            
            if self.game_state != "VICTORY":

                self.game_state = "EXPLORING"
                self.room_choices = []
                self.pending_placement_position = None
        else:
            # Le joueur ne peut pas payer
            self.warning_message = f"Not enough diamonds ! You need {room_cost - player_diamonds} more."
            # On ne change pas d'état, le joueur reste sur l'écran de choix
    
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
            print(f"Critical Error: Room '{room.name}' has no valid rotation.")
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
            self.sound_to_play = "victory"
            return
        
    def check_game_over(self):
        """
        Vérifie si le joueur a perdu.
        La défaite survient à 0 pas, SEULEMENT s'il n'y a plus
        d'objets donnant des pas (Pomme, Banane) à ramasser
        dans la salle actuelle.
        """
        # si le jeu est déjà gagné ou perdu, on ne fait rien
        if self.game_state in ["VICTORY", "GAME_OVER"]:
            return

        current_steps = self.player.inventory.get_quantity("Footsteps")
        
        if current_steps <= 0:
            # verification des objets dispo dans la salle du joueur
            current_room = self.map.get_current_mapping()[self.player.position]
            room_inventory_list = current_room.inventories.inventory
            
            step_item_available = False
            for room_action in room_inventory_list:
                
                if room_action.name in ["Apple", "Banana"]:
                    step_item_available = True
                    break
            
            if not step_item_available:
                # 0 pas et aucune pomme/banane à ramasser = GAME OVER
                self.game_state = "GAME_OVER"
                self.sound_to_play = "game_over"
            else:
                # 0 pas mais il y a des objets à ramasser
                self.warning_message = "You are out of steps! You must collect the items in this room."