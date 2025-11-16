from item import *
import numpy as np
from inventory import RoomObject as RoomTypeObject
from inventory import *
import random
import copy


class RoomObject:
    '''
    Classe de base pour toutes les salles du jeu.
    
    Elle gère l'état fondamental d'une salle, y compris son nom, son image,
    ses sorties de base, son orientation actuelle, le niveau de verrouillage
    de ses portes, son inventaire d'actions et ses effets spéciaux.
    Cette classe est destinée à être héritée, pas instanciée directement
    (à l'exception des salles de départ/arrivée).

    Attributes
    ----------
    rarity : str
        Rareté de la salle ('common', 'uncommon', 'rare'), utilisée par RandomManager.
    cost : int
        Coût en 'Diamond' (Diamants) pour placer cette salle.
    room_type : str
        Catégorie de la salle (ex: 'Room', 'Green Room', 'Bedroom', 'Shop').
    placement_constraints : str
        Contrainte de placement (ex: 'WEST', 'EAST', 'INDOOR', ou None).
    name : str
        Nom de la salle pour l'affichage.
    image : str
        Chemin d'accès au fichier image de la salle.
    base_exits : list
        Liste des directions de sortie (0-3) dans l'orientation de base (0).
    orientation : int
        Orientation actuelle de la salle (0=Nord, 1=Ouest, 2=Sud, 3=Est).
    exit_locks : dict
        Dictionnaire mappant la direction *de base* (int) à un niveau de verrouillage (int).
    inventories : RoomInventory
        Instance de RoomInventory gérant les actions possibles dans cette salle.
    '''
    
    # Attribut de classe pour la rareté : common par défaut
    # Je les met ici pour qu'ils soient difficile changeable par erreur
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    placement_constraints = None

    def __init__(self, name, image, base_exits=None):
        '''
        Initialise une nouvelle instance de salle.

        Parameters
        ----------
        name : str
            Nom de la salle (ex: "Aquarium").
        image : str
            Chemin vers le fichier image (ex: "Images/Rooms/Aquarium.png").
        base_exits : list, optional
            Liste des sorties de base (0-3). Par défaut, None (devient []).
        '''
        
        self.name = name
        self.image = image
        self.base_exits = base_exits
        # NORD: 0; OUEST: 1; SUD: 2; EST: 3
        self.orientation = 0
        self.exit_locks = {}
        self.inventories = RoomInventory()

    def has_exits(self, direction):
        '''
        Vérifie si la salle a une sortie dans une direction donnée.
        
        Prend en compte l'orientation actuelle de la salle pour
        mapper la direction visible à la direction de base.

        Parameters
        ----------
        direction : int
            Direction "visible" à vérifier (0-3), après rotation.

        Returns
        -------
        bool
            True si une sortie de base correspondante existe, False sinon.
        '''

        # dictionnaires de rotation triog et horraire
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        
        original_drection_to_check = direction
        # exemple: si orientation = 1 alors en tournant 1 fois a droite on retrouve la direction originale
        # si c'est 3 alors on tourne 3 fois a droite pour retrouver la direction originale
        for _ in range(self.orientation):
            original_drection_to_check = MAP_TURN_RIGHT[original_drection_to_check]
            
        return original_drection_to_check in self.base_exits

    def change_room_orientation(self, rotation):
        '''
        Définit l'orientation de la salle.

        Parameters
        ----------
        rotation : int
            La nouvelle orientation (0-3).
        '''
        
        # définition de l'orientation de la salle
        self.orientation = rotation % 4

    def set_exit_lock(self, base_direction, lock_level):
        '''
        Définit le niveau de verrouillage pour une sortie de base.
        
        Appelé par le RandomManager lors de la création de la salle
        (avant rotation).

        Parameters
        ----------
        base_direction : int
            Direction de base (0-3) à laquelle appliquer le verrou.
        lock_level : int
            Niveau de verrouillage (0, 1, ou 2).
        '''
        
        if base_direction in self.base_exits:
            self.exit_locks[base_direction] = lock_level

    def get_original_direction(self, rotated_direction):
        '''
        Fonction utilisée pour retrouver la direction originale d'une sortie après 
        rotation de la salle.
        
        Exemple: si la salle est tournée de 1 (90° horaire), une sortie "NORD" (0) 
        devient "EST" (3). Pour retrouver la direction originale, on doit tourner 
        1 fois à gauche (270°).
        
        Convertit une direction "visible" (après rotation) en sa direction de base.

        Parameters
        ----------
        rotated_direction : int
            Direction (0-3) dont on cherche l'origine.

        Returns
        -------
        int
            Direction de base (0-3) correspondante.
        '''
        
        MAP_TURN_RIGHT = { 0: 3, 1: 0, 2: 1, 3: 2 }
        original_direction = rotated_direction

        for _ in range(self.orientation):
            original_direction = MAP_TURN_RIGHT[original_direction]
        return original_direction
    
    def get_lock_level(self, direction):
        '''
        Récupère le niveau de verrouillage pour une direction "visible" (après rotation).
        
        Parameters
        ----------
        direction : int
            Direction (0-3) à vérifier.
        
        Returns
        -------
        int
            Niveau de verrouillage (0 par défaut si non défini).
        '''
        
        original_direction = self.get_original_direction(direction)
            
        # Renvoie le niveau de blocage (0 par défaut si non défini)
        return self.exit_locks.get(original_direction, 0)
    
    def unlock_exit(self, direction):
        '''
        Déverrouille à jamais (met à 0) une porte pour une direction "visible".

        Parameters
        ----------
        direction : int
            Direction (0-3) à déverrouiller.

        Returns
        -------
        bool
            True si une porte existait et a été déverrouillée, False sinon.
        '''
        original_direction = self.get_original_direction(direction)
        
        if original_direction in self.exit_locks:
            self.exit_locks[original_direction] = 0
            return True
        return False
    
    def unlock_all_exits(self):
        '''
        Force le déverrouillage (niveau 0) de toutes les sorties de base de cette salle.
        Utile pour l'effet du Foyer.
        '''
        
        for base_direction in self.base_exits:
            self.exit_locks[base_direction] = 0

    def on_entry(self, game_logic):
        '''
        Effet spécial déclenché lorsque le joueur entre dans la pièce.
        
        Destiné à être surchargé (override) par les sous-classes.
        Par défaut, ne fait rien.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        pass
    
    def on_draft(self, game_logic):
        '''
        Effet spécial déclenché lorsque le joueur choisit (draft) la pièce.
        
        Destiné à être surchargé (override) par les sous-classes.
        Gère l'effet de base du bonus "Nursery".
        Par défaut, ne fait rien.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
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
        '''
        Récupère les inventaires de la salle.
        (Note: Tente d'appeler `get_inventories` sur `RoomInventory`, 
        ce qui n'existe pas. Probablement une erreur pour `return self.inventories`).
        
        Returns
        -------
        mixed
            Le résultat de `self.inventories.get_inventories()`.
        '''
        return self.inventories.get_inventories()

