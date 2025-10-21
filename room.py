
class RoomObject:
    """
    Room class, inheritance only, helps stock all rooms as needed
    """

    def __init__(self, name, image):
        self.name = name
        self.image = image
    

    def change_room_orientation():
        pass



class EntryHall(RoomObject):

    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png")
    


class Parlor(RoomObject):
    
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png")
    

class AnteChamber(RoomObject):

    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png") 


class Aquarium(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Aquarium.png")


class Attic(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Attic.png") 


class Ballroom(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Ballroom.png")


class Billiard_Room(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Billiard_Room.png") 


class Boiler_Room(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Boiler_Room.png")


class Chamber_of_Mirrors(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Chamber_of_Mirrors.png") 


class Closet(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Closet.png") 


class Coat_Check(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Coat_Check.png")


class Conference_Room(RoomObject):

    def __init__(self):
        super().__init__("Cloister", "Images/Rooms/Conference_Room.png") 