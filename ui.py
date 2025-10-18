
import pygame
import numpy as np
from map import *
from sys import exit

class UI:


    def __init__(self):
        #Dimensions de l'écran de jeu de Pygames et d'autres paramètres
        self.SCREEN_WIDTH = 1440    
        self.SCREEN_HEIGHT = 720
        self.COLOR_BACKGROUND = (14, 38, 82)
        self.COLOR_GRID_LIGHT = (40, 90, 180)
        self.COLOR_PANEL_BORDER = (200, 220, 255)
        self.map = Map()
        #Pygame window init
        pygame.init()
        self.display_surface = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("CMI BluePrints")
        self.clock = pygame.time.Clock()

        #Définition des dimensions des différentes parties de l'UI
        self.MARGIN = 40
        self.INVENTORY_WIDTH, self.INVENTORY_HEIGHT = 680,200
        self.MAP_WIDTH, self.MAP_HEIGHT = 400, (self.SCREEN_HEIGHT - (2 * self.MARGIN))
        self.ACTION_MENU_WIDTH, self.ACTION_MENU_HEIGHT = 920, 400


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


    def display_MAP(self, map_array):
        #Divise la carte en 45 cellules (cells) pour poser chacune des chambres
        cell_width = self.MAP_WIDTH // 5
        cell_height = self.MAP_HEIGHT // 9
        active_rooms = [(i, j) for i in range(map_array.shape[0]) for j in range(map_array.shape[1]) if map_array[i, j] is not None]

        for x,y in active_rooms:
            current_cell = pygame.Rect(0, 0, cell_width, cell_height)
            cell_x = x * cell_width + self.MARGIN
            cell_y = y * cell_height + self.MARGIN

            current_cell.topleft = (cell_x, cell_y)
            pygame.draw.rect(self.display_surface, self.COLOR_BACKGROUND, current_cell, border_radius=10)
            if map_array[x,y].image:
                img = pygame.image.load(map_array[x,y].image).convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                self.display_surface.blit(img, current_cell)
            else:
                raise ValueError(f"Image non trouvée pour display_map image {map_array[x,y].name}")

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

    def run(self):
        """Lance la boucle de jeu principale qui gère les événements et le dessin."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


                if event.type == pygame.KEYDOWN:
                    pass
            
            self.draw_background_grid()
            self.draw_elements()
            self.display_MAP(self.map.get_current_mapping())

            pygame.display.update()
            self.clock.tick(60)