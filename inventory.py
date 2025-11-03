from item import *

class Inventory:
    """
    Gère les objets possédés par le joueur.
    Sépare les consommables (empilables) des non-consommables (uniques).
    """
    def __init__(self):
        # Un dictionnaire pour les consommables { "nom_objet": instance_ConsumableItem }
        self.consumables = {}
        # Un dictionnaire pour les objets uniques { "nom_objet": instance_NonConsumableItem }
        self.non_consumables = {}
    
    def add_item(self, item_to_add: Item):
        """
        Ajoute un objet à l'inventaire.
        Si c'est un consommable déjà possédé, augmente la quantité.
        Si c'est un non-consommable, l'ajoute s'il n'est pas déjà présent.
        """
        if isinstance(item_to_add, ConsumableItem):
            if item_to_add.name in self.consumables:
                # Si le joueur a déjà cet objet on ajoute juste la quantité
                self.consumables[item_to_add.name].add(item_to_add.quantity)
            else:
                # Sinon on ajoute le nouvel objet au dictionnaire
                self.consumables[item_to_add.name] = item_to_add
                
        elif isinstance(item_to_add, NonConsumableItem):
            if item_to_add.name not in self.non_consumables:
                # On ajoute l'objet unique seulement s'il n'est pas déjà là
                self.non_consumables[item_to_add.name] = item_to_add


    def use_consumable(self, item_name, amount=1):
        """Tente d'utiliser un objet consommable"""
        if item_name in self.consumables:
            return self.consumables[item_name].use(None, amount)
        return False

    def has_non_consumable(self, item_name):
        """Vérifie si le joueur possède un objet unique spécifique"""
        return item_name in self.non_consumables

    def get_quantity(self, item_name):
        """Retourne la quantité d'un consommable (0 si non possédé)"""
        if item_name in self.consumables:
            return self.consumables[item_name].quantity
        return 0

    def get_all_items(self):
        """Retourne une seule liste de tous les objets pour l'affichage dans l'inventaire"""
        all_items = list(self.consumables.values()) + list(self.non_consumables.values())
        return all_items
    
