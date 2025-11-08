from item import ConsumableItem
import numpy as np

class RoomObject:
    """
    Room class, inheritance only, helps stock all rooms as needed
    """
    # Attribut de classe pour la rareté : common par défaut
    # Je les met ici pour qu'ils soient difficile changeable par erreur
    rarity = 'common'
    cost = 0
    room_type = 'Room'

    def __init__(self, name, image, base_exits=None):
        self.name = name
        self.image = image
        self.base_exits = base_exits
        # NORD: 0; OUEST: 1; SUD: 2; EST: 3
        self.orientation = 0
        self.exit_locks = {}
        self.items_on_floor = []

    def has_exits(self, direction):

        # dictionnaires de rotation triog et horraire
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        
        original_drection_to_check = direction
        # exemple: si orientation = 1 alors en tournant 1 fois a droite on retrouve la direction originale
        # si c'est 3 alors on tourne 3 fois a droite pour retrouver la direction originale
        for _ in range(self.orientation):
            original_drection_to_check = MAP_TURN_RIGHT[original_drection_to_check]
            
        return original_drection_to_check in self.base_exits

    def change_room_orientation(self, rotation):
        # définition de l'orientation de la salle
        self.orientation = rotation % 4

    def set_exit_lock(self, base_direction, lock_level):
        """
        Appelé par le RandomManager pour définir le blocage initial
        d'une sortie de base (avant rotation).
        """
        if base_direction in self.base_exits:
            self.exit_locks[base_direction] = lock_level

    def get_original_direction(self, rotated_direction):
        """Fonction utilisée pour retrouver la direction originale 
        d'une sortie après rotation de la salle.
        Exemple: si la salle est tournée de 1 (90° horaire),
        une sortie "NORD" (0) devient "EST" (3). Pour retrouver
        la direction originale, on doit tourner 1 fois à gauche (270°).
        """
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        original_direction = rotated_direction

        for _ in range(self.orientation):
            original_direction = MAP_TURN_RIGHT[original_direction]
        return original_direction
    
    def get_lock_level(self, direction):
        """
        Récupère le niveau de blocage pour une direction après rotation
        """
        original_direction = self.get_original_direction(direction)
            
        # Renvoie le niveau de blocage (0 par défaut si non défini)
        return self.exit_locks.get(original_direction, 0)
    
    def unlock_exit(self, direction):
        """
        Déverrouille à jamais une porte (met son niveau à 0) pour une direction après rotation
        """
        original_direction = self.get_original_direction(direction)
        
        if original_direction in self.exit_locks:
            self.exit_locks[original_direction] = 0
            return True
        return False

    def add_item_to_floor(self, item):
        """
        Ajoute un objet au sol dans la salle.
        """
        self.items_on_floor.append(item)

    def get_items_on_floor(self):
        """
        Renvoie la liste des objets au sol dans la salle.
        """
        return self.items_on_floor
    
    def clear_items_on_floor(self):
        """
        Vide la liste des objets au sol dans la salle.
        """
        self.items_on_floor = []
    
    def on_entry(self, game_logic):
        """
        Applique un effet spécial lorsque le joueur entre dans la pièce.
        'game_logic' est l'instance principale de la classe Game.
        Par défaut, ne fait rien.
        """
        pass
    
    def on_draft(self, game_logic):
        """
        Applique un effet spécial lorsque le joueur choisit (draft) la pièce.
        'game_logic' est l'instance principale de la classe Game.
        Par défaut, ne fait rien.
        """
        pass

class EntryHall(RoomObject):
    rarity = 'common' 
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", base_exits=[0,1,3])

class AnteChamber(RoomObject):
    rarity = 'common' 
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png", base_exits=[1,2,3]) 

class Aquarium(RoomObject):
    rarity = 'uncommon'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Aquarium", "Images/Rooms/Aquarium.png", base_exits=[1,2,3])

