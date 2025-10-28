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
    
    def is_placement_valid(self, room_to_place, position):
        x, y = position
        
        # (Direction, (Voisin_X, Voisin_Y))
        neighbors_coords = [
            (0, (x, y - 1)), # NORD
            (1, (x - 1, y)), # OUEST
            (2, (x, y + 1)), # SUD
            (3, (x + 1, y)) # EST
        ]

        MIN_X, MAX_X = 0, 4
        MIN_Y, MAX_Y = 0, 8

        for (direction_vers_voisin, (nx, ny)) in neighbors_coords:
            
            # voisin = mur ?
            is_wall = not ((MIN_X <= nx <= MAX_X) and (MIN_Y <= ny <= MAX_Y))
            
            if is_wall:
                # Si c'est un mur -> la pièce ne doit PAS avoir de sortie dans cette direction
                if room_to_place.has_exits(direction_vers_voisin):
                    return False # porte vers un mur
            else:
                # Sinon la case est valide
                neighbor_room = self.get_current_mapping()[nx, ny]
                
                if neighbor_room is not None:
                    # case existante ? -> vérifier la cohérence des portes
                    
                    # Direction opposée (depuis le voisin vers la nouvelle pièce)
                    direction_du_voisin = (direction_vers_voisin + 2) % 4
                    
                    salle_actuelle_a_une_porte = room_to_place.has_exits(direction_vers_voisin)
                    voisin_a_une_porte = neighbor_room.has_exits(direction_du_voisin)
                    
                    # soit les 2 ont une porte, soit les 2 n'en ont pas
                    if salle_actuelle_a_une_porte != voisin_a_une_porte:
                        return False # porte vs mur de pièce
            
            # Si le voisin est une case vide alorws c'est toujours bon
            
        return True # tous les voisins sont cohérents