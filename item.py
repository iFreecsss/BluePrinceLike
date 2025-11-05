from abc import ABC, abstractmethod
import random

class Item(ABC):
    """
    Classe de base abstraite pour tous les objets du jeu définit interface commune
    """
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

    @abstractmethod
    def use(self, game_logic):
        """
        Méthode abstraite pour utiliser l'objet => dépendra du type d'objet.
        """
        pass

class ConsumableItem(Item):
    """
    Un objet consommable qui s'empile (ex: pièces, pas) + hérite de Item.
    """
    def __init__(self, name, image_path, quantity=1):
        super().__init__(name, image_path)
        self.quantity = quantity

    def add(self, amount=1):
        """Ajoute une certaine quantité de cet objet."""
        self.quantity += amount

    def use(self, game_logic, amount=1):
        """
        Tente d'utiliser (consommer) une certaine quantité de l'objet.
        Retourne True si l'utilisation a réussi, False sinon.
        """
        if self.quantity >= amount:
            self.quantity -= amount
            return True
        else:
            return False
            

class NonConsumableItem(Item):
    """
    Un objet non consommable (unique) (ex: pelle) + hérite de Item.
    """
    def __init__(self, name, image_path):
        super().__init__(name, image_path)

    def use(self, game_logic):
        """
        Utiliser un objet unique déclenche une logique spécifique dans le jeu.
        Par exemple, 'game_logic' pourrait vérifier si le joueur est devant une porte pour l'ouvrir ou devant un truc à creuser.
        """
        # La logique de ce qui se passe (ex: ouvrir une porte)
        # serait gérée dans game_logic, appelée depuis handle_inputs
        pass

class FloorItem(ABC):
    """
    Classe de base abstraite pour les objets placés sur le sol dans le jeu.
    """
    def __init__(self, name, image_path):
        self.name = name  # Position sous forme de tuple (x, y)
        self.image_path = image_path

    @abstractmethod
    def collect(self, game_logic):
        """
        logique pour collecter l'objet du sol soit pour qu'il s'ajoute à l'inventaire du joueur soit 
        pour déclencher une action spécifique dans le jeu.
        """
        pass

class Apple(FloorItem):
    """
    Un objet pomme placé sur le sol que le joueur peut collecter.
    """
    def __init__(self):
        super().__init__("Apple", "Images/Icons/apple_icon.png")

    def collect(self, game_logic):
        """
        Ajoute 2 pas à l'inventaire du joueur lorsqu'il collecte la pomme.
        """
        game_logic.player.inventory.add_item(ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 2))

class Banana(FloorItem):
    """
    Un objet banane placé sur le sol que le joueur peut collecter.
    """
    def __init__(self):
        super().__init__("Banana", "Images/Icons/banana_icon.png")

    def collect(self, game_logic):
        """
        Ajoute 3 pas à l'inventaire du joueur lorsqu'il collecte la banane.
        """
        game_logic.player.inventory.add_item(ConsumableItem("Footsteps", "Images/Icons/footsteps_icon.png", 3))

class Diamond(FloorItem):
    """
    Un objet diamant placé sur le sol que le joueur peut collecter.
    """
    def __init__(self, quantity=1):
        self.quantity = quantity
        super().__init__("Diamond", "Images/Icons/diamond_icon.png")

    def collect(self, game_logic):
        """
        Ajoute 5 pièces à l'inventaire du joueur lorsqu'il collecte le diamant.
        """
        game_logic.player.inventory.add_item(ConsumableItem("Diamond", "Images/Icons/diamond_icon.png", self.quantity))

class Key(FloorItem):
    """
    Un objet clé placé sur le sol que le joueur peut collecter.
    """
    def __init__(self, quantity=1):
        self.quantity = quantity
        super().__init__("Key", "Images/Icons/key_icon.png")

    def collect(self, game_logic):
        """
        Ajoute une clé unique à l'inventaire du joueur lorsqu'il collecte la clé.
        """
        game_logic.player.inventory.add_item(ConsumableItem("Key", "Images/Icons/key_icon.png", self.quantity))

class Dice(FloorItem):
    """
    Un objet dé placé sur le sol que le joueur peut collecter.
    """
    def __init__(self, quantity=1):
        self.quantity = quantity
        super().__init__("Dice", "Images/Icons/dice_icon.png")

    def collect(self, game_logic):
        """
        Ajoute un dé unique à l'inventaire du joueur lorsqu'il collecte le dé.
        """
        game_logic.player.inventory.add_item(ConsumableItem("Dice", "Images/Icons/dice_icon.png", self.quantity))