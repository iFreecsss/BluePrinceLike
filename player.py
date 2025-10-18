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
    

    def move(self,position):
        self.position = position
    
    def face(self,direction):
        self.direction = direction
    
