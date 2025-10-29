
import pygame
import numpy as np
from map import *
from sys import exit

class UI:
    def __init__(self):
        #Données d'affichage
        self.data= {}
        #Dimensions de l'écran de jeu de Pygames et d'autres paramètres
        self.SCREEN_WIDTH = 1440    
        self.SCREEN_HEIGHT = 720
        self.COLOR_BACKGROUND = (14, 38, 82)
        self.COLOR_GRID_LIGHT = (40, 90, 180)
        self.COLOR_PANEL_BORDER = (200, 220, 255)
        self.COLOR_PANEL_HIGHLIGHT = (255, 0, 0)

        #Définition des dimensions des différentes parties de l'UI
        self.MARGIN = 40
        self.INVENTORY_WIDTH, self.INVENTORY_HEIGHT = 680,200
        self.MAP_WIDTH, self.MAP_HEIGHT = 355, (self.SCREEN_HEIGHT - (2 * self.MARGIN))
        self.ACTION_MENU_WIDTH, self.ACTION_MENU_HEIGHT = 920, 400

        #Définition de la carte
        self.map = Map()
        self.cell_mapping = self.init_cell_Mapping()

        #Pygame window init
        pygame.init()
        self.display_surface = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("CMI BluePrints")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 30)
        self.COLOR_TEXT = (255, 255, 255)
        
        self.message_text = None
        self.message_timer = 0
        self.MESSAGE_DURATION = 1250
        self.message_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.COLOR_MESSAGE_TEXT = (255, 220, 220) # Un blanc-cassé-rose

        self.main_view_rect = pygame.Rect(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT)
        self.main_view_rect.left = self.MARGIN
        self.main_view_rect.top = self.MARGIN

        self.inventory_rect = pygame.Rect(0, 0, self.INVENTORY_WIDTH, self.INVENTORY_HEIGHT)
        self.inventory_rect.left = self.main_view_rect.right + self.MARGIN
        self.inventory_rect.top = self.MARGIN

        self.current_room_panel_rect = pygame.Rect(0, 0, 200, 200)
        self.current_room_panel_rect.left = self.inventory_rect.right + self.MARGIN
        self.current_room_panel_rect.top = self.MARGIN

        self.draw_room_rect = pygame.Rect(0, 0, self.ACTION_MENU_WIDTH, self.ACTION_MENU_HEIGHT)
        self.draw_room_rect.left = self.inventory_rect.left
        self.draw_room_rect.top = self.inventory_rect.bottom + self.MARGIN

        self.main_border_rect = pygame.Rect(20, 20, self.SCREEN_WIDTH - 40, self.SCREEN_HEIGHT - 40)

    def init_cell_Mapping(self):
        cell_mapping = np.empty((5,9), dtype=np.object_)

        cell_width = self.MAP_WIDTH // 5
        cell_height = self.MAP_HEIGHT // 9

        for w in range(0,5):
            for h in range(0,9):
                current_cell = pygame.Rect(0, 0, cell_width, cell_height)
                cell_x = w * cell_width + self.MARGIN
                cell_y = h * cell_height + self.MARGIN
                current_cell.topleft = (cell_x, cell_y)
                cell_mapping[w,h] = current_cell
        
        return cell_mapping

    def display_MAP(self, map_array):
        #Divise la carte en 45 cellules (cells) pour poser chacune des chambres
        active_rooms = [(i, j) for i in range(map_array.shape[0]) for j in range(map_array.shape[1]) if map_array[i, j] is not None]

        for x,y in active_rooms:

            cell_rect = self.cell_mapping[x,y]
            room = map_array[x,y]

            if hasattr(room, 'image'):
                
                img = pygame.image.load(map_array[x,y].image).convert_alpha()
                img = pygame.transform.scale(img, (cell_rect.width, cell_rect.height)) 
                
                rotation_angle = room.orientation * 90
                
                img_rotated = pygame.transform.rotate(img, rotation_angle)
                img_rect = img_rotated.get_rect(center = cell_rect.center)

                self.display_surface.blit(img_rotated, img_rect)
            else:
                    raise ValueError(f"Image non trouvée pour display_map image {map_array[x,y].name}")

    def display_current_room(self, map_array, player_position):
        player_x, player_y = player_position
        if hasattr(map_array[player_x,player_y], 'image'):
            img = pygame.image.load(map_array[player_x,player_y].image).convert_alpha()
            img = pygame.transform.scale(img, (200, 200))
            self.display_surface.blit(img, self.current_room_panel_rect)
        else:
            print("WARNING- Pas d'images pour la chambre!")
            pass

    def display_Player(self, player_position, player_direction):
        WHITE = (255, 255, 255)
        WIDTH = 5
        player_x, player_y = player_position
        current_player_cell = self.cell_mapping[player_x,player_y]
        
        BORDER_COLOR = WHITE
        BORDER_WIDTH = 1
        
        points = [
            current_player_cell.topleft,
            current_player_cell.topright,
            current_player_cell.bottomright,
            current_player_cell.bottomleft
        ]
        
        pygame.draw.lines(self.display_surface, BORDER_COLOR, True, points, BORDER_WIDTH)   # contour blanc autour de la case active

        if player_direction == 0:
            pygame.draw.line(self.display_surface, WHITE,current_player_cell.topleft, current_player_cell.topright , WIDTH)
        elif player_direction == 1:
            pygame.draw.line(self.display_surface, WHITE,current_player_cell.topleft, current_player_cell.bottomleft , WIDTH)
        elif player_direction == 2:
            pygame.draw.line(self.display_surface, WHITE,current_player_cell.bottomleft, current_player_cell.bottomright , WIDTH)
        elif player_direction == 3:
            pygame.draw.line(self.display_surface, WHITE,current_player_cell.bottomright, current_player_cell.topright , WIDTH)
        else:
            raise ValueError("Valeur impossible de direction")
    
    def draw_background_grid(self):
        """Dessine la grille de fond sur la surface d'affichage."""
        self.display_surface.fill(self.COLOR_BACKGROUND)
        for x in range(0, self.SCREEN_WIDTH, 40):
            pygame.draw.line(self.display_surface, self.COLOR_GRID_LIGHT, (x, 0), (x, self.SCREEN_HEIGHT))
        for y in range(0, self.SCREEN_HEIGHT, 40):
            pygame.draw.line(self.display_surface, self.COLOR_GRID_LIGHT, (0, y), (self.SCREEN_WIDTH, y))

    def draw_elements(self):
        """Dessine les panneaux et les images de l'interface."""
        # Cadre général et Panneaux
        pygame.draw.rect(self.display_surface, self.COLOR_PANEL_BORDER, self.main_border_rect, 4, border_radius=10)
        pygame.draw.rect(self.display_surface, self.COLOR_BACKGROUND, self.main_view_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, self.COLOR_BACKGROUND, self.inventory_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, self.COLOR_BACKGROUND, self.draw_room_rect, border_radius=10)

    def draw_room_choice_screen(self):
        """
        Affiche les 3 salles tirées au hasard dans le panneau self.draw_room_rect.
        """
        # le rectangle prévu à l'effet des choix de salle
        panel = self.draw_room_rect 
        # titre
        title_text = self.font.render("Please choose a room : ", True, self.COLOR_TEXT)
        # centrage du titre en haut du panneau au milieu
        title_rect = title_text.get_rect(center=(panel.centerx, panel.top + self.MARGIN))
        self.display_surface.blit(title_text, title_rect)
        # on récupère toute la liste des salles à afficher qu'on a stockées dans self.data dans game.py
        room_choices = self.data.get('room_choices', [])
        # ainsi que l'index de la salle actuellement sélectionnée
        current_index = self.data.get('current_choice_index', 0)

        if not room_choices:
            return
        
        # taille des cadres autour des cartes
        choice_width = 250  
        choice_height = 250 
        
        # Espacement entre les cartes
        padding = (panel.width - (3 * choice_width)) // 4
        
        # position verticale des cartes
        choice_y = panel.top + self.MARGIN + 40 # 40 pour laisser place au titre

        for i, room in enumerate(room_choices):
            # pour chaque room on calcule sa position horizontale dans le pannel 
            choice_x = panel.left + padding + i * (choice_width + padding)
            choice_rect = pygame.Rect(choice_x, choice_y, choice_width, choice_height)
            
            if i == current_index:
                # si c'est la salle sélectionnée on met en évidence en rouge plus épais
                border_color = self.COLOR_PANEL_HIGHLIGHT
                border_width = 6
            else:
                border_color = self.COLOR_PANEL_BORDER
                border_width = 4
            
            # cadre autour de la carte de la salle
            pygame.draw.rect(self.display_surface, border_color, choice_rect, border_width, border_radius=10)
            # ON DOIT AFFICHER L'IMAGE DANS LE CADRE DES CHOIX DANS LE SENS OU ELLE SERA PLACEE 
            # CET ESSAI EST INFRUCTUEUX CAR L'IMAGE TOUJOURS ORIENTEE A L'ENDROIT
            img = pygame.image.load(room.image).convert_alpha()
            img = pygame.transform.scale(img, (210, 210))
            rotation_angle = room.orientation * 90
            img_rotated = pygame.transform.rotate(img, rotation_angle)
            img_rect = img_rotated.get_rect(center=(choice_rect.centerx, choice_rect.centery)) # +30 pour descendre un peu
            self.display_surface.blit(img_rotated, img_rect) # on affiche les salles déjà tournées

    def set_data(self, data):
        self.data = data
        
        new_message = self.data.get('warning_message')
        if new_message:
            self.message_text = new_message
            # on stocke l'heure de réception (en ms)
            self.message_timer = pygame.time.get_ticks()
            
    def draw_warning_message(self):
        """
        Affiche le message d'avertissement au centre de la carte s'il existe
        et si son minuteur n'est pas écoulé.
        """
        if self.message_text:
            current_time = pygame.time.get_ticks()
            
            if current_time - self.message_timer < self.MESSAGE_DURATION:
                
                text_surface = self.message_font.render(self.message_text, True, self.COLOR_MESSAGE_TEXT)
                text_rect = text_surface.get_rect(center=self.main_view_rect.center) # centré sur la map
                
                # fond semi-transparent
                bg_rect = text_rect.inflate(20, 10) # 20px de marge H, 10px de marge V
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 150)) # Noir semi-transparent
                
                self.display_surface.blit(bg_surface, bg_rect)
                self.display_surface.blit(text_surface, text_rect)
                
            else:
                # le temps est écoulé on efface le message
                self.message_text = None
                self.message_timer = 0
    
    def draw_victory_screen(self):
        """
        Affiche l'écran de victoire.
        """
        self.display_surface.fill(self.COLOR_BACKGROUND)
        
        victory_font = pygame.font.SysFont('Arial', 80, bold=True)
        text_surface = victory_font.render("VICTORY !", True, self.COLOR_TEXT)
        
        # texte centré
        text_rect = text_surface.get_rect(
            center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 50)
        )
        self.display_surface.blit(text_surface, text_rect)

        sub_text_surface = self.font.render(
            "You have reached the AnteChamber and completed the game!",
            True,
            self.COLOR_PANEL_BORDER # Une couleur un peu différente
        )
        sub_text_rect = sub_text_surface.get_rect(
            center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 40)
        )
        self.display_surface.blit(sub_text_surface, sub_text_rect)

        quit_text_surface = self.font.render(
            "Press Escape to exit.",
            True,
            self.COLOR_GRID_LIGHT # Couleur discrète
        )
        quit_text_rect = quit_text_surface.get_rect(
            center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT - 60)
        )
        self.display_surface.blit(quit_text_surface, quit_text_rect)
    
    def run(self):  
        """Lance la boucle de jeu principale qui gère les événements et le dessin."""
        inputs = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # échap pour quitter le jeu
                    pygame.quit()
                    exit()
                if event.key == pygame.K_z:
                    inputs.append("UP")
                elif event.key == pygame.K_s:
                    inputs.append("DOWN")
                elif event.key == pygame.K_q:
                    inputs.append("LEFT")
                elif event.key == pygame.K_d:
                    inputs.append("RIGHT")
                elif event.key == pygame.K_SPACE:
                    inputs.append("SPACE")
                elif event.key == pygame.K_LEFT: # Flèche gauche
                    inputs.append("LEFT_ROOM")
                elif event.key == pygame.K_RIGHT: # Flèche droite
                    inputs.append("RIGHT_ROOM")
                elif event.key == pygame.K_RETURN: # Touche Entrée
                    inputs.append("ENTER")
        
        current_game_state = self.data.get('game_state')
        
        if current_game_state == "VICTORY":
            # si on gagne on dessine l'écran de victoire
            self.draw_victory_screen()
            
        # elif current_game_state == "GAME_OVER":
            # self.draw_game_over_screen()
        
        else : 
            self.draw_background_grid()

            self.draw_elements()
            self.display_MAP(self.data['mapping'])
            self.display_current_room(self.data['mapping'],self.data['position'])
            # mis à part car il faut que tout le reste soit dessiné quelque soit le mode
            if current_game_state == "DRAWING_ROOM":
                self.draw_room_choice_screen() 
            
            self.draw_warning_message()
            self.display_Player(self.data['position'],self.data['direction'])
        
        pygame.display.update()
        self.clock.tick(60)
        return inputs