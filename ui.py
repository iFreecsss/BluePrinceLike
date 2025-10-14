
import pygame
from sys import exit

class UI:
    def __init__(self):
        # --- Constantes et Initialisation de Pygame ---
        self.SCREEN_WIDTH = 1440
        self.SCREEN_HEIGHT = 720
        self.COLOR_BACKGROUND = (14, 38, 82)
        self.COLOR_GRID_LIGHT = (40, 90, 180)
        self.COLOR_PANEL_BORDER = (200, 220, 255)

        pygame.init()
        self.display_surface = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("CMI BluePrints")
        self.clock = pygame.time.Clock()

        # --- Création des rectangles pour l'UI ---
        MARGIN = 40
        self.main_view_rect = pygame.Rect(0, 0, 400, self.SCREEN_HEIGHT - (2 * MARGIN))
        self.main_view_rect.left = MARGIN
        self.main_view_rect.top = MARGIN

        self.inventory_rect = pygame.Rect(0, 0, 680, 200)
        self.inventory_rect.left = self.main_view_rect.right + MARGIN
        self.inventory_rect.top = MARGIN

        self.current_room_panel_rect = pygame.Rect(0, 0, 200, 200)
        self.current_room_panel_rect.left = self.inventory_rect.right + MARGIN
        self.current_room_panel_rect.top = MARGIN

        self.draw_room_rect = pygame.Rect(0, 0, 920, 400)
        self.draw_room_rect.left = self.inventory_rect.left
        self.draw_room_rect.top = self.inventory_rect.bottom + MARGIN

        self.main_border_rect = pygame.Rect(20, 20, self.SCREEN_WIDTH - 40, self.SCREEN_HEIGHT - 40)
        
        # --- Gestion des Salles ---
        # 1. Base de données des salles
        self.room_data = {
            'entrance_hall': {'path': 'Images/Rooms/Entrance_Hall.png'},
            'library': {'path': 'Images/Rooms/Library.png'}
        }
        
        # 2. Variables pour stocker les images de la salle ACTUELLE
        self.current_room_image = None
        self.current_room_image_rect = None
        self.current_room_icon = None
        self.current_room_icon_rect = None

        # 3. On charge la salle de départ
        self.set_current_room('entrance_hall')


    # <--- NOUVELLE FONCTION ---
    def set_current_room(self, room_name):
        """
        Charge et prépare les images pour une salle donnée.
        Cette fonction met à jour les images qui seront affichées.
        """
        if room_name in self.room_data:
            try:
                # Charger l'image originale une seule fois
                original_image = pygame.image.load(self.room_data[room_name]['path']).convert_alpha()
                
                # Créer la version zoomée pour la vue actuelle 
                self.current_room_image = pygame.transform.scale(original_image, (200, 200))
                self.current_room_image_rect = self.current_room_image.get_rect(center=self.current_room_panel_rect.center)
                
                # Créer l'icône pour la carte PROBLÉMATIQUE : cahnge la case qui a déjà été posée
                self.current_room_icon = pygame.transform.scale(original_image, (80, 80))
                self.current_room_icon_rect = self.current_room_icon.get_rect(midbottom=self.main_view_rect.midbottom)

            except pygame.error:
                print(f"ERREUR: Fichier image introuvable pour la salle '{room_name}' au chemin: {self.room_data[room_name]['path']}")
                # En cas d'erreur, on efface les images pour éviter de planter
                self.current_room_image = None
                self.current_room_icon = None
        else:
            print(f"ERREUR: La salle '{room_name}' n'existe pas dans room_data.")


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
        
        # On dessine le panneau de fond pour la salle actuelle
        pygame.draw.rect(self.display_surface, self.COLOR_BACKGROUND, self.current_room_panel_rect, border_radius=10)

        # On dessine les images de la salle si elles ont été chargées
        if self.current_room_image:
            self.display_surface.blit(self.current_room_image, self.current_room_image_rect)
        if self.current_room_icon:
            self.display_surface.blit(self.current_room_icon, self.current_room_icon_rect)

    def run(self):
        """Lance la boucle de jeu principale qui gère les événements et le dessin."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


                # --- EXEMPLE POUR TESTER ---
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.set_current_room('entrance_hall')
                    if event.key == pygame.K_2:
                        self.set_current_room('library')
            
            self.draw_background_grid()
            self.draw_elements()

            pygame.display.update()
            self.clock.tick(60)