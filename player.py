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
    
    def check_condition(self, condition :Item):
        inventory = self.inventory.inventory
        if condition is not None:
            if condition.name in inventory and inventory[condition.name].quantity >= condition.quantity:
                return True
            else:
                return False
        else:
            return True

    def check_Item(self,condition : Item, item: Item, test=False):
        inventory = self.inventory.inventory
        # On vérifie si l'item de butin (item) existe et est déja dans l'inventaire
        # On le fait ici pour éviter les "None.name"
        item_name_in_inventory = False

        # Si test=True cela signifie que le marteau est utilisé.
        # On ignore complètement la condition (la clé)
        # et on passe directement à l'ajout du butin
        if test:
            if item_name_in_inventory:
                inventory[item.name].add(item.quantity)
            elif item: # S'il y a du butin (item n'est pas None)
                item.use(self, item.quantity)
            # On retourne True car l'action a réussi (le marteau a fonctionné)
            return True
        
        if not condition: 
            if item.name in inventory:
                inventory[item.name].add(item.quantity) 
            else:
                item.use(self, item.quantity)
            return True
        
        elif condition.name in inventory:
            result = self.use(condition, test=test)
            if result == True and (not isinstance(item,Inventory)):
                if item.name in inventory:
                    inventory[item.name].add(item.quantity) 
                else:
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
    
