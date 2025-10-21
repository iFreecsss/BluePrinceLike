
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
        self.MAP_WIDTH, self.MAP_HEIGHT = 400, (self.SCREEN_HEIGHT - (2 * self.MARGIN))
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
            current_cell = self.cell_mapping[x,y]
            pygame.draw.rect(self.display_surface, self.COLOR_BACKGROUND, current_cell, border_radius=10)
            if hasattr(map_array[x,y], 'image'):
                # changement de l'affichage car les images se chevauchaient
                # on regarde directement la cellule sur laquelle la salle doit être et on scale à partir de la taille de la cellule
                cell_rect = self.cell_mapping[x,y]
                img = pygame.image.load(map_array[x,y].image).convert_alpha()
                img = pygame.transform.scale(img, (cell_rect.width, cell_rect.height)) 
                self.display_surface.blit(img, cell_rect)
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

            img = pygame.image.load(room.image).convert_alpha()
            img = pygame.transform.scale(img, (210, 210))
            
            img_rect = img.get_rect(center=(choice_rect.centerx, choice_rect.centery)) # +30 pour descendre un peu
            self.display_surface.blit(img, img_rect)

    def set_data(self, data):
        self.data = data
    
    def run(self):  
        """Lance la boucle de jeu principale qui gère les événements et le dessin."""
        inputs = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
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
        
        self.draw_background_grid()

        self.draw_elements()
        self.display_MAP(self.data['mapping'])
        self.display_current_room(self.data['mapping'],self.data['position'])
        # mis à part car il faut que tout le reste soit dessiné quelque soit le mode
        if self.data.get('game_state') == "DRAWING_ROOM":
            self.draw_room_choice_screen() 

        self.display_Player(self.data['position'],self.data['direction'])
        
        pygame.display.update()
        self.clock.tick(60)
        return inputs