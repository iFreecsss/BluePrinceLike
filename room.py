from item import *
import numpy as np
from inventory import *
import random
import copy


class RoomObject:
    """
    Room class, inheritance only, helps stock all rooms as needed
    """
    # Attribut de classe pour la rareté : common par défaut
    # Je les met ici pour qu'ils soient difficile changeable par erreur
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    placement_constraints = None

    def __init__(self, name, image, base_exits=None):
        self.name = name
        self.image = image
        self.base_exits = base_exits
        # NORD: 0; OUEST: 1; SUD: 2; EST: 3
        self.orientation = 0
        self.exit_locks = {}
        self.items_on_floor = []
        self.inventories = Room_Inventory()

    def has_exits(self, direction):

        # dictionnaires de rotation triog et horraire
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        
        original_drection_to_check = direction
        # exemple: si orientation = 1 alors en tournant 1 fois a droite on retrouve la direction originale
        # si c'est 3 alors on tourne 3 fois a droite pour retrouver la direction originale
        for _ in range(self.orientation):
            original_drection_to_check = MAP_TURN_RIGHT[original_drection_to_check]
            
        return original_drection_to_check in self.base_exits

    def change_room_orientation(self, rotation):
        # définition de l'orientation de la salle
        self.orientation = rotation % 4

    def set_exit_lock(self, base_direction, lock_level):
        """
        Appelé par le RandomManager pour définir le blocage initial
        d'une sortie de base (avant rotation).
        """
        if base_direction in self.base_exits:
            self.exit_locks[base_direction] = lock_level

    def get_original_direction(self, rotated_direction):
        """Fonction utilisée pour retrouver la direction originale 
        d'une sortie après rotation de la salle.
        Exemple: si la salle est tournée de 1 (90° horaire),
        une sortie "NORD" (0) devient "EST" (3). Pour retrouver
        la direction originale, on doit tourner 1 fois à gauche (270°).
        """
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        original_direction = rotated_direction

        for _ in range(self.orientation):
            original_direction = MAP_TURN_RIGHT[original_direction]
        return original_direction
    
    def get_lock_level(self, direction):
        """
        Récupère le niveau de blocage pour une direction après rotation
        """
        original_direction = self.get_original_direction(direction)
            
        # Renvoie le niveau de blocage (0 par défaut si non défini)
        return self.exit_locks.get(original_direction, 0)
    
    def unlock_exit(self, direction):
        """
        Déverrouille à jamais une porte (met son niveau à 0) pour une direction après rotation
        """
        original_direction = self.get_original_direction(direction)
        
        if original_direction in self.exit_locks:
            self.exit_locks[original_direction] = 0
            return True
        return False
    
    def unlock_all_exits(self):
        """
        Force le déverrouillage (niveau 0) de toutes les portes de base de cette salle.
        Utile pour l'effet du Foyer.
        """
        for base_direction in self.base_exits:
            self.exit_locks[base_direction] = 0
    
    def add_item_to_floor(self, item):
        """
        Ajoute un objet au sol dans la salle.
        """
        self.items_on_floor.append(item)

    def get_items_on_floor(self):
        """
        Renvoie la liste des objets au sol dans la salle.
        """
        return self.items_on_floor
    
    def clear_items_on_floor(self):
        """
        Vide la liste des objets au sol dans la salle.
        """
        self.items_on_floor = []
    
    def on_entry(self, game_logic):
        """
        Applique un effet spécial lorsque le joueur entre dans la pièce.
        'game_logic' est l'instance principale de la classe Game.
        Par défaut, ne fait rien.
        """
        pass
    
    def on_draft(self, game_logic):
        """
        Applique un effet spécial lorsque le joueur choisit (draft) la pièce.
        'game_logic' est l'instance principale de la classe Game.
        Par défaut, ne fait rien.
        """
        # Si le bonus Nursery est actif ET que la pièce est une Bedroom
        if game_logic.random_manager.nursery_bonus_active and self.room_type == 'Bedroom':
            game_logic.player.inventory.add_item(
                ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 5)
                )
            # On ajoute au message existant (s'il y en a un)
            current_msg = game_logic.warning_message if game_logic.warning_message else ""
            game_logic.warning_message = f"{current_msg} Nursery bonus: +5 Footsteps!"
        
        pass
    
    def get_inventories(self):
        return self.inventories.get_inventories()

class EntryHall(RoomObject):
    rarity = 'common' 
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", base_exits=[0,1,3])

class AnteChamber(RoomObject):
    rarity = 'common' 
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png", base_exits=[1,2,3]) 

