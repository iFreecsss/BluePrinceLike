from inventory import *
from item import *

class Player:
    """
    Position (x,y) -> Position du joueur sur la carte,
    x est la coordonnée horizontale
    y est la cordonnée verticale
    Le joueur débute toujours dans le entrance hall, soit la position (2,8)
    La carte est crée de façon a avoir 45 cases. La case en haut a gauche de l'écran est la coordonnée (0,0)
    L'antechambre se trouve donc à la position (2,0)

    Orientation int(x) -> Orientation du jouer:
    0 - Nord
    1 - Est
    2 - Sud
    4 - Ouest
    Le jouer débute en faisant face au NORD
    """

    def __init__(self):
        self.position = (2,8)
        self.direction = 0
        self.inventory = Inventory()

    def move(self,position):
        self.position = position
    
    def face(self,direction):
        self.direction = direction
    
    def check_Item(self,condition : Item, item: Item, test=False):
        inventory = self.inventory.inventory
        if not condition: 
            if test: return True # si pas de condition, on peut toujours faire l'action
            if item.name in inventory:
                inventory[item.name].add(item.quantity) 
            else:
                item.use(self, item.quantity)
            return True
        elif condition.name in inventory:
            result = self.use(condition, test=test)
            if result == True:
                item.use(self, item.quantity)
            return result
        else:
            return False
        
    def use(self, item : Item, test=False):
        if item and (not isinstance(item,Inventory)):
            inventory = self.inventory.inventory

            if test:
                # On vérifie juste si on a assez, on ne consomme rien
                if item.name in inventory and inventory[item.name].quantity >= item.quantity:
                    return True
                else:
                    return False
                
            result = item.use(self, item.quantity)
            return result
        else:
            return True
    
