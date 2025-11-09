from inventory import *

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
        self.inventories = Room_Inventory()

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
    
    def get_inventories(self):
        return self.inventories.get_inventories()

class EntryHall(RoomObject):
    rarity = 'common' 
    cost = 0
    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", base_exits=[0,1,3])
    
class Parlor(RoomObject):
    rarity = 'common'
    cost = 0
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", base_exits=[1,2])
    
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


class Dining_Room(RoomObject):
    rarity = 'common'
    cost = 2
    def __init__(self):
        super().__init__("Dining_Room", "Images/Rooms/Dining_Room.png", base_exits=[1,2,3])

class Security(RoomObject):
    rarity = 'rare'
    cost = 1
    def __init__(self):
        super().__init__("Security", "Images/Rooms/Security.png", base_exits=[1,2,3])

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

class Passageway(RoomObject):
    rarity = 'common'
    cost = 2
    def __init__(self):
        super().__init__("Passageway", "Images/Hallways/Passageway.png", base_exits=[0,1,2,3])

class Foyer(RoomObject):
    rarity = 'uncommon'
    cost = 2
    def __init__(self):
        super().__init__("Foyer", "Images/Hallways/Foyer.png", base_exits=[0,2])