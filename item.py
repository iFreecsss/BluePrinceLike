from abc import ABC, abstractmethod
import random
import copy

class Item(ABC): 
    """
    Classe de base abstraite pour tous les objets du jeu définit interface commune
    """
    def __init__(self, name, image_path, quantity = 1, description=""):
        self.name = name
        self.description = description
        self.image_path = image_path
        self.quantity = quantity
    
    def set_quantity(self, quantity):
        self.quantity = quantity
    @abstractmethod
    def use(self, player, amount):
        """
        Méthode abstraite pour utiliser l'objet => dépendra du type d'objet.
        """
        pass

    def return_item_with_amount(self, quantity):
        """
        Renvoie une copie de l'instance de l'objet avec une quantité spécifié par le joueur.
        """
        item_copy = copy.deepcopy(self)
        item_copy.quantity = quantity
        return item_copy

class ConsumableItem(Item):
    """
    Un objet consommable qui s'empile (ex: pièces, pas) + hérite de Item.
    """
    def __init__(self, name, image_path, quantity=1, description=""):
        super().__init__(name, image_path, quantity, description)
    
    def use(self, player, amount=0):
        """
        Tente d'utiliser (consommer) une certaine quantité de l'objet.
        Retourne True si l'utilisation a réussi, False sinon.
        """
        inventory = player.inventory.inventory
        if self.name in inventory:
            if inventory[self.name].quantity - self.quantity >= 0:
                inventory[self.name].quantity -= self.quantity
                return True
            else:
                return False
    
    def add(self, amount):
        self.quantity += amount

    
            

class NonConsumableItem(Item):
    """
    Un objet non consommable (unique) (ex: pelle) + hérite de Item.
    """
    def __init__(self, name, image_path,quantity=1, description=""):
        super().__init__(name, image_path, quantity, description)

    def add(self,amount):
        pass

    def use(self, player, amount):
        """
        Cette fonction renvoie True, cela vient du fait que si l'utilisateur arrive a utiliser l'objet cela veut dire qu'il existe dans son inventaire.
        """
        player.inventory.add_item(self)
        return True

class RegenerativeItem(Item):
    def __init__(self, name, image_path,quantity=1, regenerate : Item = None, amount=1, description=""):
        super().__init__(name, image_path, quantity, description)
        self.regenerate = regenerate.return_item_with_amount(amount)
        
    def add(self,amount):
        pass

    def use(self, player, amount):
        for _ in range(self.quantity):
            player.inventory.add_item(self.regenerate)
        return True

#INSTANTATION DES OBJETS

player_Diamond = ConsumableItem("Diamond", "Images/Icons/diamond_icon.png", 1, "Used to purchase and place new rooms.") 
player_Key = ConsumableItem("Key", "Images/Icons/key_icon.png", 1, "Opens locked doors (1 key) or double-locked doors (2 keys), chests and lockers.") 
player_Footsteps = ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 1, "Your stamina. Moving and building consumes steps. Game Over if 0.") 
player_Dice = ConsumableItem("Dice", "Images/Icons/dice_icon.png", 1, "Reroll the available room choices if you don't like them.") 
player_Coin = ConsumableItem("Coin", "Images/Icons/coin_icon.png", 1, "Can be used to buy in stores") 

player_hammer = NonConsumableItem("Hammer", "Images/Icons/hammer_icon.png", 1, "A heavy tool. Useful to highjack chests.")
player_shovel = NonConsumableItem("Shovel", "Images/Icons/shovel_icon.png", 1, "Required to dig up holes interactions for loot.")
player_charm_chroma = NonConsumableItem("Charm Chroma", "Images/Icons/charm_chroma_icon.png", 1, "Increases the probability of finding items in rooms by 50%.")
player_metal_detector = NonConsumableItem("Metal Detector", "Images/Icons/metal_detector_icon.png", 1, "Drastically increases chance to find Keys and Coins.")
player_lock_picking_kit = NonConsumableItem("Lock Picking Kit", "Images/Icons/lock_picking_kit_icon.png", 1, "Makes locks easier. Opens simple locks for free and spare 1 key when you open a double lock !")

player_Apple = RegenerativeItem("Apple", "Images/Icons/apple_icon.png", 1, player_Footsteps, 2, "A healthy snack. Restores +2 Footsteps immediately.")
player_Banana = RegenerativeItem("Banana","Images/Icons/banana_icon.png", 1, player_Footsteps, 3, "Rich in energy. Restores +3 Footsteps immediately.")
player_ClubSandwich = RegenerativeItem("Club Sandwich", None, 1, player_Footsteps, 15, "A classic. Restores +15 Footsteps immediately.")
player_ChefSalad = RegenerativeItem("Chef Salad",None, 1, player_Footsteps, 5, "Healthy for the whole family. Restores +5 Footsteps per Green Room in the House.")
player_TomatoSoup = RegenerativeItem("Tomato Soup",None, 1, player_Footsteps, 5, "An acquired taste. Restores +5 Footsteps per Red Room in the House.")


