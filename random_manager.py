import random
from room import *

# Définition des poids pour les raretés
RARITY_WEIGHTS = {
    'common': 10,
    'uncommon': 5,
    'rare': 2
}

class RandomManager:
    
    def __init__(self):
        # doit contenir les classes des salles et non les instances
        self.room_deck = [
            Aquarium, Attic, Ballroom, Billiard_Room, 
            Boiler_Room, Chamber_of_Mirrors, Closet, 
            Coat_Check, Conference_Room, Parlor
        ]
        
    def is_room_placable(self, RoomClass, current_map, position, direction_of_entry):
        """
        Vérifie si une *Classe* de pièce peut être placée.
        Teste les 4 rotations pour trouver au moins une orientation valide.
        """
        temp_room = RoomClass() # instance temporaire pour les tests de rotation
        
        for rotation in range(4):
            temp_room.change_room_orientation(rotation)
            
            # Check si la porte d'entrée existe avec cette rotation
            if not temp_room.has_exits(direction_of_entry):
                continue # Mauvaise rotation -> on teste la suivante directement
                
            # Check si la pièce n'est pas compatible avec ses voisins
            if current_map.is_placement_valid(temp_room, position):
                return True # Rotation valide trouvée
        
        return False # Aucune des 4 rotations n'est valide

    def draw_placable_rooms(self, current_map, position, direction_of_entry):
        """
        Tire 'count' salles (par défaut 3) qui sont *garanties* d'être plaçables
        à la 'position' donnée, en tenant compte de la 'direction_of_entry'.
        Prend en compte la rareté.
        """
        
        # Tri la liste complète pour garder que les pièces plaçables
        placable_room_classes = []
        for RoomClass in self.room_deck:
            if self.is_room_placable(RoomClass, current_map, position, direction_of_entry):
                placable_room_classes.append(RoomClass)
        
        if not placable_room_classes:
            # Cas horrible aucune pièce n'est plaçable normalement ça ne devrait jamais arriver
            return []
            
        # Préparer le tirage pondéré en fonction de la rareté
        weights = [
            RARITY_WEIGHTS.get(RoomClass.rarity) 
            for RoomClass in placable_room_classes
        ]
        
        # Là j'utilise .choices pour faire un tirage avec remise donc on a possiblement des doublons dans la 
        # même sélection de 3 pièces mais on peut utiliser .sample si on veut absolument pas de doublons
        # mais j'iame bien l'idée d'avoir des doublons possibles comme ça les salles rares sont vraiment rares
        chosen_classes = random.choices(
            placable_room_classes, 
            weights=weights, 
            k=3
        )

        # On retourne les 3 salles instanciées
        return [RoomClass() for RoomClass in chosen_classes]