class Attic(RoomObject):
    rarity = 'common' 
    cost = 3
    room_type = 'Room'
    def __init__(self):
        super().__init__("Attic", "Images/Rooms/Attic.png", base_exits=[2]) 

class Ballroom(RoomObject):
    rarity = 'uncommon'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Ballroom", "Images/Rooms/Ballroom.png", base_exits=[0,2])

class Bedroom(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Bedroom", "Images/Bedrooms/Bedroom.png", base_exits=[1,2])
        
    def on_entry(self, game_logic):
        """
        Donne +2 Pas (Footsteps) au joueur lorsqu'il entre.
        """
        game_logic.player.inventory.add_item(
            ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 2)
        )
        game_logic.warning_message = "You feel rested : +2 Footsteps!"

class Billiard_Room(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Billiard_Room", "Images/Rooms/Billiard_Room.png", base_exits=[1,2]) 

class Boiler_Room(RoomObject):
    rarity = 'uncommon'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Boiler_Room", "Images/Rooms/Boiler_Room.png", base_exits=[1,2,3])

class Chamber_of_Mirrors(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Chamber_of_Mirrors", "Images/Rooms/Chamber_of_Mirrors.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Active la possibilité de tirer des doublons de pièces
        en empêchant le retrait de la pioche.
        """
        game_logic.random_manager.allow_duplicates = True
        game_logic.warning_message = "The mirrors reflect reality. Duplicates are now possible!"

class Closet(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Closet", "Images/Rooms/Closet.png", base_exits=[2]) 

class Coat_Check(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Coat_Check", "Images/Rooms/Coat_Check.png", base_exits=[2])

class Conference_Room(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Conference_Room", "Images/Rooms/Conference_Room.png", base_exits=[1,2,3])

class Chapel(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Chapel", "Images/Red Rooms/Chapel.png", base_exits=[1,2,3])
    
    def on_entry(self, game_logic):
        """
        Retire 1 Pièce (Coin) au joueur s'il en a.
        """
        if game_logic.player.inventory.use_consumable("Coin", 1):
            game_logic.warning_message = "You pay tribute : -1 Coin."
        else:
            # L'effet s'active mais le joueur ne peut pas payer
            game_logic.warning_message = "Chapel demands tribute but you're poor."


class Dining_Room(RoomObject):
    rarity = 'common'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Dining_Room", "Images/Rooms/Dining_Room.png", base_exits=[1,2,3])

class Foyer(RoomObject):
    rarity = 'uncommon'
    cost = 2
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Foyer", "Images/Hallways/Foyer.png", base_exits=[0,2])

class Furnace(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Furnace", "Images/Red Rooms/Furnace.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Augmente la chance de tirer des Red Rooms.
        """
        # On multiplie par 5 la probabilité des Red Rooms
        game_logic.random_manager.type_weight_multipliers['Red Room'] *= 5.0
        game_logic.warning_message = "Heat spreads! More chance to draft Red Rooms."

class Greenhouse(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Greenhouse", "Images/Green Rooms/Greenhouse.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Augmente la chance de tirer des Green Rooms.
        """
        # On multiplie par 3 la probabilité des Green Rooms
        game_logic.random_manager.type_weight_multipliers['Green Room'] *= 3.0
        game_logic.warning_message = "The air feels fresher. More chance to draft Green Rooms."

class Kitchen(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Shop'
    def __init__(self):
        super().__init__("Kitchen", "Images/Shops/Kitchen.png", base_exits=[1,2])

class Locker_Room(RoomObject):
    rarity = 'rare'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Locker_Room", "Images/Rooms/Locker_Room.png", base_exits=[0,2])

class Maids_Chamber(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Red Room' #et Bedroom elle est les deux types
    def __init__(self):
        super().__init__("Maids_Chamber", "Images/Red Rooms/Maids_Chamber.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        """
        Réduit la probabilité de trouver des objets dans TOUTES les salles.
        """
        # On modifie la chance de base globale dans le random_manager : réduit de 25%
        current_chance = game_logic.random_manager.item_spawn_chance
        game_logic.random_manager.item_spawn_chance = current_chance * 0.75 
        game_logic.warning_message = "The maid tidies up. Item spawn chance reduced."

class Master_Bedroom(RoomObject):
    rarity = 'rare'
    cost = 2
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Master_Bedroom", "Images/Bedrooms/Master_Bedroom.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Donne +1 Pas (Footsteps) pour chaque pièce déjà placée sur la carte.
        """
        # np.count_nonzero() compte tous les éléments non-None dans la grille
        room_count = np.count_nonzero(game_logic.map.get_current_mapping())
        
        if room_count > 0:
            game_logic.player.inventory.add_item(
                ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", room_count)
            )
            game_logic.warning_message = f"Master Bedroom bonus: +{room_count} Footsteps!"

class Office(RoomObject):
    rarity = 'common'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Office", "Images/Rooms/Office.png", base_exits=[1,2])

class Parlor(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", base_exits=[1,2])

class Passageway(RoomObject):
    rarity = 'common'
    cost = 2
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Passageway", "Images/Hallways/Passageway.png", base_exits=[0,1,2,3])

class Patio(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Patio", "Images/Green Rooms/Patio.png", base_exits=[1,2])

class Pump_Room(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Pump_Room", "Images/Rooms/Pump_Room.png", base_exits=[1,2])

class Security(RoomObject):
    rarity = 'rare'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Security", "Images/Rooms/Security.png", base_exits=[1,2,3])

class Sauna(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Sauna", "Images/Rooms/Sauna.png", base_exits=[2])

class The_Pool(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("The_Pool", "Images/Rooms/The_Pool.png", base_exits=[1,2,3])
    
    def on_draft(self, game_logic):
        """
        Ajoute 3 nouvelles pièces (Sauna, Locker_Room, Pump_Room)
        à la pioche si elles n'y sont pas déjà.
        """
        rooms_to_add = [Sauna, Locker_Room, Pump_Room]
        
        full_deck = game_logic.random_manager.room_deck
        current_deck = game_logic.random_manager.current_room_deck
        added_rooms_names = []

        for room_class in rooms_to_add:
            # on les ajoute à la pioche principale si elles n'y sont pas
            if room_class not in full_deck:
                full_deck.append(room_class)
                added_rooms_names.append(room_class.__name__)
            
            # aussi à la pioche actuelle
            if room_class not in current_deck:
                current_deck.append(room_class)
        
        if added_rooms_names:
            game_logic.warning_message = f"New rooms added to the deck: {', '.join(added_rooms_names)}!"

class Veranda(RoomObject):
    rarity = 'uncommon'
    cost = 2
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Veranda", "Images/Green Rooms/Veranda.png", base_exits=[0,2])
    
    def on_draft(self, game_logic):
        """
        Augmente la probabilité de trouver des objets dans les Green Rooms.
        """
        # On modifie le multiplicateur spécifique aux "Green Room" : on double les chances
        current_multiplier = game_logic.random_manager.item_spawn_multipliers['Green Room']
        game_logic.random_manager.item_spawn_multipliers['Green Room'] = current_multiplier * 2.0
        game_logic.warning_message = "The garden flourishes! More items in Green Rooms."

class Weight_Room(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Weight_Room", "Images/Red Rooms/Weight_Room.png", base_exits=[0,1,2,3])
    
    def on_draft(self, game_logic):
        """
        Fait perdre la moitié des Pas actuels (arrondi à l'inférieur).
        """
        current_steps = game_logic.player.inventory.get_quantity("Footsteps")
        steps_to_lose = current_steps // 2 # Arrondi à l'inférieur
        
        if steps_to_lose > 0:
            game_logic.player.inventory.use_consumable("Footsteps", steps_to_lose)
            game_logic.warning_message = f"You feel exhausted : -{steps_to_lose} Footsteps!"
        else:
            game_logic.warning_message = "You feel exhausted but have no steps to lose."