class EntryHall(RoomObject):
    '''Salle de départ du jeu.'''
    rarity = 'common' 
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Entrance Hall", "Images/Rooms/Entrance_Hall.png", base_exits=[0,1,3])

class AnteChamber(RoomObject):
    '''Salle d'arrivée (objectif) du jeu.'''
    rarity = 'common' 
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("AnteChamber", "Images/Rooms/Antechamber.png", base_exits=[1,2,3]) 

class Aquarium(RoomObject):
    '''Salle 'Aquarium'.'''
    rarity = 'uncommon'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Aquarium", "Images/Rooms/Aquarium.png", base_exits=[1,2,3])

class Attic(RoomObject):
    '''Salle 'Attic' (Grenier).'''
    rarity = 'common' 
    cost = 3
    room_type = 'Room'
    def __init__(self):
        super().__init__("Attic", "Images/Rooms/Attic.png", base_exits=[2]) 

class Ballroom(RoomObject):
    '''Salle 'Ballroom' (Salle de bal).'''
    rarity = 'uncommon'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Ballroom", "Images/Rooms/Ballroom.png", base_exits=[0,2])
    
    def on_entry(self, game_logic):
        '''
        Définit le nombre de 'Diamond' (gemmes) du joueur à 2,
        qu'il en ait plus ou moins.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        super().on_entry(game_logic)
        
        target_gems = 2
        current_gems = game_logic.player.inventory.get_quantity("Diamond")
        difference = target_gems - current_gems
        
        if difference > 0:
            # a moins de 2 gemmes on lui en donne
            item_to_add = player_Diamond.return_item_with_amount(difference)
            game_logic.player.inventory.add_item(item_to_add) #
            game_logic.warning_message = f"Your grace at the ball is rewarded. Gems set to {target_gems}!"
        elif difference < 0:
            # a plus de 2 gemmes on lui en retire
            item_to_lose = player_Diamond.return_item_with_amount(abs(difference))
            game_logic.player.use(item_to_lose) #
            game_logic.warning_message = f"You paid for the dance. Gems set to {target_gems}!"
        else:
            # a 2 gemmes
            game_logic.warning_message = f"You dance gracefully. Your {target_gems} Gems remain."

class Bedroom(RoomObject):
    '''Salle 'Bedroom' (Chambre).'''
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Bedroom", "Images/Bedrooms/Bedroom.png", base_exits=[1,2])
        
    def on_entry(self, game_logic):
        '''
        Donne +2 'Footsteps' (Pas) au joueur lorsqu'il entre.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        game_logic.player.inventory.add_item(
            ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 2)
        )
        game_logic.warning_message = "You feel rested : +2 Footsteps!"

