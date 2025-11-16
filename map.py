import numpy as np
from room import *


class Map:
    '''
    Gère la grille 5x9 du manoir et le placement des salles.
    
    Cette classe contient la structure de données (un tableau NumPy) 
    qui représente la carte du jeu. Elle initialise la salle d'entrée 
    et de sortie et fournit des méthodes pour placer de nouvelles 
    salles et valider leur position.

    Attributes
    ----------
    mapping : numpy.ndarray
        Un tableau NumPy de 5x9 (shape (5,9)) de type `object`. 
        Chaque cellule contient soit `None`, soit une instance 
        de `RoomObject`.
    '''

    def __init__(self):
        '''
        Initialise la carte.
        
        Crée une grille 5x9 vide et y place 'EntryHall' (2,8) 
        et 'AnteChamber' (2,0).
        '''
        
        self.mapping =  np.empty((5,9), dtype=np.object_)
        self.mapping[2,8] = EntryHall()
        self.mapping[2,0] = AnteChamber()

    
    def place_room(self, room, position):
        '''
        Place une instance de salle sur la carte à une position donnée.

        Parameters
        ----------
        room : RoomObject
            L'instance de la salle (ex: `Aquarium()`) à placer.
        position : tuple
            Les coordonnées (x, y) où placer la salle.
        '''
        
        # position est un tuple (x, y)
        x, y = position
        self.mapping[x, y] = room
    

    def get_current_mapping(self):
        '''
        Retourne la grille actuelle de la carte.

        Returns
        -------
        numpy.ndarray
            Le tableau 5x9 `self.mapping` contenant l'état actuel 
            de la carte.
        '''
        
        return self.mapping
    
    def is_placement_valid(self, room_to_place, position):
        '''
        Vérifie si une salle (avec son orientation déjà définie) 
        peut être placée à une position donnée.
        
        La validité est déterminée en vérifiant la compatibilité des 
        portes avec les 4 voisins (murs de la grille ou autres salles).
        Une porte ne peut pas faire face à un mur (de grille ou 
        d'une autre salle), et une porte doit faire face à une autre porte.
        
        Parameters
        ----------
        room_to_place : RoomObject
            L'instance de la salle, *déjà orientée* (après rotation), 
            à tester.
        position : tuple
            Les coordonnées (x, y) du placement à tester.

        Returns
        -------
        bool
            True si le placement est valide (pas de conflits de portes), 
            False sinon.
        '''
        
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