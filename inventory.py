from item import *
import re

class Inventory:
    '''
    Gère les objets possédés par le joueur.
    
    Stocke les objets dans un dictionnaire, faisant la distinction
    entre les consommables (empilables) et les non-consommables (uniques)
    lors de l'ajout.
    
    Attributes
    ----------
    inventory : dict
        Stocke les objets du joueur. Les clés sont les noms (str) 
        des objets et les valeurs sont les instances (Item) de ces objets.
    '''
    
    def __init__(self):
        self.inventory = {}

    def add_item(self, item_to_add : Item):
        '''
        Ajoute un objet à l'inventaire.
        
        Si c'est un consommable déjà possédé, augmente la quantité.
        Si c'est un non-consommable, l'ajoute s'il n'est pas déjà présent.
        
        Parameters
        ----------
        item_to_add : Item
            L'instance de l'objet (ConsumableItem ou NonConsumableItem) 
            à ajouter.
        '''
        
        if isinstance(item_to_add, ConsumableItem):
            if item_to_add.name in self.inventory:
                # Si le joueur a déjà cet objet on ajoute juste la quantité
                self.inventory[item_to_add.name].add(item_to_add.quantity)
            else:
                # Sinon on ajoute le nouvel objet au dictionnaire
                self.inventory[item_to_add.name] = item_to_add
                
        elif isinstance(item_to_add, NonConsumableItem):
            if item_to_add.name not in self.inventory:
                # On ajoute l'objet unique seulement s'il n'est pas déjà là
                self.inventory[item_to_add.name] = item_to_add

    def get_quantity(self, item_name):
        '''
        Retourne la quantité d'un objet possédé.

        Parameters
        ----------
        item_name : str
            Le nom de l'objet à vérifier.

        Returns
        -------
        int
            La quantité de l'objet (0 si non possédé).
        '''
        
        if item_name in self.inventory:
            return self.inventory[item_name].quantity
        return 0

    def get_all_items(self):
        '''
        Retourne une liste de tous les objets pour l'affichage dans l'inventaire.
        
        Returns
        -------
        list
            Une liste de toutes les instances d'objets (Item) 
            présentes dans l'inventaire.
        '''
        
        all_items = list(self.inventory.values())
        return all_items
    

class RoomInventoryObject():
    '''
    Représente une action ou un objet interactif dans une salle.
    
    Contient le nom de l'action, l'objet de récompense (`item`), 
    le coût (`activation_condition`), les messages d'UI, et si 
    l'action nécessite une confirmation.

    Attributes
    ----------
    name : str
        Le nom de l'action (ex: "Chest", "Apple").
    item : Item or Inventory
        L'objet (ou le butin d'un coffre) que le joueur reçoit.
    activation_condition : Item
        L'objet requis (coût) pour activer l'action (ex: une Clé, des Pièces).
    action_message : str
        Le message formaté affiché dans la liste d'actions de l'UI.
    action_success : str
        Le message formaté affiché en cas de succès de l'action.
    action_failure : str
        Le message formaté affiché en cas d'échec de l'action.
    confirmation : bool
        Si True, l'action demandera une confirmation (Oui/Non) à l'UI.
    '''
    
    def __init__(self, name, item, activation_condition, action_message, action_sucess, action_failure, confirmation=False):
        self.name = name
        self.item = item
        self.activation_condition = activation_condition
        self.action_message = action_message
        self.action_success = action_sucess
        self.action_failure = action_failure
        self.confirmation = confirmation
        self.set_message()
    
    def string_to_message(self, message, replacements):
        '''
        Dans le message donnée, remplace les marqueurs (_0, _1) par les 
        élements trouvé à l'index indiqué dans la liste remplacements.
        
        Ex replacement = ["Apples","2"]
        message = "You took _1 _0"
        Devient "You took 2 Apples"
        
        Parameters
        ----------
        message : str
            La chaîne de caractères modèle (ex: "Prendre _0 x _1").
        replacements : list
            La liste des valeurs à insérer (ex: ["Apple", 2]).

        Returns
        -------
        str
            Le message formaté (ex: "Prendre Apple x 2").
        '''
        
        if not replacements:
            return message

        pattern = re.compile(r"_(\d+)")

        def replacer(match):
            idx = int(match.group(1))
            if 0 <= idx < len(replacements):
                return str(replacements[idx])   # ensure we return a string
            return match.group(0)  # leave the placeholder unchanged if out of range

        return pattern.sub(replacer, message)
    
    def set_message(self):
        '''
        Initialise ou met à jour les messages (action, succès, échec) 
        en utilisant `string_to_message` pour insérer les détails 
        de l'objet (`item`).
        '''
        
        replacements = []
        if self.item is None:
            replacements = [self.name]
        if isinstance(self.item,Inventory):
            replacements = [self.name]
        if isinstance(self.item,ConsumableItem):
            replacements= [self.item.name,self.item.quantity]
        if isinstance(self.item,NonConsumableItem):
            replacements = [self.item.name]
        if isinstance(self.item,RegenerativeItem):
            replacements = [self.item.name, self.item.quantity, self.item.regenerate.name, (self.item.regenerate.quantity * self.item.quantity)]

        self.action_message = self.string_to_message(self.action_message,replacements)
        self.action_success = self.string_to_message(self.action_success,replacements)
        self.action_failure = self.string_to_message(self.action_failure,replacements)
    
