import numpy as np
from room import *


class Map:
    """
    Lists all possible rooms in the mansion and manages their interaction
    """

    def __init__(self):
        self.mapping =  np.empty((5,9), dtype=np.object_)
        self.mapping[2,8] = EntryHall()
        self.mapping[2,0] = AnteChamber()

    
    def place_room(self, room, position):
        # position est un tuple (x, y)
        x, y = position
        self.mapping[x, y] = room
    

    def get_current_mapping(self):
        return self.mapping