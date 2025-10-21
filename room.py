
class RoomObject:
    """
    Room class, inheritance only, helps stock all rooms as needed
    """

    def __init__(self, name, image, exits=None):
        self.name = name
        self.image = image
        self.exits = exits
        # NORD: 0; OUEST: 1; SUD: 2; EST: 3

    def has_exits(self, direction):
        return direction in self.exits
    

    def change_room_orientation():
        pass



class EntryHall(RoomObject):

    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", exits=[0,1,3])
    


class Parlor(RoomObject):
    
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", exits=[1,2])
    

class AnteChamber(RoomObject):

    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png", exits=[1,2,3]) 


class Aquarium(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Aquarium.png", exits=[1,2,3])


class Attic(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Attic.png", exits=[2]) 


class Ballroom(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Ballroom.png", exits=[0,2])


class Billiard_Room(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Billiard_Room.png", exits=[1,2]) 


class Boiler_Room(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Boiler_Room.png", exits=[1,2,3])


class Chamber_of_Mirrors(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Chamber_of_Mirrors.png", exits=[2]) 


class Closet(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Closet.png", exits=[2]) 


class Coat_Check(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Coat_Check.png", exits=[2])


class Conference_Room(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Conference_Room.png", exits=[1,2,3]) 