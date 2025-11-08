import random
from room import *
from item import *

# Définition des poids pour les raretés
RARITY_WEIGHTS = {
    'common': 10,
    'uncommon': 5,
    'rare': 2
}

LOCK_PROB = {
    # Facile 
    7: (0.0, 0.20),  # 0% niv2, 20% niv1, 80% niv0
    6: (0.05, 0.25), # 5% niv2, 25% niv1, 70% niv0
    # Moyen
    5: (0.10, 0.30), # 10% niv2, 30% niv1, 60% niv0
    4: (0.15, 0.40), # 15% niv2, 40% niv1, 45% niv0
    3: (0.25, 0.35), # 25% niv2, 35% niv1, 40% niv0
    # Difficile
    2: (0.40, 0.30), # 40% niv2, 30% niv1, 30% niv0
    1: (0.50, 0.30)  # 50% niv2, 30% niv1, 20% niv0
}
class RandomManager:
    
    def __init__(self):
        # doit contenir les classes des salles et non les instances
        self.room_deck = [
            Aquarium, Attic, Ballroom, Billiard_Room, 
            Boiler_Room, Chamber_of_Mirrors, Closet, 
            Coat_Check, Conference_Room, Parlor, Security, 
            Foyer, Kitchen, Dining_Room, Passageway, Master_Bedroom,
            Bedroom, Chapel, Weight_Room, Office, Patio, Greenhouse,
            Furnace, Maids_Chamber, Veranda, The_Pool
        ]
        
        # la pioche qui se vide
        self.current_room_deck = self.room_deck.copy()
        
        # par défaut le jeu retire les pièces de la pioche : pas de doublons
        self.allow_duplicates = False
        
        self.item_spawn_chance = 0.6
        
        self.floor_items = [
            (Apple, 20),
            (Banana, 15),
            (Diamond, 10),
            (Key, 5),
            (Dice, 5)
        ]

        self.items_classes = [item[0] for item in self.floor_items]
        self.items_weights = [item[1] for item in self.floor_items]
        
        # Stocke les multiplicateurs de poids pour chaque type de salle
        # Par défaut, tout est à 1.0
        self.type_weight_multipliers = {
            'Red Room': 1.0,
            'Green Room': 1.0,
            'Shop': 1.0,
            'Bedroom': 1.0,
            'Room': 1.0,
            'Secret Room' : 1.0
        }
        
        # Stocke les multiplicateurs pour la CHANCE qu'une salle contienne des objets
        self.item_spawn_multipliers = {
            'Red Room': 1.0,
            'Green Room': 1.0,
            'Shop': 1.0,
            'Bedroom': 1.0,
            'Room': 1.0,
            'Hallway': 1.0,
            'Secret Room' : 1.0
        }
    
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
        
        # On choisit la liste source en fonction de l'effet
        if self.allow_duplicates:
            # effet "Chamber of Mirrors" est actif : on pioche dans la liste complète
            source_deck = self.room_deck
        else:
            # comportment normal : on pioche dans la liste qui se vide
            source_deck = self.current_room_deck
        
        # Tri la liste complète pour garder que les pièces plaçables
        placable_room_classes = []
        for RoomClass in source_deck:
            if self.is_room_placable(RoomClass, current_map, position, direction_of_entry):
                placable_room_classes.append(RoomClass)
        
        if not placable_room_classes:
            # Cas horrible aucune pièce n'est plaçable normalement ça ne devrait jamais arriver
            return []
        
        # Fonction pour calculer le poids final d'une pièce
        def get_weighted_rarity(RoomClass):
            base_weight = RARITY_WEIGHTS.get(RoomClass.rarity, 10)
            type_multiplier = self.type_weight_multipliers.get(RoomClass.room_type, 1.0)
            return base_weight * type_multiplier

        placable_free_rooms = [
            RoomClass for RoomClass in placable_room_classes 
            if RoomClass.cost == 0
        ]
        
        chosen_classes = []

        if not placable_free_rooms:
            # Si aucune pièce gratuite n'est dispo on tire juste 3 pièces normales pour éviter de crash
            weights = [
                get_weighted_rarity(RoomClass) 
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
        else:
            # on récupère les poids des pièces dont le cost=0
            free_weights = [
                get_weighted_rarity(RoomClass) 
                for RoomClass in placable_free_rooms
                ]

            # Pièce gratuite garantie (on en tire que 1)
            guaranteed_free_room = random.choices(
                placable_free_rooms, 
                weights=free_weights, 
                k=1
            )
            # .extend pour éviter de créer une liste dans une liste
            chosen_classes.extend(guaranteed_free_room)
            
            # On récupère tous les poids des pièces quelque soit leur cost
            all_weights = [
                get_weighted_rarity(RoomClass)
                for RoomClass in placable_room_classes
                ]
            # Parmi toutes les pièces (y compris les cost=0) on en tire 2 autres
            other_rooms = random.choices(
                placable_room_classes, 
                weights=all_weights, 
                k=2
            )
            chosen_classes.extend(other_rooms)
            
            # Mélange pour ne pas avoir la pièce gratuite toujours en première position
            random.shuffle(chosen_classes)
        pos_x, pos_y = position 
        
        chosen_instances = []

        for RoomClass in chosen_classes:
            instance = RoomClass()
            
            base_spawn_chance = self.item_spawn_chance # la chance de base globale
            
            # le multiplicateur spécifique au type de cette salle
            type_multiplier = self.item_spawn_multipliers.get(instance.room_type, 1.0)
            
            final_spawn_chance = base_spawn_chance * type_multiplier # calcule de la chance finale
            final_spawn_chance = min(final_spawn_chance, 1.0) # on s'assure que la chance ne dépasse pas 100%
            
            if random.random() < final_spawn_chance:
                
                num_items_to_spawn = random.choices([2,3,4], weights=[50,30,20], k=1)[0]

                for _ in range(num_items_to_spawn):
                    # Tirage d'un objet à faire apparaître au sol
                    item_class_to_spawn = random.choices(
                        self.items_classes,
                        weights=self.items_weights,
                        k=1
                    )[0]
                    item_instance = item_class_to_spawn()

                    if isinstance(item_instance, (Diamond, Key, Dice)):
                        item_instance.quantity = random.choices([1,2,5], weights=[74,25,1], k=1)[0]
                    instance.add_item_to_floor(item_instance)
                    
            # On assigne les blocages en fonction de la ligne (pos_y)
            self.assign_locks_to_room(instance, pos_y)
            chosen_instances.append(instance)
            
        return chosen_instances

    def calculate_lock_level(self, y_coordinate):
        """
        Calcule le niveau de blocage (0, 1, ou 2)
        basé sur la ligne (y) de la carte.
        """
        # 1ère ligne -> niveau 0
        if y_coordinate == 8:
            return 0
        
        # Dernière -> niveau 2
        if y_coordinate == 0:
            return 2
        
        # Lignes 1 à 7 -> probabilités croissantes
        prob_level_2, prob_level_1 = LOCK_PROB.get(y_coordinate, (0.0, 0.0))
        
        roll = random.random() # Un float entre 0 et 1
        
        if roll < prob_level_2:
            return 2 # Fermé à double tour
        elif roll < (prob_level_2 + prob_level_1):
            return 1 # Fermé à clé
        else:
            return 0 # Ouvert
        
    def assign_locks_to_room(self, room_instance, y_coordinate):
        """
        Applique les niveaux de blocage à toutes les sorties de base d'une instance de salle.
        """
        for base_direction in room_instance.base_exits:
            lock_level = self.calculate_lock_level(y_coordinate)
            room_instance.set_exit_lock(base_direction, lock_level)
    
    def remove_room_from_deck(self, room_class_to_remove):
        """
        Retire une pièce de la pioche actuelle (current_room_deck), 
        sauf si l'effet de la Chamber of Mirrors (allow_duplicates) est actif.
        """
        # Si l'effet est actif, on ne fait rien, la pièce reste.
        if self.allow_duplicates:
            return

        # Sinon on retire la pièce de la pioche
        if room_class_to_remove in self.current_room_deck:
            self.current_room_deck.remove(room_class_to_remove)