class Billiard_Room(RoomObject):
    '''Salle 'Billiard_Room' (Salle de billard).'''
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Billiard_Room", "Images/Rooms/Billiard_Room.png", base_exits=[1,2]) 

class Boiler_Room(RoomObject):
    '''Salle 'Boiler_Room' (Chaufferie).'''
    rarity = 'uncommon'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Boiler_Room", "Images/Rooms/Boiler_Room.png", base_exits=[1,2,3])

class Boudoir(RoomObject):
    '''Salle 'Boudoir'.'''
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Boudoir", "Images/Bedrooms/Boudoir.png", base_exits=[1,2])
    
    def on_entry(self, game_logic):
        '''
        Si le bonus de 'Her Ladyship's Chamber' est actif, donne +10 Pas.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        # vérifie si le bonus est actif
        if game_logic.random_manager.next_boudoir_bonus:
            game_logic.player.inventory.add_item(
                ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 10)
            )
            game_logic.warning_message = "Her Ladyship's favor: \n+10 Footsteps in the Boudoir!"
            # désactive le bonus après utilisation
            game_logic.random_manager.next_boudoir_bonus = False

class Chamber_of_Mirrors(RoomObject):
    '''Salle 'Chamber_of_Mirrors' (Chambre des miroirs).'''
    rarity = 'rare'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Chamber_of_Mirrors", "Images/Rooms/Chamber_of_Mirrors.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Active `allow_duplicates` dans le RandomManager, permettant 
        aux salles de réapparaître dans la pioche.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        game_logic.random_manager.allow_duplicates = True
        game_logic.warning_message = "The mirrors reflect reality. Duplicates are now possible!"

class Cloister(RoomObject):
    '''Salle 'Cloister' (Cloître).'''
    rarity = 'uncommon'
    cost = 3
    room_type = 'Green Room'
    placement_constraints = 'INDOOR'
    def __init__(self):
        super().__init__("Cloister", "Images/Green Rooms/Cloister.png", base_exits=[0,1,2,3])

class Closet(RoomObject):
    '''Salle 'Closet' (Placard).'''
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Closet", "Images/Rooms/Closet.png", base_exits=[2])
    
    def on_entry(self, game_logic):
        '''
        Si le bonus de 'Her Ladyship's Chamber' est actif, donne +3 Gemmes.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        # vérifie si le bonus est actif
        if game_logic.random_manager.next_closet_bonus:
            game_logic.player.inventory.add_item(
                ConsumableItem("Diamond", "Images/Icons/diamond_icon.png", 3)
            )
            game_logic.warning_message = "Found Her Ladyship's stash: +3 Gems in the Closet!"
            # désactive le bonus après utilisation
            game_logic.random_manager.next_closet_bonus = False

