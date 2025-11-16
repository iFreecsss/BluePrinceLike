from abc import ABC, abstractmethod
import random
import copy

class Item(ABC): 
    '''
    Classe de base abstraite pour tous les objets (items) du jeu.
    
    Définit une interface commune pour tous les objets, y compris leurs 
    attributs de base (nom, image, quantité) et les méthodes abstraites 
    pour leur utilisation et leur ajout.
    
    Attributes
    ----------
    name : str
        Le nom de l'objet (ex: "Diamond", "Shovel").
    description : str
        Courte description de l'objet pour l'UI (infobulle).
    image_path : str
        Chemin d'accès au fichier image de l'icône de l'objet.
    quantity : int
        La quantité de l'objet. Vaut 1 pour les non-consommables.
    '''
    
    def __init__(self, name, image_path, quantity = 1, description=""):
        self.name = name
        self.description = description
        self.image_path = image_path
        self.quantity = quantity
    
    def set_quantity(self, quantity):
        '''
        Définit la quantité de l'objet.
        
        Parameters
        ----------
        quantity : int
            La nouvelle quantité à assigner.
        '''
        
        self.quantity = quantity
    @abstractmethod
    def use(self, player, amount):
        '''
        Méthode abstraite pour utiliser l'objet.
        
        La logique spécifique (consommer, équiper, ajouter un autre objet) 
        est définie dans les sous-classes.

        Parameters
        ----------
        player : Player
            L'instance du joueur qui utilise l'objet.
        amount : int
            La quantité à utiliser (la logique d'utilisation peut différer).
        '''
        
        pass
    @abstractmethod
    def add(self, amount):
        '''
        Méthode abstraite pour ajouter une quantité à l'objet.
        
        Principalement pour les objets empilables.
        
        Parameters
        ----------
        amount : int
            La quantité à ajouter.
        '''
        
        pass

    def return_item_with_amount(self, quantity):
        '''
        Renvoie une nouvelle copie (deepcopy) de l'instance de l'objet 
        avec une quantité spécifiée par le joueur.
        
        Parameters
        ----------
        quantity : int
            La quantité désirée pour la nouvelle instance.
            
        Returns
        -------
        Item
            Une nouvelle instance de l'objet avec la quantité définie.
        '''
        
        item_copy = copy.deepcopy(self)
        item_copy.quantity = quantity
        return item_copy

class ConsumableItem(Item):
    '''
    Un objet consommable qui s'empile (ex: pièces, pas, clés).
    Hérite de Item.
    
    Attributes
    ----------
    (Hérités de Item)
    '''
    
    def __init__(self, name, image_path, quantity=1, description=""):
        super().__init__(name, image_path, quantity, description)
    
    def use(self, player, amount=0):
        '''
        Tente d'utiliser (consommer) une quantité de l'objet de 
        l'inventaire du joueur.
        
        La quantité consommée est `self.quantity` (la quantité de 
        l'instance passée en paramètre, ex: 2 clés).
        
        Parameters
        ----------
        player : Player
            L'instance du joueur dont l'inventaire sera affecté.
        amount : int, optional
            Paramètre ignoré (présent pour la compatibilité de l'interface).
        
        Returns
        -------
        bool
            True si le joueur avait assez d'objets et qu'ils ont été 
            consommés, False sinon.
        '''
        
        inventory = player.inventory.inventory
        if self.name in inventory:
            if inventory[self.name].quantity - self.quantity >= 0:
                inventory[self.name].quantity -= self.quantity
                return True
            else:
                return False
    
    def add(self, amount):
        '''
        Augmente la quantité de cet objet.
        
        Parameters
        ----------
        amount : int
            La quantité à ajouter.
        '''
        self.quantity += amount

class NonConsumableItem(Item):
    '''
    Un objet non consommable (unique) (ex: pelle, marteau).
    Hérite de Item.
    
    Attributes
    ----------
    (Hérités de Item)
    '''
    
    def __init__(self, name, image_path,quantity=1, description=""):
        super().__init__(name, image_path, quantity, description)

    def add(self,amount):
        '''
        Ne fait rien (les objets non-consommables ne s'empilent pas).

        Parameters
        ----------
        amount : int
            Quantité ignorée.
        '''
        pass

    def use(self, player, amount):
        '''
        Logique d'utilisation pour un non-consommable.
        
        Dans ce contexte (appelé par `player.check_Item`), cette 
        méthode signifie "s'ajouter à l'inventaire du joueur".

        Parameters
        ----------
        player : Player
            Le joueur qui reçoit l'objet.
        amount : int
            Paramètre ignoré.

        Returns
        -------
        bool
            Toujours True.
        '''
        
        player.inventory.add_item(self)
        return True

class RegenerativeItem(Item):
    '''
    Un objet consommable qui donne un autre objet lorsqu'il est utilisé 
    (ex: Pomme -> Pas). Hérite de Item.
    
    Attributes
    ----------
    regenerate : Item
        L'instance de l'objet (ex: Footsteps) à donner au joueur 
        lors de l'utilisation, avec la quantité à donner.
    (Autres hérités de Item)
    '''
    
    def __init__(self, name, image_path,quantity=1, regenerate : Item = None, amount=1, description=""):
        '''
        Initialise l'objet régénératif.
        
        Parameters
        ----------
        name : str
            Nom de l'objet (ex: "Apple").
        image_path : str
            Chemin de l'image.
        quantity : int
            Quantité de cet objet (ex: 1 Pomme).
        regenerate : Item
            L'objet *modèle* à régénérer (ex: `player_Footsteps`).
        amount : int
            La quantité de `regenerate` à donner (ex: 2 Pas).
        description : str
            Description de l'objet.
        '''
        super().__init__(name, image_path, quantity, description)
        self.regenerate = regenerate.return_item_with_amount(amount)
        
    def add(self,amount):
        '''
        Ne fait rien.
        
        Parameters
        ----------
        amount : int
            Quantité ignorée.
        '''
        
        pass

    def use(self, player, amount):
        '''
        Utilise l'objet en ajoutant l'objet `self.regenerate` à 
        l'inventaire du joueur.
        
        Le nombre d'objets régénérés est `self.regenerate.quantity`, 
        répété `self.quantity` fois.
        
        Parameters
        ----------
        player : Player
            Le joueur qui reçoit l'objet régénéré.
        amount : int
            Paramètre ignoré.
        
        Returns
        -------
        bool
            Toujours True.
        '''
        
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