class Aquarium(RoomObject):
    rarity = 'uncommon'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Aquarium", "Images/Rooms/Aquarium.png", base_exits=[1,2,3])

class Attic(RoomObject):
    rarity = 'common' 
    cost = 3
    room_type = 'Room'
    def __init__(self):
        super().__init__("Attic", "Images/Rooms/Attic.png", base_exits=[2]) 

class Ballroom(RoomObject):
    rarity = 'uncommon'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Ballroom", "Images/Rooms/Ballroom.png", base_exits=[0,2])

class Bedroom(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Bedroom", "Images/Bedrooms/Bedroom.png", base_exits=[1,2])
        
    def on_entry(self, game_logic):
        """
        Donne +2 Pas (Footsteps) au joueur lorsqu'il entre.
        """
        game_logic.player.inventory.add_item(
            ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 2)
        )
        game_logic.warning_message = "You feel rested : +2 Footsteps!"

class Billiard_Room(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Billiard_Room", "Images/Rooms/Billiard_Room.png", base_exits=[1,2]) 

class Boiler_Room(RoomObject):
    rarity = 'uncommon'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Boiler_Room", "Images/Rooms/Boiler_Room.png", base_exits=[1,2,3])

class Boudoir(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Boudoir", "Images/Bedrooms/Boudoir.png", base_exits=[1,2])
    
    def on_entry(self, game_logic):
        # vérifie si le bonus est actif
        if game_logic.random_manager.next_boudoir_bonus:
            game_logic.player.inventory.add_item(
                ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 10)
            )
            game_logic.warning_message = "Her Ladyship's favor: \n+10 Footsteps in the Boudoir!"
            # désactive le bonus après utilisation
            game_logic.random_manager.next_boudoir_bonus = False

class Chamber_of_Mirrors(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Chamber_of_Mirrors", "Images/Rooms/Chamber_of_Mirrors.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Active la possibilité de tirer des doublons de pièces
        en empêchant le retrait de la pioche.
        """
        game_logic.random_manager.allow_duplicates = True
        game_logic.warning_message = "The mirrors reflect reality. Duplicates are now possible!"

class Closet(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Closet", "Images/Rooms/Closet.png", base_exits=[2])
    
    def on_entry(self, game_logic):
        # vérifie si le bonus est actif
        if game_logic.random_manager.next_closet_bonus:
            game_logic.player.inventory.add_item(
                ConsumableItem("Diamond", "Images/Icons/diamond_icon.png", 3)
            )
            game_logic.warning_message = "Found Her Ladyship's stash: +3 Gems in the Closet!"
            # désactive le bonus après utilisation
            game_logic.random_manager.next_closet_bonus = False

class Coat_Check(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Coat_Check", "Images/Rooms/Coat_Check.png", base_exits=[2])

class Conference_Room(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Conference_Room", "Images/Rooms/Conference_Room.png", base_exits=[1,2,3])

class Chapel(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Chapel", "Images/Red Rooms/Chapel.png", base_exits=[1,2,3])
    
    def on_entry(self, game_logic):
        """
        Retire 1 Pièce (Coin) au joueur s'il en a.
        """
        if game_logic.player.inventory.get_quantity("Coin") >= 1:
            game_logic.player.use(player_Coin.return_item_with_amount(1))
            game_logic.warning_message = "You pay tribute : -1 Coin."
        else:
            # L'effet s'active mais le joueur ne peut pas payer
            game_logic.warning_message = "Chapel demands tribute but you're poor."

class Corridor(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Corridor", "Images/Hallways/Corridor.png", base_exits=[0,2])

class Dining_Room(RoomObject):
    rarity = 'common'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Dining_Room", "Images/Rooms/Dining_Room.png", base_exits=[1,2,3])

class East_Wing_Hall(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Hallway'
    placement_constraints = 'EAST'
    def __init__(self):
        super().__init__("East_Wing_Hall", "Images/Hallways/East_Wing_Hall.png", base_exits=[1,2,3])

class Foyer(RoomObject):
    rarity = 'uncommon'
    cost = 2
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Foyer", "Images/Hallways/Foyer.png", base_exits=[0,2])
    
    def on_draft(self, game_logic):
        """
        Déverrouille toutes les portes des Hallways existants
        et garantit que les futurs Hallways seront déverrouillés.
        """
        game_logic.random_manager.hallways_are_unlocked = True
        
        current_map = game_logic.map.get_current_mapping()
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            
            # Si c'est un Hallway déjà posé
            if room_obj is not None and room_obj.room_type == 'Hallway':
                # On déverrouille toutes ses portes
                room_obj.unlock_all_exits()

        game_logic.warning_message = "All Hallway doors are now unlocked!"

class Furnace(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Furnace", "Images/Red Rooms/Furnace.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Augmente la chance de tirer des Red Rooms.
        """
        # On multiplie par 5 la probabilité des Red Rooms
        game_logic.random_manager.type_weight_multipliers['Red Room'] *= 5.0
        game_logic.warning_message = "Heat spreads! More chance to draft Red Rooms."

class Greenhouse(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Greenhouse", "Images/Green Rooms/Greenhouse.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Augmente la chance de tirer des Green Rooms.
        """
        # On multiplie par 3 la probabilité des Green Rooms
        game_logic.random_manager.type_weight_multipliers['Green Room'] *= 3.0
        game_logic.warning_message = "The air feels fresher. \n More chance to draft Green Rooms."

class Guest_Bedroom(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Guest_Bedroom", "Images/Bedrooms/Guest_Bedroom.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Donne +10 Pas au moment du tirage (draft).
        """
        game_logic.player.inventory.add_item(
            ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 10)
        )
        game_logic.warning_message = "Guest Bedroom drafted! +10 Footsteps."

class Hallway(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Hallway", "Images/Hallways/Hallway.png", base_exits=[1,2,3])

class Her_Ladyships_Chamber(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Her_Ladyships_Chamber", "Images/Bedrooms/Her_Ladyships_Chamber.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        super().on_draft(game_logic) # pour le bonus Nursery éventuel
        
        # active les bonus pour la prochaine visite
        game_logic.random_manager.next_boudoir_bonus = True
        game_logic.random_manager.next_closet_bonus = True
        game_logic.warning_message = "Her Ladyship is pleased. \nBonuses await in the Boudoir and Closet."

class Kitchen(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Shop'
    def __init__(self):
        super().__init__("Kitchen", "Images/Shops/Kitchen.png", base_exits=[1,2])

class Locker_Room(RoomObject):
    rarity = 'rare'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Locker_Room", "Images/Rooms/Locker_Room.png", base_exits=[0,2])

    def on_draft(self, game_logic):
        """
        Disperse des Clés (Keys) aléatoirement dans le manoir sous forme d'interactions.
        Si Conference Room est présente, tout va là-bas.
        """
        keys_amount = random.randint(2, 4)
        
        active_rooms = []
        conference_room = None
        current_map = game_logic.map.get_current_mapping()
        
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            if room_obj is not None:
                active_rooms.append(room_obj)
                if room_obj.name == "Conference_Room":
                    conference_room = room_obj
        
        active_rooms.append(self)   # Locker Room peut recevoir des clés

        if conference_room:
            # tout dans la Conference Room
            for _ in range(keys_amount):
                # on ajoute une copie de l'interaction "Key" à l'inventaire de la salle
                conference_room.inventories.addInventory(copy.deepcopy(room_Key))
            game_logic.warning_message = f"Locker Room: {keys_amount} Keys sent to Conference Room!"
        else:
            # dispersion aléatoire
            targets = random.choices(active_rooms, k=keys_amount)
            for target_room in targets:
                target_room.inventories.addInventory(copy.deepcopy(room_Key))
            game_logic.warning_message = f"Locker Room: {keys_amount} Keys spread throughout the house!"

class Maids_Chamber(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Red Room' #et Bedroom elle est les deux types
    def __init__(self):
        super().__init__("Maids_Chamber", "Images/Red Rooms/Maids_Chamber.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        """
        Réduit la probabilité de trouver des objets dans TOUTES les salles.
        """
        # On modifie la chance de base globale dans le random_manager : réduit de 25%
        current_chance = game_logic.random_manager.item_spawn_chance
        game_logic.random_manager.item_spawn_chance = current_chance * 0.75 
        game_logic.warning_message = "The maid tidies up. Item spawn chance reduced."

class Master_Bedroom(RoomObject):
    rarity = 'rare'
    cost = 2
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Master_Bedroom", "Images/Bedrooms/Master_Bedroom.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Donne +1 Pas (Footsteps) pour chaque pièce déjà placée sur la carte.
        """
        # np.count_nonzero() compte tous les éléments non-None dans la grille
        room_count = np.count_nonzero(game_logic.map.get_current_mapping())
        
        if room_count > 0:
            game_logic.player.inventory.add_item(
                ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", room_count)
            )
            game_logic.warning_message = f"Master Bedroom bonus: +{room_count} Footsteps!"

class Nursery(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Nursery", "Images/Bedrooms/Nursery.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Active le bonus de +5 pas pour toutes les futures chambres draftées.
        """
        # on appelle d'abord super().on_draft() pour avoir son propre effet si une autre Nursery a déjà été posée
        super().on_draft(game_logic)
        
        game_logic.random_manager.nursery_bonus_active = True
        game_logic.warning_message = "Nursery built! \nFuture Bedrooms will grant +5 Footsteps."

class Office(RoomObject):
    rarity = 'common'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Office", "Images/Rooms/Office.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        """
        Disperse de l'Or (Coins) aléatoirement.
        """
        coins_amount = random.randint(3, 5)
        
        active_rooms = []
        conference_room = None
        current_map = game_logic.map.get_current_mapping()
        
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            if room_obj is not None:
                active_rooms.append(room_obj)
                if room_obj.name == "Conference_Room":
                    conference_room = room_obj
        
        active_rooms.append(self)

        if conference_room:
            for _ in range(coins_amount):
                conference_room.inventories.addInventory(copy.deepcopy(room_Coin))
            game_logic.warning_message = f"Office: {coins_amount} Coins collected in Conference Room!"
        else:
            targets = random.choices(active_rooms, k=coins_amount)
            for target_room in targets:
                target_room.inventories.addInventory(copy.deepcopy(room_Coin))
            game_logic.warning_message = f"Office: {coins_amount} Coins spread through the house!"

class Parlor(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", base_exits=[1,2])

class Passageway(RoomObject):
    rarity = 'common'
    cost = 2
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Passageway", "Images/Hallways/Passageway.png", base_exits=[0,1,2,3])

class Patio(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Patio", "Images/Green Rooms/Patio.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        """
        Donne 1 Gemme UNIQUEMENT aux 'Green Rooms' (déjà placées + le Patio).
        Si Conference Room est là, toutes les gemmes vont là-bas.
        """
        green_rooms = []
        conference_room = None
        current_map = game_logic.map.get_current_mapping()
        
        # on cherche la Conference Room et les Green Rooms existantes
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            if room_obj is not None:
                if room_obj.name == "Conference_Room":
                    conference_room = room_obj
                # vérification du type pour l'effet Patio
                if room_obj.room_type == 'Green Room':
                    green_rooms.append(room_obj)
        
        green_rooms.append(self)    # Patio est aussi dedans
        
        total_gems = len(green_rooms) # 1 gemme par Green Room

        if conference_room:
            # toutes les gemmes (1 par Green Room) vont dans la Conference Room
            for _ in range(total_gems):
                conference_room.inventories.addInventory(copy.deepcopy(room_Diamond))
            game_logic.warning_message = f"Patio: {total_gems} Gems gathered in Conference Room!"
        else:
            # une gemme apparaît dans chaque Green Room
            for target_room in green_rooms:
                target_room.inventories.addInventory(copy.deepcopy(room_Diamond))
            game_logic.warning_message = "Patio: A Gem appears in every Green Room!"

class Pump_Room(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Pump_Room", "Images/Rooms/Pump_Room.png", base_exits=[1,2])

class Rotunda(RoomObject):
    rarity = 'rare'
    cost = 3
    room_type = 'Room'
    def __init__(self):
        super().__init__("Rotunda", "Images/Rooms/Rotunda.png", base_exits=[1,2])

    def rotate_walls(self):
        """
        Tourne la salle de 90 degrés dans le sens horaire.
        Met à jour l'orientation qui est utilisée par has_exits() et par l'affichage.
        """
        self.orientation = (self.orientation + 1) % 4

class Security(RoomObject):
    rarity = 'rare'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Security", "Images/Rooms/Security.png", base_exits=[1,2,3])

class Secret_Garden(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Secret_Garden", "Images/Green Rooms/Secret_Garden.png", base_exits=[1,2,3])
    
    def on_draft(self, game_logic):
        """
        Disperse des Fruits (Apple/Banana).
        """
        fruit_amount = random.randint(3, 5)
        possible_fruits_interactions = [room_Apple, room_Banana]
        
        active_rooms = []
        conference_room = None
        current_map = game_logic.map.get_current_mapping()
        
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            if room_obj is not None:
                active_rooms.append(room_obj)
                if room_obj.name == "Conference_Room":
                    conference_room = room_obj
                    
        active_rooms.append(self)

        if conference_room:
            for _ in range(fruit_amount):
                interaction = random.choice(possible_fruits_interactions)
                conference_room.inventories.addInventory(copy.deepcopy(interaction))
            game_logic.warning_message = f"Secret Garden: {fruit_amount} Fruits delivered to Conference Room!"
        else:
            targets = random.choices(active_rooms, k=fruit_amount)
            for target_room in targets:
                interaction = random.choice(possible_fruits_interactions)
                target_room.inventories.addInventory(copy.deepcopy(interaction))
            game_logic.warning_message = f"Secret Garden: {fruit_amount} Fruits grew around the house!"

class Secret_Passage(RoomObject):
    rarity = 'uncommon'
    cost = 1
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Secret_Passage", "Images/Hallways/Secret_Passage.png", base_exits=[2])

class Servants_Quarters(RoomObject):
    rarity = 'uncommon'
    cost = 1
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Servants_Quarters", "Images/Bedrooms/Servants_Quarters.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        super().on_draft(game_logic) # bonus Nursery
        
        # compte les Bedrooms sur la carte
        bedroom_count = 0
        current_map = game_logic.map.get_current_mapping()
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            if room_obj is not None and room_obj.room_type == 'Bedroom':
                bedroom_count += 1
        
        if bedroom_count > 0:
            game_logic.player.inventory.add_item(
                ConsumableItem("Key", "Images/Icons/key_icon.png", bedroom_count)
                )
            current_msg = game_logic.warning_message if game_logic.warning_message else ""
            game_logic.warning_message = f"{current_msg} Servants' aid: +{bedroom_count} Keys!"

class Terrace(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Terrace", "Images/Green Rooms/Terrace.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        """
        Rend toutes les 'Green Rooms' gratuites pour le reste de la partie.
        """
        # on parcourt la liste principale de TOUTES les classes de pièces
        for room_class in game_logic.random_manager.full_room_deck:
            
            # si la classe de pièce est de type 'Green Room'
            if room_class.room_type == 'Green Room':
                room_class.cost = 0
        
        game_logic.warning_message = "The garden blooms! All Green Rooms are now free."

class Sauna(RoomObject):
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Sauna", "Images/Rooms/Sauna.png", base_exits=[2])

class The_Pool(RoomObject):
    rarity = 'common'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("The_Pool", "Images/Rooms/The_Pool.png", base_exits=[1,2,3])
    
    def on_draft(self, game_logic):
        """
        Ajoute 3 nouvelles pièces (Sauna, Locker_Room, Pump_Room)
        à la pioche si elles n'y sont pas déjà.
        """
        rooms_to_add = [Sauna, Locker_Room, Pump_Room]
        
        full_deck = game_logic.random_manager.full_room_deck
        current_deck = game_logic.random_manager.current_room_deck
        added_rooms_names = []

        for room_class in rooms_to_add:
            # on les ajoute à la pioche principale si elles n'y sont pas
            if room_class not in full_deck:
                full_deck.append(room_class)
                added_rooms_names.append(room_class.__name__)
            
            # aussi à la pioche actuelle
            if room_class not in current_deck:
                current_deck.append(room_class)
        
        if added_rooms_names:
            game_logic.warning_message = f"New rooms added to the deck: {', '.join(added_rooms_names)}!"

class Veranda(RoomObject):
    rarity = 'uncommon'
    cost = 2
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Veranda", "Images/Green Rooms/Veranda.png", base_exits=[0,2])
    
    def on_draft(self, game_logic):
        """
        Augmente la probabilité de trouver des objets dans les Green Rooms.
        """
        # On modifie le multiplicateur spécifique aux "Green Room" : on double les chances
        current_multiplier = game_logic.random_manager.item_spawn_multipliers['Green Room']
        game_logic.random_manager.item_spawn_multipliers['Green Room'] = current_multiplier * 2.0
        game_logic.warning_message = "The garden flourishes! More items in Green Rooms."

class Weight_Room(RoomObject):
    rarity = 'rare'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Weight_Room", "Images/Red Rooms/Weight_Room.png", base_exits=[0,1,2,3])
    
    def on_draft(self, game_logic):
        """
        Fait perdre la moitié des Pas actuels (arrondi à l'inférieur).
        """
        current_steps = game_logic.player.inventory.get_quantity("Footsteps")
        steps_to_lose = current_steps // 2 # Arrondi à l'inférieur
        
        if steps_to_lose > 0:
            steps_item_to_lose = player_Footsteps.return_item_with_amount(steps_to_lose)
            game_logic.player.use(steps_item_to_lose)
            game_logic.warning_message = f"You feel exhausted : -{steps_to_lose} Footsteps!"
        else:
            game_logic.warning_message = "You feel exhausted but have no steps to lose."

class West_Wing_Hall(RoomObject):
    rarity = 'common'
    cost = 0
    room_type = 'Hallway'
    placement_constraints = 'WEST'
    def __init__(self):
        super().__init__("West_Wing_Hall", "Images/Hallways/West_Wing_Hall.png", base_exits=[1,2,3])