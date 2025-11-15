from item import *
import re

class Inventory:
    """
    Gère les objets possédés par le joueur.
    Sépare les consommables (empilables) des non-consommables (uniques).
    """
    def __init__(self):
        self.inventory = {}
    

    def add_item(self, item_to_add : Item):
        """
        Ajoute un objet à l'inventaire.
        Si c'est un consommable déjà possédé, augmente la quantité.
        Si c'est un non-consommable, l'ajoute s'il n'est pas déjà présent.
        """
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

    def add_Inventory(self, other):
        for item in other.get_all_items():
            self.add_item(item)

    def get_quantity(self, item_name):
        """Retourne la quantité d'un consommable (0 si non possédé)"""
        if item_name in self.inventory:
            return self.inventory[item_name].quantity
        return 0

    def get_all_items(self):
        """Retourne une seule liste de tous les objets pour l'affichage dans l'inventaire"""
        all_items = list(self.inventory.values())
        return all_items
    

class RoomObject():
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
        """
        Dans le message donnée, remplace _0, _1 ect par les élements trouvé à l'index indiqué dans la liste remplacements.
        Ex replacement = ["Apples","2"]
        message = "You took _1 _0"
        Devient "You took 2 Apples"
        """
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
    

        


    """
    @property
    def name(self):
        return self.name
    @property
    def item(self):
        return self.item
    
    @property
    def activation_condition(self):
        return self.activation_condition
    @property
    def action_message(self):
        return self.action_message

    @property
    def action_success(self):
        return self.action_success

    @property
    def action_failure(self):
        return self.action_failure
    """
room_items_dictionary = {}

class Room_Inventory():

    def __init__(self):
        self.inventory = [ ]
    
    def addInventory(self, inventory_Item):
        if isinstance(inventory_Item, RoomObject):
            self.inventory.append(inventory_Item)
    
    def get_action_number(self):
        return len(self.inventory)

    def get_action_messages(self):
        messages = [ ]
        for item in self.inventory:
            messages.append(item.action_message)
        return messages
    
    def checkInv_activation_condition(self, player, room_object : RoomObject, test=False):
        result = player.check_Item(room_object.activation_condition, room_object.item, test=test)
        return result

    def set_inventory(self, inventory):
        self.inventory = inventory

    def return_inventory_copy(self):
        inventory = self
        return inventory

    def handle_action(self, player, action_index, force=False):
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
                    return ("CONFIRM", f"Do you want to open this {item_to_act_upon.name} for {cost_amount} {cost_item_name} ?")
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
HOW TO SET MESSAGES:
Each item type has got referencible elements to create a message.
For example image we want to write : "You picked up Apple x 5!"
We first write the basic message
"You picked up _0 x _1"
_0 and _1 are indentifiers relating to the items parameters. Each item type has got different accessibility parameters
Example:
Consummable Items [name, quantity]
Nonconsummable Items [name]
Regenerative Items [name, quantity, item to regenerate name, item to regenerate quantity]
Inventory Type Item [name]

The index of the element in each list represents the parameter.
"""
#Room Item - Name, Item to collect/interact with, Activation Condition (None if No item needed to interact),"Action Msg", "Action Sucess", "Action Failure"


room_Dice = RoomObject("Dice",player_Dice.return_item_with_amount(1),None,"Take _0 x _1", "You took _1 _0(s)","Couldn't take item")
room_Key = RoomObject("Key",player_Key.return_item_with_amount(1),None,"Take _0 x _1", "You took _1 _0(s)","Couldn't take item")
room_Diamond = RoomObject("Diamond", player_Diamond.return_item_with_amount(1), None, "Take _0 x _1", "You took _1 _0(s)","Couldn't take item")
room_Coin = RoomObject("Coin", player_Coin.return_item_with_amount(1), None, "Take _0 x _1", "You took _1 _0(s)","Couldn't take item")

room_Apple = RoomObject("Apple",player_Apple.return_item_with_amount(1),None,"Take _0 x _1", "You ate the _0(s) and gained _3 _2(s)!","Couldn't take item")
room_Banana = RoomObject("Banana", player_Banana.return_item_with_amount(1),None, "Take _0 x _1", "You ate the _0(s) and gained _3 _2(s)!","Couldn't take item")

room_ClubSandwich = RoomObject("Club Sandwich",player_ClubSandwich.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item")
room_ChefSalad = RoomObject("Chef Salad",player_ChefSalad.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item")
room_TomatoSoup = RoomObject("Tomato Soup",player_ClubSandwich.return_item_with_amount(1),player_Coin.return_item_with_amount(8),"Buy _0", "You ate the _0 and gained _3 _2(s)!","Couldn't take item")
# Je met none pour ensuite gérer le remplissage à partir de random manager
room_Chest = RoomObject("Chest", None, player_Key.return_item_with_amount(1), "Open _0","You opened the _0!", "You do not have a Key:", confirmation=True)
room_Hole = RoomObject("Hole", None, player_shovel, "Dig _0","You dug the _0 out!", "You do not have a shovel:")
room_locker = RoomObject("Locker", None, player_Key.return_item_with_amount(1), "Open _0","You opened the _0!", "You do not have a Key:", confirmation=True)
room_hammer = RoomObject("Hammer", player_hammer, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_charm_chroma = RoomObject("Charm Chroma", player_charm_chroma, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_Shovel = RoomObject("Shovel", player_shovel, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_metal_detector = RoomObject("Metal Detector", player_metal_detector, None, "Take _0", "You picked up the _0", "Couldn't take _0")
room_lock_picking_kit = RoomObject("Lock Picking Kit", player_lock_picking_kit, None, "Take _0", "You picked up the _0", "Couldn't take _0")


items = [room_Apple,room_Banana,room_Dice,room_Key, room_Diamond, room_Chest, room_Hole, room_Shovel, room_Coin, room_charm_chroma, room_metal_detector, room_hammer, room_lock_picking_kit]
for item in items:
    if item.name not in room_items_dictionary:
        room_items_dictionary[item.name] = item


    

