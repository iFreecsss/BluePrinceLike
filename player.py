class Player:
    """
    Position (x,y) -> Player position on the map,
    x is the horizontal coordinate
    y is the vectical coordinate
    always starts at (2,0) where the Entrance Hall is

    Orientation int(x) -> Player orientation:
    0 - North
    1 - East
    2 - South
    4 - West
    Player always starts facing NORTH
    """

    def __init__(self,position,orientation):
        self.position = (0,0)
        self.direction = 0
    

    def move(self,position):
        self.position = position
    
    def face(self,direction):
        self.direction = direction
    
