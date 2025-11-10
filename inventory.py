from item import *


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
    def __init__(self, name, item, activation_condition, action_message, action_sucess, action_failure):
        self.name = name
        self.item = item
        self.activation_condition = activation_condition
        self.action_message = action_message
        self.action_success = action_sucess
        self.action_failure = action_failure
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
    
    def checkInv_activation_condition(self, player, room_object : RoomObject):
        result = player.check_Item(room_object.activation_condition, room_object.item)
        return result

    def set_inventory(self, inventory):
        self.inventory = inventory

    def return_inventory_copy(self):
        inventory = self
        return inventory

    def handle_action(self, player, action_index):
        if len(self.inventory) > 0:
            item_to_act_upon = self.inventory[action_index]
            result = self.checkInv_activation_condition(player, item_to_act_upon)

            if result == 1:
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
        


#Room Item - Name, Item to collect/interact with, Activation Condition (None if No item needed to interact),"Action Msg", "Action Sucess", "Action Failure"
room_None = RoomObject("Nothing", item_None, None, "", "", "")
room_Apple = RoomObject("Apple",player_Apple.return_item_with_amount(1),None,"Take Apple", "You took the apples!","Couldn't take item")
room_Banana = RoomObject("Banan", player_Banana.return_item_with_amount(1),None, "Take Banana", "You took the bananas", "Couldn't take item")
room_Dice = RoomObject("Dice",player_Dice.return_item_with_amount(1),None,"Take Dice", "You took the dices!", "Couldn't take item")
room_Key = RoomObject("Key",player_Key.return_item_with_amount(1),None,"Take Key", "You took the keys!", "Couldn't take item")
room_Shovel = RoomObject("Shovel", shovel, None, "Take Shovel", "You took the Shovel", "Couldn't take item")
room_Diamond = RoomObject("Diamond", player_Diamond.return_item_with_amount(1), None, "Take Diamond", "You took a diamond!", "Couldn't take item")
room_Coin = RoomObject("Coin", player_Coin.return_item_with_amount(1), None, "Take Coin", "You took a coin!", "Couldn't take item")
# Je met none pour ensuite gérer le remplissage à partir de random manager
room_Chest = RoomObject("Chest", None, player_Key.return_item_with_amount(1), "Open Chest","You opened the chest!", "You do not have a Key:")
room_Hole = RoomObject("Hole", None, shovel, "Dig Hole","You dug the hole out!", "You do not have a shovel:")

items = [room_Apple,room_Banana,room_Dice,room_Key, room_Diamond, room_Chest, room_Hole, room_Shovel]
for item in items:
    if item.name not in room_items_dictionary:
        room_items_dictionary[item.name] = item


    

