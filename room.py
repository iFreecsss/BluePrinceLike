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
    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", base_exits=[0,1,3])

class AnteChamber(RoomObject):
    rarity = 'common' 
    cost = 0
    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png", base_exits=[1,2,3]) 

class Aquarium(RoomObject):
    rarity = 'uncommon'
    cost = 1
    def __init__(self):
        super().__init__("Aquarium", "Images/Rooms/Aquarium.png", base_exits=[1,2,3])

class Attic(RoomObject):
    rarity = 'common' 
    cost = 3
    def __init__(self):
        super().__init__("Attic", "Images/Rooms/Attic.png", base_exits=[2]) 

class Ballroom(RoomObject):
    rarity = 'uncommon'
    cost = 2
    def __init__(self):
        super().__init__("Ballroom", "Images/Rooms/Ballroom.png", base_exits=[0,2])

class Bedroom(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Ballroom", "Images/Bedrooms/Bedroom.png", base_exits=[1,2])
        
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
    def __init__(self):
        super().__init__("Billiard_Room", "Images/Rooms/Billiard_Room.png", base_exits=[1,2]) 

class Boiler_Room(RoomObject):
    rarity = 'uncommon'
    cost = 1
    def __init__(self):
        super().__init__("Boiler_Room", "Images/Rooms/Boiler_Room.png", base_exits=[1,2,3])

class Chamber_of_Mirrors(RoomObject):
    rarity = 'rare'
    cost = 0
    def __init__(self):
        super().__init__("Chamber_of_Mirrors", "Images/Rooms/Chamber_of_Mirrors.png", base_exits=[2]) 

class Closet(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Closet", "Images/Rooms/Closet.png", base_exits=[2]) 

class Coat_Check(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Coat_Check", "Images/Rooms/Coat_Check.png", base_exits=[2])

class Conference_Room(RoomObject):
    rarity = 'uncommon'
    cost = 0
    def __init__(self):
        super().__init__("Conference_Room", "Images/Rooms/Conference_Room.png", base_exits=[1,2,3])

class Chapel(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Conference_Room", "Images/Red Rooms/Chapel.png", base_exits=[1,2,3])
    
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
    def __init__(self):
        super().__init__("Dining_Room", "Images/Rooms/Dining_Room.png", base_exits=[1,2,3])

class Foyer(RoomObject):
    rarity = 'uncommon'
    cost = 2
    def __init__(self):
        super().__init__("Foyer", "Images/Hallways/Foyer.png", base_exits=[0,2])

class Kitchen(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Kitchen", "Images/Shops/Kitchen.png", base_exits=[1,2])

class Master_Bedroom(RoomObject):
    rarity = 'rare'
    cost = 2
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

class Weight_Room(RoomObject):
    rarity = 'rare'
    cost = 0
    def __init__(self):
        super().__init__("Master_Bedroom", "Images/Red Rooms/Weight_Room.png", base_exits=[0,1,2,3])
    
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

class Parlor(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", base_exits=[1,2])

class Passageway(RoomObject):
    rarity = 'common'
    cost = 2
    def __init__(self):
        super().__init__("Passageway", "Images/Hallways/Passageway.png", base_exits=[0,1,2,3])

class Security(RoomObject):
    rarity = 'rare'
    cost = 1
    def __init__(self):
        super().__init__("Security", "Images/Rooms/Security.png", base_exits=[1,2,3])