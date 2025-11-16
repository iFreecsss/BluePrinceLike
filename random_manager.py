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
    '''
    Gère tous les aspects aléatoires du jeu.
    
    Cette classe est responsable du tirage des salles (en respectant la rareté, 
    les contraintes de placement et les modificateurs), de l'assignation 
    des verrous aux portes (en fonction de la profondeur), et de la 
    génération du butin et des actions dans les salles (y compris le contenu 
    des coffres et des trous).

    Attributes
    ----------
    full_room_deck : list
        Liste complète de toutes les *classes* de salles disponibles dans le jeu.
    current_room_deck : list
        Pioche actuelle des salles. C'est une copie de `full_room_deck` qui 
        se vide à mesure que les salles sont placées (sauf si `allow_duplicates` est `True`).
    allow_duplicates : bool
        Si `True` (activé par "Chamber of Mirrors"), la pioche `current_room_deck` 
        n'est pas utilisée et les tirages se font depuis `full_room_deck`.
    hallways_are_unlocked : bool
        Si `True` (activé par "Foyer"), toutes les salles de type 'Hallway' 
        sont générées sans verrous.
    nursery_bonus_active : bool
        Flag pour le bonus de la "Nursery" (+5 Pas pour les futures "Bedroom").
    next_boudoir_bonus : bool
        Flag pour le bonus de "Her Ladyship's Chamber" sur le prochain "Boudoir".
    next_closet_bonus : bool
        Flag pour le bonus de "Her Ladyship's Chamber" sur le prochain "Closet".
    item_spawn_chance : float
        Chance de base (0.0 à 1.0) qu'une salle normale contienne des objets.
    type_weight_multipliers : dict
        Dictionnaire mappant `room_type` (str) à un multiplicateur (float).
        Modifie le poids de rareté lors du *tirage* d'une salle 
        (ex: `{'Red Room': 5.0}`).
    item_spawn_multipliers : dict
        Dictionnaire mappant `room_type` (str) à un multiplicateur (float).
        Modifie la *chance d'apparition d'objets* dans une salle 
        (ex: `{'Green Room': 2.0}`).
    room_action_pool : list
        Table de butin principale pour les objets/actions trouvés dans les salles.
        Format : [(RoomObject, poids), ...].
    room_actions : list
        Liste des `RoomObject` (actions) extraite de `room_action_pool`.
    action_weights : list
        Liste des poids (int) extraite de `room_action_pool`.
    chest_loot_pool : list
        Table de butin pour le contenu des "Chest" (Coffres).
    chest_loot_items : list
        Liste des `RoomObject` (items) extraite de `chest_loot_pool`.
    chest_loot_weights : list
        Liste des poids (int) extraite de `chest_loot_pool`.
    hole_loot_pool : list
        Table de butin pour le contenu des "Hole" (Trous).
    hole_loot_items : list
        Liste des `RoomObject` (items) extraite de `hole_loot_pool`.
    hole_loot_weights : list
        Liste des poids (int) extraite de `hole_loot_pool`.
    attic_loot_pool : list
        Table de butin spéciale pour la salle "Attic".
    attic_loot_items : list
        Liste des `RoomObject` (items) extraite de `attic_loot_pool`.
    attic_loot_weights : list
        Liste des poids (int) extraite de `attic_loot_pool`.
    '''
    
    def __init__(self):
        # doit contenir les classes des salles et non les instances
        self.full_room_deck = [
            Aquarium, Attic, Ballroom, Billiard_Room, 
            Boiler_Room, Chamber_of_Mirrors, Closet, 
            Coat_Check, Conference_Room, Parlor, Security, 
            Foyer, Kitchen, Dining_Room, Passageway, Master_Bedroom,
            Bedroom, Chapel, Weight_Room, Office, Patio, Greenhouse,
            Furnace, Maids_Chamber, Veranda, The_Pool, Terrace,
            Boudoir, Guest_Bedroom, Her_Ladyships_Chamber, Nursery,
            Rotunda, Secret_Garden, Secret_Passage, Servants_Quarters,
            Corridor, East_Wing_Hall, Hallway, West_Wing_Hall, Commissary, 
            Walkin_Closet, Cloister
        ]
        

        # la pioche qui se vide
        self.current_room_deck = self.full_room_deck.copy()
        
        # par défaut le jeu retire les pièces de la pioche : pas de doublons
        self.allow_duplicates = False
        
        # par défaut les couloirs ont des serrures normales
        self.hallways_are_unlocked = False
        
        self.nursery_bonus_active = False
        self.next_boudoir_bonus = False
        self.next_closet_bonus = False
        
        self.item_spawn_chance = 0.6
        
        
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
    

        # Toutes les actions possibles qu'une salle peut contenir
        
        self.room_action_pool = [
            (room_Apple, 20),
            (room_Banana, 15),
            (room_Dice, 5),
            (room_Key, 10),
            (room_Chest, 5),
            (room_Hole, 5),
            (room_Coin, 10), 
            (room_Diamond, 5)
        ]

        self.room_actions = [item[0] for item in self.room_action_pool]
        self.action_weights = [item[1] for item in self.room_action_pool]

        self.chest_loot_pool = [
            (room_Apple, 10),
            (room_Banana, 10),
            (room_Diamond, 10), # (action, proba)
            (room_Key, 15),
            (room_Dice, 15),
            (room_Shovel, 40), # la pelle ne peut apparaître que dans un coffre ou casier plus tard
            (room_Coin, 20),
            (room_charm_chroma, 5),
            (room_metal_detector, 5),
            (room_hammer, 5),
            (room_lock_picking_kit, 5)
        ]

        self.chest_loot_items = [item[0] for item in self.chest_loot_pool]
        self.chest_loot_weights = [item[1] for item in self.chest_loot_pool]

        self.hole_loot_pool = [
            (room_Apple, 10),
            (room_Banana, 10),
            (room_Diamond, 10), # (action, proba)
            (room_Key, 15),
            (room_Dice, 15),
            (room_Coin, 20),
            (room_charm_chroma, 10),
            (room_metal_detector, 5),
            (room_hammer, 5),
            (room_lock_picking_kit, 5)
        ]

        self.hole_loot_items = [item[0] for item in self.hole_loot_pool]
        self.hole_loot_weights = [item[1] for item in self.hole_loot_pool]
        
        # pour la salle ATTIC
        self.attic_loot_pool = [
            (room_Key, 20),
            (room_Diamond, 20),
            (room_Coin, 20),
            (room_Chest, 15),
            (room_hammer, 5),
            (room_charm_chroma, 5),
            (room_metal_detector, 5),
            (room_lock_picking_kit, 5),
            (room_Shovel, 5)
        ]
        self.attic_loot_items = [item[0] for item in self.attic_loot_pool]
        self.attic_loot_weights = [item[1] for item in self.attic_loot_pool]

    def is_room_placable(self, RoomClass, current_map, position, direction_of_entry):
        '''
        Vérifie si une Classe de salle peut être légalement placée à une position.
        
        Teste les 4 rotations possibles pour la salle. Pour être plaçable, 
        au moins une rotation doit permettre l'entrée par `direction_of_entry` 
        ET être compatible avec les voisins (`current_map.is_placement_valid`).
        Vérifie également les contraintes de placement (ex: 'WEST', 'INDOOR').

        Parameters
        ----------
        RoomClass : class
            La *classe* de la salle à tester (ex: `Attic`), pas une instance.
        current_map : Map
            L'instance `Map` actuelle du jeu.
        position : tuple
            Tuple (x, y) de la case de placement visée.
        direction_of_entry : int
            Entier (0-3) de la direction par laquelle le joueur doit entrer 
            dans la nouvelle salle.

        Returns
        -------
        bool
            `True` si au moins une des 4 rotations est valide, `False` sinon.
        '''
        # Vérification des contraintes de placement
        x, y = position
        constraints = RoomClass.placement_constraints
        
        # la carte fait 5 de large (0 à 4)
        if constraints == "WEST":
            if x > 1: # Doit être dans les colonnes 0 ou 1
                return False
        elif constraints == "EAST":
            if x < 3: # Doit être dans les colonnes 3 ou 4
                return False
        elif constraints == "INDOOR":
            if x != 2: # Doit être dans la colonne 2 (milieu)
                return False
        
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
        '''
        Tire 'count' salles (par défaut 3) salles garanties d'être plaçables et 
        les retourne comme instances.
        
        Filtre la pioche (`current_room_deck` ou `full_room_deck`) pour ne 
        garder que les salles plaçables (via `is_room_placable`).
        Applique les poids de rareté et les `type_weight_multipliers`.
        Garantit qu'au moins une salle gratuite (coût 0) est proposée si possible.
        Crée les 3 instances et leur assigne des verrous (via `assign_locks_to_room`).

        Parameters
        ----------
        current_map : Map
            L'instance `Map` actuelle du jeu.
        position : tuple
            Tuple (x, y) de la case de placement visée.
        direction_of_entry : int
            Entier (0-3) de la direction par laquelle le joueur doit entrer.

        Returns
        -------
        list
            Une liste de 3 *instances* `RoomObject` prêtes à être proposées.
        '''
        
        # On choisit la liste source en fonction de l'effet
        if self.allow_duplicates:
            # effet "Chamber of Mirrors" est actif : on pioche dans la liste complète
            source_deck = self.full_room_deck
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
            
            # On assigne les blocages en fonction de la ligne (pos_y)
            self.assign_locks_to_room(instance, pos_y)
            chosen_instances.append(instance)
            
        return chosen_instances

    def calculate_lock_level(self, y_coordinate):
        '''
        Calcule un niveau de verrouillage (0, 1, ou 2) basé sur la profondeur.
        
        Utilise la table `LOCK_PROB` pour déterminer la probabilité 
        d'un verrou de niveau 1 ou 2 en fonction de la coordonnée y.
        La ligne 8 (départ) est toujours 0, la ligne 0 (fin) est toujours 2.

        Parameters
        ----------
        y_coordinate : int
            La coordonnée y (ligne) de la salle.

        Returns
        -------
        int
            Le niveau de verrouillage (0, 1, ou 2).
        '''
        
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
        '''
        Applique les niveaux de verrouillage calculés à une instance de salle.
        
        Pour chaque sortie de base (`base_exits`) de la salle, 
        appelle `calculate_lock_level` et applique le résultat.
        Gère les exceptions (ex: "Corridor" toujours ouvert, ou 
        l'effet `hallways_are_unlocked`).

        Parameters
        ----------
        room_instance : RoomObject
            L'instance de salle qui vient d'être créée (avant d'être proposée).
        y_coordinate : int
            La coordonnée y où la salle sera placée, utilisée pour 
            `calculate_lock_level`.
        '''
        for base_direction in room_instance.base_exits:
            lock_level = self.calculate_lock_level(y_coordinate)
            
            # vérifie d'abord si c'est un Corridor
            if room_instance.name == "Corridor":
                lock_level = 0
            
            # si l'effet Foyer est actif et que c'est un Hallway, on force le déverrouillage
            if self.hallways_are_unlocked and room_instance.room_type == 'Hallway':
                lock_level = 0
            
            room_instance.set_exit_lock(base_direction, lock_level)
    
    def remove_room_from_deck(self, room_class_to_remove):
        '''
        Retire une classe de salle de la pioche `current_room_deck`.
        
        Ne fait rien si l'effet de la Chamber of Mirrors `self.allow_duplicates` 
        est `True`.

        Parameters
        ----------
        room_class_to_remove : class
            La *classe* de la salle qui a été choisie et placée par le joueur.
        '''
        
        # Si l'effet est actif, on ne fait rien, la pièce reste.
        if self.allow_duplicates:
            return

        # Sinon on retire la pièce de la pioche
        if room_class_to_remove in self.current_room_deck:
            self.current_room_deck.remove(room_class_to_remove)

    def assign_inventories_to_room(self, room_instance: RoomObject, player):
        '''
        Assigne un inventaire d'actions/objets aléatoire à une salle.
        
        Gère les salles spéciales (`Attic`, `Closet`, etc.) qui ont un 
        nombre d'objets garanti et/ou des tables de butin spéciales.
        Pour les salles normales, la chance d'apparition et le nombre d'objets 
        sont déterminés par `item_spawn_chance`, `item_spawn_multipliers` 
        et les bonus du joueur (`Charm Chroma`, `Metal Detector`).
        Si une action de type conteneur (ex: "Chest") est générée, 
        appelle `generate_random_loot_inventory` pour la remplir.

        Parameters
        ----------
        room_instance : RoomObject
            L'instance de la salle qui vient d'être placée sur la carte.
        player : Player
            L'instance du joueur (pour vérifier les bonus d'objets).
        '''
        
        room_name = room_instance.name
        source_pool_items = None
        source_pool_weights = None
        num_items_to_spawn = 0

        # gére les salles spéciales avec nombre d'objets garanti
        if room_name == "Closet":
            num_items_to_spawn = 2
            source_pool_items = self.room_actions
            source_pool_weights = self.action_weights.copy()
        elif room_name == "Walkin_Closet":
            num_items_to_spawn = 4
            source_pool_items = self.room_actions
            source_pool_weights = self.action_weights.copy()
        elif room_name == "Attic":
            num_items_to_spawn = 8
            source_pool_items = self.attic_loot_items # Utilise le pool spécial
            source_pool_weights = self.attic_loot_weights.copy()
        elif room_name == "Locker_Room":
            num_items_to_spawn = random.randint(3, 5) # Une salle pleine de casiers
            source_pool_items = [room_locker]
            source_pool_weights = [1]
        else:
            # gére les salles normales
            base_spawn_chance = self.item_spawn_chance
            type_multiplier = self.item_spawn_multipliers.get(room_instance.room_type, 1.0)
            
            charm_multiplier = 1.0
            actions_weights = [50, 30, 20]
            actions_choices = [2, 3, 4]

            if player.inventory.get_quantity("Charm Chroma") > 0: 
                charm_multiplier = 1.5
                actions_weights = [30, 40, 30]
                actions_choices = [3, 4, 5]

            final_spawn_chance = base_spawn_chance * type_multiplier * charm_multiplier
            final_spawn_chance = min(final_spawn_chance, 1.0)
            
            if random.random() >= final_spawn_chance:
                return # pas d'objets pour cette salle
            
            num_items_to_spawn = random.choices(actions_choices, weights=actions_weights, k=1)[0]
            source_pool_items = self.room_actions
            source_pool_weights = self.action_weights.copy()

        # appliquer les bonus détecteur de Métal
        current_action_weights = source_pool_weights
        if player.inventory.get_quantity("Metal Detector") > 0:
            metal_detector_multiplier = 2.0
            # on utilise try/except au cas où le pool ne contiendrait pas ces items
            try:
                key_index = source_pool_items.index(room_Key)
                current_action_weights[key_index] *= metal_detector_multiplier
            except ValueError:
                pass # le pool ne contient pas de clé
            try:
                coin_index = source_pool_items.index(room_Coin)
                current_action_weights[coin_index] *= metal_detector_multiplier
            except ValueError:
                pass # le pool ne contient pas de pièce

        #créer l'inventaire et générer le butin
        new_RoomInventory = RoomInventory()
        chosen_actions = random.choices(
            source_pool_items,
            weights=current_action_weights, 
            k=num_items_to_spawn
        )

        for action in chosen_actions:
            
            new_action_copy = copy.deepcopy(action)
            if new_action_copy.name == "Nothing":
                continue
            if new_action_copy.name == "Chest":
                loot_inv = self.generate_random_loot_inventory(player, "Chest")
                new_action_copy.item = loot_inv
            elif new_action_copy.name == "Hole":
                loot_inv = self.generate_random_loot_inventory(player, "Hole")
                new_action_copy.item = loot_inv
            elif new_action_copy.name == "Locker":
                loot_inv = self.generate_random_loot_inventory(player, "Locker")
                new_action_copy.item = loot_inv

            new_RoomInventory.addInventory(new_action_copy)
        
        # Assigne ce nouvel inventaire à la salle
        if len(room_instance.inventories.inventory) != 0: #Si la chambre a déjà un inventaire, on skip.
            pass
        else:
            room_instance.inventories = new_RoomInventory

    def generate_random_loot_inventory(self, player, type_of_contenent):
        '''
        Crée un inventaire de butin (pour un coffre, un trou, ou un casier).
        
        Tire 2-3 objets de la table de butin appropriée (`chest_loot_pool` 
        ou `hole_loot_pool`). Gère les objets non consommables (ne les donne 
        pas si le joueur les a déjà) et assure qu'au moins un objet 
        est généré (évite les conteneurs vides).

        Parameters
        ----------
        player : Player
            L'instance du joueur (pour éviter les doublons d'objets uniques).
        type_of_contenent : str
            "Chest", "Hole", ou "Locker". Détermine la table de butin 
            et la chance d'être vide.

        Returns
        -------
        Inventory
            Un objet `Inventory` (de `inventory.py`, *pas* `RoomInventory`) 
            contenant les objets de butin (`Item`).
        '''
        loot_inventory = Inventory()
        
        # Le coffre contiendra entre 1 et 3 items
        num_items = random.randint(2, 3) 

        # Ajout d'une chance que le trou soit vide (j'ai vu ça dans l'énoncé)
        if type_of_contenent in ["Hole", "Locker"]:
            empty_chance = 0.15
            if random.random() < empty_chance:
                return loot_inventory

        if type_of_contenent == "Hole":
            loot = self.hole_loot_items
            weights = self.hole_loot_weights
        if type_of_contenent == "Chest":
            loot = self.chest_loot_items
            weights = self.chest_loot_weights
        if type_of_contenent == "Locker":
            # le casier utilise le même pool que le coffre
            loot = self.chest_loot_items
            weights = self.chest_loot_weights

        items_to_add = random.choices(
            loot,
            weights=weights,
            k=num_items
        )
        
        added_items = 0

        for item in items_to_add:
            
            # On copie l'Item contenu dans le RoomObject
            item_copy = copy.deepcopy(item.item) 
            
            if isinstance(item_copy, NonConsumableItem):
                # On vérifie l'inventaire du joueur
                if player.inventory.get_quantity(item_copy.name) == 0: 
                    item_copy.quantity = 1
                    loot_inventory.add_item(item_copy)
                    added_items += 1

            elif item_copy.name in ["Diamond", "Key", "Dice", "Apple", "Banana", "Coin"]:
                item_copy.quantity = random.randint(1, 2)
                loot_inventory.add_item(item_copy)
                added_items += 1
            
        # Si après la boucle on n'a rien ajouté
        if added_items == 0:
            
            # On crée un pool de secours sans la pelle
            consumable_pool = []
            consumable_weights = []

            
            for i, item in enumerate(loot):
                if not isinstance(item.item, NonConsumableItem):
                    consumable_pool.append(item)
                    consumable_weights.append(weights[i])

            # On tire un item de secours
            if consumable_pool: 
                backup_item = random.choices(consumable_pool, weights=consumable_weights, k=1)[0]
                item_copy = copy.deepcopy(backup_item.item)
                item_copy.quantity = random.randint(1, 2) 
                loot_inventory.add_item(item_copy)
            
        return loot_inventory