room_items_dictionary = {}

class RoomInventory():
    '''
    Gère la collection d'actions (`RoomInventoryObject`) disponibles dans une salle.
    
    Attributes
    ----------
    inventory : list
        Une liste d'instances `RoomInventoryObject` représentant les 
        actions/objets dans la salle.
    '''
    
    def __init__(self):
        self.inventory = [ ]
    
    def addInventory(self, inventory_Item):
        '''
        Ajoute une action à l'inventaire de la salle.
        
        Parameters
        ----------
        inventory_Item : RoomInventoryObject
            L'instance de l'action à ajouter.
        '''
        
        if isinstance(inventory_Item, RoomInventoryObject):
            self.inventory.append(inventory_Item)
    
    def get_action_number(self):
        '''
        Retourne le nombre d'actions disponibles dans la salle.
        
        Returns
        -------
        int
            Le nombre d'objets `RoomInventoryObject` dans la liste.
        '''
        
        return len(self.inventory)

    def get_action_messages(self):
        '''
        Construit la liste des messages d'action pour l'UI.
        
        Returns
        -------
        list
            Une liste de chaînes de caractères (les `action_message` 
            formatés de chaque action).
        '''
        
        messages = [ ]
        for item in self.inventory:
            messages.append(item.action_message)
        return messages
    
    def checkInv_activation_condition(self, player, room_object : RoomInventoryObject, test=False):
        '''
        Vérifie si le joueur remplit la condition d'activation (coût) 
        pour une action.
        
        Parameters
        ----------
        player : Player
            L'instance du joueur.
        room_object : RoomInventoryObject
            L'action dont la condition est vérifiée.
        test : bool
            (Non utilisé directement ici, passé à `check_condition`).

        Returns
        -------
        bool
            Résultat de `player.check_condition()`.
        '''
        
        result = player.check_condition(room_object.activation_condition)
        return result

    def use_item(self,player, room_object : RoomInventoryObject, test=False):
        '''
        Exécute la transaction (payer le coût, recevoir l'objet) 
        pour une action.
        
        Parameters
        ----------
        player : Player
            L'instance du joueur.
        room_object : RoomInventoryObject
            L'action à exécuter.
        test : bool
            Si True, outrepasse la vérification du coût (ex: Marteau).

        Returns
        -------
        bool
            Résultat de `player.check_Item()`.
        '''
        
        result = player.check_Item(room_object.activation_condition, room_object.item, test=test)
        return result
    
    def return_inventory_copy(self):
        '''
        Retourne une référence à cette instance d'inventaire.
        (Note: Ne retourne pas une copie).
        
        Returns
        -------
        RoomInventory
            L'instance `self`.
        '''
        
        inventory = self
        return inventory

    def handle_action(self, player, action_index, force=False):
        '''
        Gère la logique principale de l'interaction du joueur 
        avec une action de la salle.
        
        Vérifie si une confirmation est nécessaire, gère l'override 
        du Marteau (Hammer), vérifie le coût, et exécute l'action 
        en retirant l'objet de la salle.
        
        Parameters
        ----------
        player : Player
            L'instance du joueur.
        action_index : int
            L'index de l'action sélectionnée dans la liste `self.inventory`.
        force : bool
            Si True, l'action est exécutée sans redemander de confirmation 
            (utilisé après un "Oui" de l'UI).
        
        Returns
        -------
        str or tuple or None
            - (tuple) `("CONFIRM", str)` si l'action nécessite une confirmation.
            - (str) Un message de succès ou d'échec.
            - `None` si la salle est vide.
        '''
        
        if len(self.inventory) > 0:
            item_to_act_upon = self.inventory[action_index]
            if item_to_act_upon.confirmation and not force:

                test = False
                hammer_check = player.inventory.get_quantity("Hammer") > 0 and item_to_act_upon.name in ["Chest"]
                if hammer_check:
                    test = True
                    
                result = self.checkInv_activation_condition(player, item_to_act_upon, test=test)

                if result == 1:
                    # le joueur a la clé ? on demande confirmation
                    if hammer_check:
                        cost_item_name = item_to_act_upon.activation_condition.name
                        return ("CONFIRM", f"Do you want to break this {item_to_act_upon.name} to get its items ?")

                    cost_item_name = item_to_act_upon.activation_condition.name
                    cost_amount = item_to_act_upon.activation_condition.quantity

                    if cost_item_name == "Coin":
                        verb = "buy"
                    else:
                        verb = "open"
                    return ("CONFIRM", f"Do you want to {verb} this {item_to_act_upon.name} for {cost_amount} {cost_item_name} ?")
                else:
                    # Le joueur ne peut pas de toute façon donc on affiche l'échec
                    return item_to_act_upon.action_failure
                
            # On doit refaire le check pour le marteau ici avant l'exécution
            test = False

            # On vérifie le marteau SEULEMENT si c'est un Coffre
            if (item_to_act_upon.confirmation and 
                player.inventory.get_quantity("Hammer") > 0 and 
                item_to_act_upon.name == "Chest"):
                test = True
                
            result = self.checkInv_activation_condition(player, item_to_act_upon, test=test)

            if result == 1:

                loot_items = []

                if isinstance(item_to_act_upon.item, Inventory):
                    loot_items = item_to_act_upon.item.get_all_items()

                # Si c'est un trou et qu'il est vide
                if item_to_act_upon.name in ["Hole", "Locker"] and not loot_items:
                    self.inventory.pop(action_index)
                    if item_to_act_upon.name == "Hole":
                        return "The hole was empty"
                    else:
                        return "The locker was empty"
                self.use_item(player, item_to_act_upon, test=test)
                msg = item_to_act_upon.action_success

                if isinstance(item_to_act_upon.item,Inventory):
                    for item in item_to_act_upon.item.get_all_items():
                        self.inventory.append(room_items_dictionary[item.name])
                self.inventory.pop(action_index)
                return msg
            else:
                return item_to_act_upon.action_failure
        else:
            return None #String empty pour le message
        


