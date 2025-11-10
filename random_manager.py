import random
from room import *
from item import *
from inventory import *
from player import *
import copy
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
            Foyer, Kitchen, Dining_Room, Passageway, Master_Bedroom
        ]
        

        # Toutes les actions possibles qu'une salle peut contenir
        self.possible_room_actions = [
            room_Apple, room_Banana, room_Dice, room_Key, 
            room_Chest, room_Hole, room_None
        ]
    

        self.action_weights = [
            20, # Apple
            15, # Banana
            5, # Dice
            10, # Key
            5, # Chest
            5, # Hole
            30 # Rien
        ]
        
        self.chest_loot_pool = [
            (room_Apple, 10),
            (room_Banana, 10),
            (room_Diamond, 10), # (action, proba)
            (room_Key, 15),
            (room_Dice, 15),
            (room_Shovel, 40) # la pelle ne peut apparaître que dans un coffre ou casier plus tard
        ]

        self.chest_loot_items = [item[0] for item in self.chest_loot_pool]
        self.chest_loot_weights = [item[1] for item in self.chest_loot_pool]

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
        

        placable_free_rooms = [
            RoomClass for RoomClass in placable_room_classes 
            if RoomClass.cost == 0
        ]
        
        chosen_classes = []

        if not placable_free_rooms:
            # Si aucune pièce gratuite n'est dispo on tire juste 3 pièces normales pour éviter de crash
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
        else:
            # on récupère les poids des pièces dont le cost=0
            free_weights = [
                RARITY_WEIGHTS.get(RoomClass.rarity) 
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
                RARITY_WEIGHTS.get(RoomClass.rarity) 
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

    def assign_inventories_to_room(self, room_instance: RoomObject, player):
        """
        Assigne un inventaire d'ACTIONS aléatoire à une salle
        """
        
        # Crée un nouvel inventaire de salle vide
        new_room_inventory = Room_Inventory()
        
        # Décide combien d'actions la salle aura
        num_actions = random.randint(1, 3) 

        # Tire N actions aléatoires depuis notre pool d'objets
        chosen_actions = random.choices(
            self.possible_room_actions,
            weights=self.action_weights, 
            k=num_actions
        )

        # Ajoute ces actions à l'inventaire de la salle
        for action in chosen_actions:

            new_action_copy = copy.deepcopy(action)
            # Si l'action est "Nothing", on ne l'ajoute tout simplement pas
            # à la liste des actions de la salle.
            if new_action_copy.name == "Nothing":
                continue
            # Si l'action est un coffre, on génère son inventaire
            if new_action_copy.name == "Chest":
                # On génère un inventaire de butin aléatoire
                loot_inv = self.generate_random_loot_inventory(player)
                # On assigne cet inventaire à l'attribut item du coffre
                new_action_copy.item = loot_inv

            new_room_inventory.addInventory(new_action_copy)
        
        # Assigne ce nouvel inventaire à la salle
        room_instance.inventories = new_room_inventory

    def generate_random_loot_inventory(self, player):
        """
        Crée et retourne un nouvel objet Inventory() avec ressources random (pour chest et casier)
        """
        loot_inventory = Inventory()
        
        # Le coffre contiendra entre 1 et 3 items
        num_items = random.randint(2, 3) 
        
        items_to_add = random.choices(
            self.chest_loot_items,
            weights=self.chest_loot_weights,
            k=num_items
        )
        
        added_items = 0

        for item_template in items_to_add:
            
            # On copie l'Item contenu dans le RoomObject
            item_copy = copy.deepcopy(item_template.item) 
            
            if item_copy.name == "Shovel":
                # On vérifie l'inventaire du joueur
                if player.inventory.get_quantity("Shovel") == 0: 
                    item_copy.quantity = 1
                    loot_inventory.add_item(item_copy)
                    added_items += 1
                else:
                    # Le joueur a déjà une pelle
                    pass

            elif item_copy.name in ["Diamond", "Key", "Dice", "Apple", "Banana"]:
                item_copy.quantity = random.randint(1, 2)
                loot_inventory.add_item(item_copy)
                added_items += 1
            
        # Si après la boucle on n'a rien ajouté
        if added_items == 0:
            
            # On crée un pool de secours sans la pelle
            non_shovel_pool = []
            non_shovel_weights = []
            
            for i, item in enumerate(self.chest_loot_items):
                if item.name != "Shovel":
                    non_shovel_pool.append(item)
                    non_shovel_weights.append(self.chest_loot_weights[i])

            # On tire un item de secours
            if non_shovel_pool: 
                backup_item_template = random.choices(non_shovel_pool, weights=non_shovel_weights, k=1)[0]
                item_copy = copy.deepcopy(backup_item_template.item)
                item_copy.quantity = random.randint(1, 2) 
                loot_inventory.add_item(item_copy)
            
        return loot_inventory