class Coat_Check(RoomObject):
    '''Salle 'Coat_Check' (Vestiaire).'''
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Coat_Check", "Images/Rooms/Coat_Check.png", base_exits=[2])

class Conference_Room(RoomObject):
    '''Salle 'Conference_Room' (Salle de conférence).'''
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Conference_Room", "Images/Rooms/Conference_Room.png", base_exits=[1,2,3])

class Chapel(RoomObject):
    '''Salle 'Chapel' (Chapelle).'''
    rarity = 'common'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Chapel", "Images/Red Rooms/Chapel.png", base_exits=[1,2,3])
    
    def on_entry(self, game_logic):
        '''
        Retire 1 'Coin' (Pièce) au joueur s'il en possède.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        if game_logic.player.inventory.get_quantity("Coin") >= 1:
            game_logic.player.use(player_Coin.return_item_with_amount(1))
            game_logic.warning_message = "You pay tribute : -1 Coin."
        else:
            # L'effet s'active mais le joueur ne peut pas payer
            game_logic.warning_message = "Chapel demands tribute but you're poor."

class Corridor(RoomObject):
    '''Salle 'Corridor'.'''
    rarity = 'common'
    cost = 0
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Corridor", "Images/Hallways/Corridor.png", base_exits=[0,2])

class Dining_Room(RoomObject):
    '''Salle 'Dining_Room' (Salle à manger).'''
    rarity = 'common'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Dining_Room", "Images/Rooms/Dining_Room.png", base_exits=[1,2,3])

class East_Wing_Hall(RoomObject):
    '''Salle 'East_Wing_Hall' (Hall de l'aile Est).'''
    rarity = 'uncommon'
    cost = 0
    room_type = 'Hallway'
    placement_constraints = 'EAST'
    def __init__(self):
        super().__init__("East_Wing_Hall", "Images/Hallways/East_Wing_Hall.png", base_exits=[1,2,3])

class Foyer(RoomObject):
    '''Salle 'Foyer'.'''
    rarity = 'uncommon'
    cost = 2
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Foyer", "Images/Hallways/Foyer.png", base_exits=[0,2])
    
    def on_draft(self, game_logic):
        '''
        Déverrouille toutes les portes de tous les 'Hallway' (Couloirs)
        déjà placés et futurs.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
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
    '''Salle 'Furnace' (Fournaise).'''
    rarity = 'rare'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Furnace", "Images/Red Rooms/Furnace.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Augmente (x5) la probabilité de tirer des 'Red Room' (Salles rouges).

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        # On multiplie par 5 la probabilité des Red Rooms
        game_logic.random_manager.type_weight_multipliers['Red Room'] *= 5.0
        game_logic.warning_message = "Heat spreads! More chance to draft Red Rooms."

class Greenhouse(RoomObject):
    '''Salle 'Greenhouse' (Serre).'''
    rarity = 'common'
    cost = 1
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Greenhouse", "Images/Green Rooms/Greenhouse.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Augmente (x3) la probabilité de tirer des 'Green Room' (Salles vertes).
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        # On multiplie par 3 la probabilité des Green Rooms
        game_logic.random_manager.type_weight_multipliers['Green Room'] *= 3.0
        game_logic.warning_message = "The air feels fresher. \n More chance to draft Green Rooms."

class Guest_Bedroom(RoomObject):
    '''Salle 'Guest_Bedroom' (Chambre d'amis).'''
    rarity = 'common'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Guest_Bedroom", "Images/Bedrooms/Guest_Bedroom.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Donne +10 'Footsteps' (Pas) immédiatement lors du tirage.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        game_logic.player.inventory.add_item(
            ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 10)
        )
        game_logic.warning_message = "Guest Bedroom drafted! +10 Footsteps."

class Hallway(RoomObject):
    '''Salle 'Hallway' (Couloir).'''
    rarity = 'common'
    cost = 0
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Hallway", "Images/Hallways/Hallway.png", base_exits=[1,2,3])

class Her_Ladyships_Chamber(RoomObject):
    '''Salle 'Her_Ladyships_Chamber' (Chambre de Madame).'''
    rarity = 'rare'
    cost = 0
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Her_Ladyships_Chamber", "Images/Bedrooms/Her_Ladyships_Chamber.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Active les bonus pour les futures visites du 'Boudoir' et du 'Closet'.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        super().on_draft(game_logic) # pour le bonus Nursery éventuel
        
        # active les bonus pour la prochaine visite
        game_logic.random_manager.next_boudoir_bonus = True
        game_logic.random_manager.next_closet_bonus = True
        game_logic.warning_message = "Her Ladyship is pleased. Bonuses await in the Boudoir and Closet."

class Locker_Room(RoomObject):
    '''Salle 'Locker_Room' (Vestiaires).'''
    rarity = 'rare'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Locker_Room", "Images/Rooms/Locker_Room.png", base_exits=[0,2])

    def on_draft(self, game_logic):
        '''
        Disperse 2-4 'Key' (Clés) dans des salles aléatoires du manoir sous fore d'interactions.
        Si 'Conference_Room' est présente, toutes les clés y sont placées.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
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
    '''Salle 'Maids_Chamber' (Chambre de la domestique).'''
    rarity = 'uncommon'
    cost = 0
    room_type = 'Red Room' #et Bedroom elle est les deux types
    def __init__(self):
        super().__init__("Maids_Chamber", "Images/Red Rooms/Maids_Chamber.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        '''
        Réduit la chance de base de trouver des objets dans les salles (-25%).

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        # On modifie la chance de base globale dans le random_manager : réduit de 25%
        current_chance = game_logic.random_manager.item_spawn_chance
        game_logic.random_manager.item_spawn_chance = current_chance * 0.75 
        game_logic.warning_message = "The maid tidies up. Item spawn chance reduced."

class Master_Bedroom(RoomObject):
    '''Salle 'Master_Bedroom' (Chambre principale).'''
    rarity = 'rare'
    cost = 2
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Master_Bedroom", "Images/Bedrooms/Master_Bedroom.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Donne +1 'Footstep' (Pas) pour chaque salle déjà placée sur la carte.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        # np.count_nonzero() compte tous les éléments non-None dans la grille
        room_count = np.count_nonzero(game_logic.map.get_current_mapping())
        
        if room_count > 0:
            game_logic.player.inventory.add_item(
                ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", room_count)
            )
            game_logic.warning_message = f"Master Bedroom bonus: +{room_count} Footsteps!"

class Nursery(RoomObject):
    '''Salle 'Nursery' (Crêche).'''
    rarity = 'common'
    cost = 1
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Nursery", "Images/Bedrooms/Nursery.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Active un bonus de +5 Pas pour toutes les futures 'Bedroom' (Chambres)
        qui seront choisies.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        # on appelle d'abord super().on_draft() pour avoir son propre effet si une autre Nursery a déjà été posée
        super().on_draft(game_logic)
        
        game_logic.random_manager.nursery_bonus_active = True
        game_logic.warning_message = "Nursery built! \nFuture Bedrooms will grant +5 Footsteps."

class Office(RoomObject):
    '''Salle 'Office' (Bureau).'''
    rarity = 'common'
    cost = 2
    room_type = 'Room'
    def __init__(self):
        super().__init__("Office", "Images/Rooms/Office.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        '''
        Disperse 3-5 'Coin' (Pièces) dans des salles aléatoires du manoir.
        Si 'Conference_Room' est présente, toutes les pièces y sont placées.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
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
    '''Salle 'Parlor' (Parloir).'''
    rarity = 'common'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Parlor", "Images/Rooms/Parlor.png", base_exits=[1,2])

class Passageway(RoomObject):
    '''Salle 'Passageway' (Passage).'''
    rarity = 'common'
    cost = 2
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Passageway", "Images/Hallways/Passageway.png", base_exits=[0,1,2,3])

class Patio(RoomObject):
    '''Salle 'Patio'.'''
    rarity = 'common'
    cost = 1
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Patio", "Images/Green Rooms/Patio.png", base_exits=[1,2])
    
    def on_draft(self, game_logic):
        '''
        Place 1 'Diamond' (Gemme) dans chaque 'Green Room' déjà placée 
        (y compris celle-ci). Si 'Conference_Room' est présente, 
        toutes les gemmes y sont placées.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
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
    '''Salle 'Pump_Room' (Salle des pompes).'''
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Pump_Room", "Images/Rooms/Pump_Room.png", base_exits=[1,2])

class Rotunda(RoomObject):
    '''Salle 'Rotunda' (Rotonde).'''
    rarity = 'rare'
    cost = 3
    room_type = 'Room'
    def __init__(self):
        super().__init__("Rotunda", "Images/Rooms/Rotunda.png", base_exits=[1,2])
    
    def on_entry(self, game_logic):
        '''
        Avertit le joueur qu'il peut appuyer sur 'T' pour pivoter la salle.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        super().on_entry(game_logic)
        game_logic.warning_message = "This room feels strange... \nPress 'T' to rotate it."

    def rotate_walls(self):
        '''
        Fait pivoter la salle de 90 degrés dans le sens horaire en modifiant `self.orientation`.
        Met à jour l'orientation qui est utilisée par has_exits() et par l'affichage.
        '''
        
        self.orientation = (self.orientation + 1) % 4

class Security(RoomObject):
    '''Salle 'Security' (Sécurité).'''
    rarity = 'rare'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Security", "Images/Rooms/Security.png", base_exits=[1,2,3])

class Secret_Garden(RoomObject):
    '''Salle 'Secret_Garden' (Jardin secret).'''
    rarity = 'rare'
    cost = 0
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Secret_Garden", "Images/Green Rooms/Secret_Garden.png", base_exits=[1,2,3])
    
    def on_draft(self, game_logic):
        '''
        Disperse 3-5 fruits (Pommes/Bananes) dans des salles aléatoires.
        Si 'Conference_Room' est présente, tous les fruits y sont placés.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
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
    '''Salle 'Secret_Passage' (Passage secret).'''
    rarity = 'uncommon'
    cost = 1
    room_type = 'Hallway'
    def __init__(self):
        super().__init__("Secret_Passage", "Images/Hallways/Secret_Passage.png", base_exits=[2])

class Servants_Quarters(RoomObject):
    '''Salle 'Servants_Quarters' (Quartiers des domestiques).'''
    rarity = 'uncommon'
    cost = 1
    room_type = 'Bedroom'
    def __init__(self):
        super().__init__("Servants_Quarters", "Images/Bedrooms/Servants_Quarters.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Donne +1 'Key' (Clé) pour chaque 'Bedroom' (Chambre) déjà placée.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
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
    '''Salle 'Terrace'.'''
    rarity = 'common'
    cost = 0
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Terrace", "Images/Green Rooms/Terrace.png", base_exits=[2])
    
    def on_draft(self, game_logic):
        '''
        Met le coût de toutes les 'Green Room' (Salles vertes) à 0 
        pour le reste de la partie.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        # on parcourt la liste principale de TOUTES les classes de pièces
        for room_class in game_logic.random_manager.full_room_deck:
            
            # si la classe de pièce est de type 'Green Room'
            if room_class.room_type == 'Green Room':
                room_class.cost = 0
        
        game_logic.warning_message = "The garden blooms! All Green Rooms are now free."

class Sauna(RoomObject):
    '''Salle 'Sauna'.'''
    rarity = 'uncommon'
    cost = 0
    room_type = 'Room'
    def __init__(self):
        super().__init__("Sauna", "Images/Rooms/Sauna.png", base_exits=[2])

class The_Pool(RoomObject):
    '''Salle 'The_Pool' (La piscine).'''
    rarity = 'common'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("The_Pool", "Images/Rooms/The_Pool.png", base_exits=[1,2,3])
    
    def on_draft(self, game_logic):
        '''
        Ajoute 3 nouvelles salles (Sauna, Locker_Room, Pump_Room) 
        aux pioches (complète et actuelle).
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
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
    '''Salle 'Veranda'.'''
    rarity = 'uncommon'
    cost = 2
    room_type = 'Green Room'
    def __init__(self):
        super().__init__("Veranda", "Images/Green Rooms/Veranda.png", base_exits=[0,2])
    
    def on_draft(self, game_logic):
        '''
        Double la probabilité de trouver des objets dans les 'Green Room'.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        # On modifie le multiplicateur spécifique aux "Green Room" : on double les chances
        current_multiplier = game_logic.random_manager.item_spawn_multipliers['Green Room']
        game_logic.random_manager.item_spawn_multipliers['Green Room'] = current_multiplier * 2.0
        game_logic.warning_message = "The garden flourishes! More items in Green Rooms."

class Walkin_Closet(RoomObject):
    '''Salle 'Walkin_Closet' (Dressing).'''
    rarity = 'common'
    cost = 1
    room_type = 'Room'
    def __init__(self):
        super().__init__("Walkin_Closet", "Images/Rooms/Walk-in_Closet.png", base_exits=[2])

class Weight_Room(RoomObject):
    '''Salle 'Weight_Room' (Salle de musculation).'''
    rarity = 'rare'
    cost = 0
    room_type = 'Red Room'
    def __init__(self):
        super().__init__("Weight_Room", "Images/Red Rooms/Weight_Room.png", base_exits=[0,1,2,3])
    
    def on_draft(self, game_logic):
        '''
        Fait perdre au joueur la moitié de ses 'Footsteps' (Pas) actuels.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        current_steps = game_logic.player.inventory.get_quantity("Footsteps")
        steps_to_lose = current_steps // 2 # Arrondi à l'inférieur
        
        if steps_to_lose > 0:
            steps_item_to_lose = player_Footsteps.return_item_with_amount(steps_to_lose)
            game_logic.player.use(steps_item_to_lose)
            game_logic.warning_message = f"You feel exhausted : -{steps_to_lose} Footsteps!"
        else:
            game_logic.warning_message = "You feel exhausted but have no steps to lose."

class West_Wing_Hall(RoomObject):
    '''Salle 'West_Wing_Hall' (Hall de l'aile Ouest).'''
    rarity = 'common'
    cost = 0
    room_type = 'Hallway'
    placement_constraints = 'WEST'
    def __init__(self):
        super().__init__("West_Wing_Hall", "Images/Hallways/West_Wing_Hall.png", base_exits=[1,2,3])

#SHOPS
class Kitchen(RoomObject):
    '''Salle 'Kitchen' (Cuisine). C'est une boutique de nourriture.'''
    rarity = 'common'
    cost = 0
    room_type = 'Shop'
    def __init__(self):
        super().__init__("Kitchen", "Images/Shops/Kitchen.png", base_exits=[1,2])

    def return_number_room_type(self, game_logic, room_type):
        '''
        Compte le nombre de salles d'un type donné sur la carte.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        room_type : str
            Le 'room_type' à rechercher.
        
        Returns
        -------
        int
            Le nombre de salles de ce type (y compris celle-ci si elle correspond).
        '''
        rooms = []
        current_map = game_logic.map.get_current_mapping()
        
        for room in np.nditer(current_map, flags=['refs_ok']):
            room_obj = room.item()
            if room_obj is not None:
                if room_obj.room_type == room_type:
                    rooms.append(room_obj)
        
        rooms.append(self)    # Patio est aussi dedans
        
        return len(rooms) # 1 gemme par Green Room

    def on_draft(self, game_logic):
        '''
        Crée et assigne l'inventaire de la boutique (nourriture).
        Le coût de la salade et de la soupe est dynamique.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        room_Menu = RoomInventory()

        kitchen_Banana = RoomTypeObject("Banana", player_Banana.return_item_with_amount(1),player_Coin.return_item_with_amount(2), "Buy _0 x _1", "You ate the _0(s) and gained _3 _2(s)!","Couldn't take item",confirmation=True)
        kitchen_ClubSandwich = RoomTypeObject("Club Sandwich",player_ClubSandwich.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item",confirmation=True)
        kitchen_ChefSalad = RoomTypeObject("Chef Salad",player_ChefSalad.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item",confirmation=True)
        kitchen_TomatoSoup = RoomTypeObject("Tomato Soup",player_TomatoSoup.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item",confirmation=True)

        room_Menu.addInventory(kitchen_Banana)
        room_Menu.addInventory(kitchen_ClubSandwich)


        room_number = self.return_number_room_type(game_logic, 'Green Room')
        kitchen_ChefSalad.item.quantity = room_number 
        room_Menu.addInventory(kitchen_ChefSalad)

        room_number = self.return_number_room_type(game_logic, 'Red Room')
        kitchen_TomatoSoup.item.quantity = room_number 
        room_Menu.addInventory(kitchen_TomatoSoup)

        self.inventories.inventory = room_Menu.inventory
        game_logic.warning_message = "Come and eat for a reasonable price!"
    
    def on_entry(self, game_logic):
        '''
        Met à jour la quantité de 'Footsteps' (Pas) restaurés par la
        salade et la soupe en fonction du nombre actuel de salles 
        'Green Room' et 'Red Room'.
        
        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''
        
        for item in self.inventories.inventory:
            if item.name == "Chef Salad":
                room_number = self.return_number_room_type(game_logic, 'Green Room')
                item.item.quantity = room_number 
                item.set_message()
            elif item.item.name == "Tomato Soup":
                room_number = self.return_number_room_type(game_logic, 'Red Room')
                item.item.quantity = room_number
                item.set_message()

class Commissary(RoomObject):
    '''Salle 'Commissary' (comptoir). C'est une boutique d'objets.'''
    rarity = 'uncommon'
    cost = 0
    room_type = 'Shop'
    def __init__(self):
        super().__init__("Commissary", "Images/Shops/Commissary.png", base_exits=[1,2])

    def on_draft(self, game_logic):
        '''
        Crée et assigne l'inventaire de la boutique.
        Propose 4 objets aléatoires parmi une sélection.

        Parameters
        ----------
        game_logic : Game
            L'instance principale de la classe Game.
        '''

        commissary_Banana = RoomTypeObject("Banana", player_Banana.return_item_with_amount(1),player_Coin.return_item_with_amount(3), "Buy _0 x _1", "You bought _1 _0 and restored _4 _3!","Couldn't buy item",confirmation=True)
        commissary_Shovel = RoomTypeObject("Shovel", player_shovel.return_item_with_amount(1),player_Coin.return_item_with_amount(6), "Buy _0", "You bought the _0","Couldn't buy item",confirmation=True)
        commissary_hammer = RoomTypeObject("Hammer", player_hammer.return_item_with_amount(1),player_Coin.return_item_with_amount(8), "Buy _0", "You bought the _0","Couldn't buy item",confirmation=True)
        commissary_MetalDetector = RoomTypeObject("Metal Detector", player_metal_detector.return_item_with_amount(1),player_Coin.return_item_with_amount(10), "Buy _0", "You bought the _0","Couldn't buy item",confirmation=True)
        commissary_diamond_set = RoomTypeObject("Set of Diamonds", player_Diamond.return_item_with_amount(random.randint(3,4)),player_Coin.return_item_with_amount(10), "Buy _0", "You got _1 diamonds","Couldn't buy item",confirmation=True)
        commissary_Key = RoomTypeObject("Key", player_Key.return_item_with_amount(1),player_Coin.return_item_with_amount(10), "Buy _0 x _1", "You bought _1 _0","Couldn't buy item",confirmation=True)

        room_item_pool = [commissary_Banana,commissary_Shovel,commissary_hammer,commissary_MetalDetector,commissary_diamond_set,commissary_Key]


        room_Menu = RoomInventory()

        for i in range(0,4):
            index = random.randint(0,len(room_item_pool)-1)
            room_Menu.addInventory(room_item_pool[index])
            room_item_pool.pop(index)


        self.inventories.inventory = room_Menu.inventory
        game_logic.warning_message = "Buy items for a price!"