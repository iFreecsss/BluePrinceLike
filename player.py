from inventory import *
from item import *

class Player:
    '''
    Représente le joueur, gère sa position, sa direction et son inventaire.
    
    Contient également la logique métier pour interagir avec les objets 
    (vérifier, utiliser, consommer).
    
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
    
    Attributes
    ----------
    position : tuple
        Position (x, y) actuelle du joueur sur la grille (carte).
    direction : int
        Direction (0-3) vers laquelle le joueur fait face (0=N, 1=O, 2=S, 3=E).
    inventory : Inventory
        Instance de la classe `Inventory` gérant les objets possédés 
        par le joueur.
    '''

    def __init__(self):
        self.position = (2,8)
        self.direction = 0
        self.inventory = Inventory()

    def move(self,position):
        '''
        Met à jour la position du joueur.
        
        Parameters
        ----------
        position : tuple
            Les nouvelles coordonnées (x, y) du joueur.
        '''
        
        self.position = position
    
    def face(self,direction):
        '''
        Met à jour la direction (orientation) du joueur.
        
        Parameters
        ----------
        direction : int
            La nouvelle direction (0-3).
        '''
        
        self.direction = direction
    
    def check_condition(self, condition :Item):
        '''
        Vérifie si le joueur possède un objet requis en quantité suffisante.
        (Ne consomme pas l'objet).
        
        Parameters
        ----------
        condition : Item
            L'objet (et sa quantité) requis pour une action. Si None, 
            retourne toujours True.
        
        Returns
        -------
        bool
            True si la condition est remplie (ou s'il n'y a pas de condition), 
            False si le joueur n'a pas l'objet ou pas assez.
        '''
        
        inventory = self.inventory.inventory
        if condition is not None:
            if condition.name in inventory and inventory[condition.name].quantity >= condition.quantity:
                return True
            else:
                return False
        else:
            return True

    def check_Item(self,condition : Item, item: Item, test=False):
        '''
        Gère la transaction d'une action : vérifie et consomme la 
        condition (coût), puis donne l'objet (récompense).
        
        Gère le cas spécial `test=True` (Marteau) qui ignore la condition.
        
        Parameters
        ----------
        condition : Item
            L'objet requis (coût) que le joueur doit payer (ex: 1 Clé).
        item : Item
            L'objet (récompense) que le joueur reçoit (ex: 1 Pomme).
        test : bool
            Si True (ex: Marteau), ignore la `condition` (le coût n'est 
            pas vérifié ni consommé).
        
        Returns
        -------
        bool
            True si l'action (consommation du coût + ajout de la récompense) 
            a réussi, False sinon.
        '''
        
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
        '''
        Tente de consommer un objet de l'inventaire, ou vérifie 
        seulement s'il est présent.
        
        C'est la méthode de bas niveau pour "payer" un coût ou "vérifier" 
        une ressource.
        
        Parameters
        ----------
        item : Item
            L'objet à utiliser/vérifier (et sa quantité).
        test : bool
            - Si `True`: Vérifie seulement si le joueur a l'objet en 
                quantité suffisante (ne consomme rien).
            - Si `False`: Tente de consommer l'objet.
        
        Returns
        -------
        bool
            True si l'opération (vérification ou consommation) est un succès, 
            False si le joueur n'a pas l'objet en quantité suffisante.
        '''
        
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
    
