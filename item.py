from abc import ABC, abstractmethod
import random
import copy

class Item(ABC): 
    """
    Classe de base abstraite pour tous les objets du jeu définit interface commune
    """
    def __init__(self, name, image_path, quantity = 1):
        self.name = name
        self.image_path = image_path
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
    def __init__(self, name, image_path, quantity=1):
        super().__init__(name, image_path,quantity)
    
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
    def __init__(self, name, image_path,quantity=1):
        super().__init__(name, image_path, quantity)

    def add(self,amount):
        pass

    def use(self, player, amount):
        """
        Cette fonction renvoie True, cela vient du fait que si l'utilisateur arrive a utiliser l'objet cela veut dire qu'il existe dans son inventaire.
        """
        player.inventory.add_item(self)
        return True

class RegenerativeItem(Item):
    def __init__(self, name, image_path,quantity=1, regenerate : Item = None, amount=1):
        super().__init__(name, image_path, quantity)
        self.regenerate = regenerate.return_item_with_amount(amount)
        
    def add(self,amount):
        pass

    def use(self, player, amount):
        for _ in range(self.quantity):
            player.inventory.add_item(self.regenerate)
        return True

#INSTANTATION DES OBJETS
item_None = NonConsumableItem(None,None,None)
player_Diamond = ConsumableItem("Diamond", "Images/Icons/diamond_icon.png", 1) #10
player_Key = ConsumableItem("Key", "Images/Icons/key_icon.png", 1) #15
player_Footsteps = ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 1) #70
player_Dice = ConsumableItem("Dice", "Images/Icons/dice_icon.png", 1) #5

shovel = NonConsumableItem("Shovel", "Images/Icons/dice_icon.png", 1)

player_Apple = RegenerativeItem("Apple", "Images/Icons/apple_icon.png", 1, player_Footsteps, 2)
player_Banana = RegenerativeItem("Banana","Images/Icons/banana_icon.png", 1, player_Footsteps, 3)

