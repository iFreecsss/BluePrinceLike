from ui import UI
from game import *

game_interface = UI()
game_logic = Game()


while(True):
    game_interface.set_data(game_logic.publish_data()) 
    inputs = game_interface.run()
    game_logic.handle_inputs(inputs)