"""
COMMENT DÉFINIR LES MESSAGES :
Chaque type d'objet possède des éléments référençables pour créer un message.
Par exemple, si nous voulons écrire : « Vous avez ramassé Apple x 5 ! »
On écrit d'abord le message de base
« Vous avez ramassé _0 x _1 »
_0 et _1 sont des identifiants liés aux paramètres de l'objet. Chaque type d'objet possède différents paramètres accessibles
Exemple :
Objets Consommables [name, quantity]
Objets Non-consommables [name]
Objets Régénératifs [name, quantity, item to regenerate name, item to regenerate quantity]
Objet de type Inventaire [name]

L'index de l'élément dans chaque liste représente le paramètre.
"""
#Room Item - Name, Item to collect/interact with, Activation Condition (None if No item needed to interact),"Action Msg", "Action Sucess", "Action Failure"
room_Dice = RoomInventoryObject("Dice",player_Dice.return_item_with_amount(1),None,"Take _0 x _1", "You took _1 _0(s)","Couldn't take item")
room_Key = RoomInventoryObject("Key",player_Key.return_item_with_amount(1),None,"Take _0 x _1", "You took _1 _0(s)","Couldn't take item")
room_Diamond = RoomInventoryObject("Diamond", player_Diamond.return_item_with_amount(1), None, "Take _0 x _1", "You took _1 _0(s)","Couldn't take item")
room_Coin = RoomInventoryObject("Coin", player_Coin.return_item_with_amount(1), None, "Take _0 x _1", "You took _1 _0(s)","Couldn't take item")

room_Apple = RoomInventoryObject("Apple",player_Apple.return_item_with_amount(1),None,"Take _0 x _1", "You ate the _0(s) and gained _3 _2(s)!","Couldn't take item")
room_Banana = RoomInventoryObject("Banana", player_Banana.return_item_with_amount(1),None, "Take _0 x _1", "You ate the _0(s) and gained _3 _2(s)!","Couldn't take item")

room_ClubSandwich = RoomInventoryObject("Club Sandwich",player_ClubSandwich.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item")
room_ChefSalad = RoomInventoryObject("Chef Salad",player_ChefSalad.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item")
room_TomatoSoup = RoomInventoryObject("Tomato Soup",player_ClubSandwich.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item")

room_Chest = RoomInventoryObject("Chest", None, player_Key.return_item_with_amount(1), "Open _0","You opened the _0!", "You do not have a Key:", confirmation=True)
room_Hole = RoomInventoryObject("Hole", None, player_shovel, "Dig _0","You dug the _0 out!", "You do not have a shovel:")
room_locker = RoomInventoryObject("Locker", None, player_Key.return_item_with_amount(1), "Open _0","You opened the _0!", "You do not have a Key:", confirmation=True)
room_hammer = RoomInventoryObject("Hammer", player_hammer, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_charm_chroma = RoomInventoryObject("Charm Chroma", player_charm_chroma, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_Shovel = RoomInventoryObject("Shovel", player_shovel, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_metal_detector = RoomInventoryObject("Metal Detector", player_metal_detector, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_lock_picking_kit = RoomInventoryObject("Lock Picking Kit", player_lock_picking_kit, None, "Take _0", "You picked up the _0", "Couldn't take _0")


items = [room_Apple,room_Banana,room_Dice,room_Key, room_Diamond, room_Chest, room_Hole, room_Shovel, room_Coin, room_charm_chroma, room_metal_detector, room_hammer, room_lock_picking_kit]
for item in items:
    if item.name not in room_items_dictionary:
        room_items_dictionary[item.name] = item


    

