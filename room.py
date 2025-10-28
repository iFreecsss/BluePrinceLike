class RoomObject:
    """
    Room class, inheritance only, helps stock all rooms as needed
    """
    # Attribut de classe pour la rareté : common par défaut
    # Je les met ici pour qu'ils soient difficile changeable par erreur
    rarity = 'common'

    def __init__(self, name, image, base_exits=None):
        self.name = name
        self.image = image
        self.base_exits = base_exits
        # NORD: 0; OUEST: 1; SUD: 2; EST: 3
        self.orientation = 0

    def has_exits(self, direction):

        # dictionnaires de rotation triog et horraire
        MAP_TURN_LEFT = { 0: 1, 1: 2, 2: 3, 3: 0 }
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        
        original_drection_to_check = direction
        for _ in range(self.orientation):
            original_drection_to_check = MAP_TURN_RIGHT[original_drection_to_check]
            
        return original_drection_to_check in self.base_exits

    def change_room_orientation(self, rotation):
        # définition de l'orientation de la salle
        self.orientation = rotation % 4


class EntryHall(RoomObject):
    rarity = 'common' 
    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", base_exits=[0,1,3])
    
class Parlor(RoomObject):
    rarity = 'common'
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", base_exits=[1,2])
    
class AnteChamber(RoomObject):
    rarity = 'common' 
    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png", base_exits=[1,2,3]) 

class Aquarium(RoomObject):
    rarity = 'uncommon'
    def __init__(self):
        super().__init__("Aquarium", "Images/Rooms/Aquarium.png", base_exits=[1,2,3])

class Attic(RoomObject):
    rarity = 'common' 
    def __init__(self):
        super().__init__("Attic", "Images/Rooms/Attic.png", base_exits=[2]) 

class Ballroom(RoomObject):
    rarity = 'uncommon'
    def __init__(self):
        super().__init__("Ballroom", "Images/Rooms/Ballroom.png", base_exits=[0,2])

class Billiard_Room(RoomObject):
    rarity = 'common'
    def __init__(self):
        super().__init__("Billiard_Room", "Images/Rooms/Billiard_Room.png", base_exits=[1,2]) 

class Boiler_Room(RoomObject):
    rarity = 'uncommon'
    def __init__(self):
        super().__init__("Boiler_Room", "Images/Rooms/Boiler_Room.png", base_exits=[1,2,3])

class Chamber_of_Mirrors(RoomObject):
    rarity = 'rare'
    def __init__(self):
        super().__init__("Chamber_of_Mirrors", "Images/Rooms/Chamber_of_Mirrors.png", base_exits=[2]) 

class Closet(RoomObject):
    rarity = 'common'
    def __init__(self):
        super().__init__("Closet", "Images/Rooms/Closet.png", base_exits=[2]) 

class Coat_Check(RoomObject):
    rarity = 'common'
    def __init__(self):
        super().__init__("Coat_Check", "Images/Rooms/Coat_Check.png", base_exits=[2])

class Conference_Room(RoomObject):
    rarity = 'uncommon'
    def __init__(self):
        super().__init__("Conference_Room", "Images/Rooms/Conference_Room.png", base_exits=[1,2,3])