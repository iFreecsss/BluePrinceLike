
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
    
    def __init__(self, name, image):
        super().__init__(name, image)
    

class AnteChamber(RoomObject):

    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png") 
