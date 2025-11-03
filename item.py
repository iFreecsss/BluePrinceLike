from abc import ABC, abstractmethod

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