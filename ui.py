
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

        # initialisation du mixer pour les sons
        pygame.mixer.init()
        pygame.mixer.music.load('Sounds\\Mood\\29. Ovinn Nevarei.mp3') 
        pygame.mixer.music.set_volume(0.4) # volume 40%
        pygame.mixer.music.play(loops=-1) # boucle infinie
        
        self.new_room_sound = pygame.mixer.Sound('Sounds/Effects/door_opening.wav') 
        self.new_room_sound.set_volume(0.7)
        
        self.footsteps_sound = pygame.mixer.Sound('Sounds/Effects/footsteps.wav') 
        self.footsteps_sound.set_volume(0.7)

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

        # interface graphique pour le menu settings
        self.settings_font_small = pygame.font.SysFont('Arial', 20)
        self.settings_font_large = pygame.font.SysFont('Arial', 30, bold=True)

        self.COLOR_PANEL_SETTINGS = (10, 20, 40, 230) # panneau transparent
        self.COLOR_SLIDER_BG = (100, 100, 100) # fond des sliders
        self.COLOR_square = (200, 220, 255) # carré des sliders
        self.COLOR_CHECKBOX = (200, 220, 255) # contour des checkbox
        self.COLOR_CHECKBOX_FILLED = (100, 180, 255) # intérieur des checkbox cochées

        # Panneau principal
        panel_width, panel_height = 500, 400
        panel_x = (self.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.SCREEN_HEIGHT - panel_height) // 2
        self.settings_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        p = 40 # padding interne
        slider_w = 300 # largeur slider
        
        # Slider musique de fond
        self.music_slider_rect = pygame.Rect(panel_x + p + 120, panel_y + p + 50, slider_w, 20)
        self.music_square_rect = pygame.Rect(0, 0, 16, 30) # x peut varier
        
        # Slider effets sonores
        self.effects_slider_rect = pygame.Rect(panel_x + p + 120, panel_y + p + 120, slider_w, 20)
        self.effects_square_rect = pygame.Rect(0, 0, 16, 30) # x peut varier

        # Checkbox pour muter musique et effets sonores
        self.music_mute_rect = pygame.Rect(panel_x + p + 120, panel_y + p + 190, 25, 25)
        self.effects_mute_rect = pygame.Rect(panel_x + p + 120, panel_y + p + 260, 25, 25)



    def play_door_sound(self):
        if self.door_sound:
            self.door_sound.play()

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

        # gestion des sons
        sound_request = data.get('sound_to_play')
        
        if sound_request == 'new_room' and self.new_room_sound:
            self.new_room_sound.play()
        elif sound_request == 'footsteps' and self.footsteps_sound:
            self.footsteps_sound.play()
        
        music_vol = self.data.get('music_volume', 0.4)
        effects_vol = self.data.get('effects_volume', 0.7)
        
        if self.data.get('is_music_muted', False):
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(music_vol)
        
        final_effects_vol = 0 if self.data.get('is_effects_muted', False) else effects_vol
        
        if self.new_room_sound: self.new_room_sound.set_volume(final_effects_vol)
        if self.footsteps_sound: self.footsteps_sound.set_volume(final_effects_vol)

        # gestion des messages d'avertissement
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

    def draw_settings_menu(self, mouse_pos, mouse_pressed):
        inputs = [] 

        # Panneau settings principal avec transparence
        panel_surface = pygame.Surface(self.settings_panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill(self.COLOR_PANEL_SETTINGS)
        self.display_surface.blit(panel_surface, self.settings_panel_rect.topleft)
        pygame.draw.rect(self.display_surface, self.COLOR_PANEL_BORDER, self.settings_panel_rect, 4, border_radius=10)
        
        # Titre du menu
        title_text = self.settings_font_large.render("Settings", True, self.COLOR_TEXT)
        self.display_surface.blit(title_text, (self.settings_panel_rect.x + 40, self.settings_panel_rect.y + 20))

        # Titre musique de fond
        label_music = self.settings_font_small.render("Music", True, self.COLOR_TEXT)
        self.display_surface.blit(label_music, (self.settings_panel_rect.x + 40, self.music_slider_rect.y))
        
        # Barre du slider pour le volume musique de fond
        pygame.draw.rect(self.display_surface, self.COLOR_SLIDER_BG, self.music_slider_rect, border_radius=10)
        
        # Calculer la position du carré sur le slider
        music_vol = self.data.get('music_volume', 0.4)
        if self.data.get('is_music_muted', False): music_vol = 0
        
        square_x = self.music_slider_rect.x + int(music_vol * self.music_slider_rect.width)
        self.music_square_rect.center = (square_x, self.music_slider_rect.centery)
        pygame.draw.rect(self.display_surface, self.COLOR_square, self.music_square_rect, border_radius=5)
        
        # Logique de clic 
        if mouse_pressed and (self.music_slider_rect.collidepoint(mouse_pos) or self.music_square_rect.collidepoint(mouse_pos)):
            new_vol_percent = (mouse_pos[0] - self.music_slider_rect.x) / self.music_slider_rect.width
            new_vol = max(0.0, min(1.0, new_vol_percent)) # Borner entre 0 et 1
            inputs.append(("SET_MUSIC_VOLUME", round(new_vol, 2)))

        # Titre effets sonores
        label_effects = self.settings_font_small.render("Sound Effects", True, self.COLOR_TEXT)
        self.display_surface.blit(label_effects, (self.settings_panel_rect.x + 40, self.effects_slider_rect.y))
        # Barre du slider pour le volume des effets sonores
        pygame.draw.rect(self.display_surface, self.COLOR_SLIDER_BG, self.effects_slider_rect, border_radius=10)
        # Calculer la position du carré sur le slider
        effects_vol = self.data.get('effects_volume', 0.7)
        if self.data.get('is_effects_muted', False): effects_vol = 0

        square_x_effects = self.effects_slider_rect.x + int(effects_vol * self.effects_slider_rect.width)
        self.effects_square_rect.center = (square_x_effects, self.effects_slider_rect.centery)
        pygame.draw.rect(self.display_surface, self.COLOR_square, self.effects_square_rect, border_radius=5)
        
        # Logique de clic comme pour la musique
        if mouse_pressed and (self.effects_slider_rect.collidepoint(mouse_pos) or self.effects_square_rect.collidepoint(mouse_pos)):
            new_vol_percent = (mouse_pos[0] - self.effects_slider_rect.x) / self.effects_slider_rect.width
            new_vol = max(0.0, min(1.0, new_vol_percent))
            inputs.append(("SET_effects_VOLUME", round(new_vol, 2)))

        # Muter la musique ou les effets sonores
        label_mute_music = self.settings_font_small.render("Mute", True, self.COLOR_TEXT)
        self.display_surface.blit(label_mute_music, (self.music_mute_rect.x + 35, self.music_mute_rect.y))
        pygame.draw.rect(self.display_surface, self.COLOR_CHECKBOX, self.music_mute_rect, 2, border_radius=5)
        
        if self.data.get('is_music_muted', False):
            # inflate pour faire un carré plus petit à l'intérieur
            inner_rect = self.music_mute_rect.inflate(-8, -8)
            pygame.draw.rect(self.display_surface, self.COLOR_CHECKBOX_FILLED, inner_rect)

        # effets sonores muter
        label_mute_effects = self.settings_font_small.render("Mute", True, self.COLOR_TEXT)
        self.display_surface.blit(label_mute_effects, (self.effects_mute_rect.x + 35, self.effects_mute_rect.y))
        pygame.draw.rect(self.display_surface, self.COLOR_CHECKBOX, self.effects_mute_rect, 2, border_radius=5)
        
        if self.data.get('is_effects_muted', False):
            inner_rect = self.effects_mute_rect.inflate(-8, -8)
            pygame.draw.rect(self.display_surface, self.COLOR_CHECKBOX_FILLED, inner_rect)
        
        # Texte de fermeture
        close_text = self.settings_font_small.render("Press P to close", True, self.COLOR_TEXT)
        self.display_surface.blit(close_text, (self.settings_panel_rect.centerx - close_text.get_width() // 2, self.settings_panel_rect.bottom - 45))

        return inputs

    def run(self):  
        """Lance la boucle de jeu principale qui gère les événements et le dessin."""
        inputs = []
        
        # état de la souris
        mouse_pos = pygame.mouse.get_pos()
        # si clique gauche est appuyé
        mouse_pressed = pygame.mouse.get_pressed()[0] 
        
        game_state = self.data.get('game_state')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            
            # gestion clavier
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: 
                    inputs.append("TOGGLE_SETTINGS")
                if game_state in ["VICTORY", "GAME_OVER"]:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    # Si le jeu est fini, on n'écoute aucune autre touche
                    continue
                # Le jeu ne fonctionne que si on n'est pas dans le menu settings
                if game_state != "SETTINGS":
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
                    elif event.key == pygame.K_LEFT: 
                        inputs.append("LEFT_ROOM")
                    elif event.key == pygame.K_RIGHT: 
                        inputs.append("RIGHT_ROOM")
                    elif event.key == pygame.K_RETURN: 
                        inputs.append("ENTER")
            
            if game_state == "SETTINGS":
                # si on est dans le menu settings on gère les clics sur les checkbox
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # collidepoint pour voir si on a cliqué sur une checkbox
                    if self.music_mute_rect.collidepoint(event.pos):
                        inputs.append(("TOGGLE_MUSIC_MUTE", True))
                    elif self.effects_mute_rect.collidepoint(event.pos):
                        inputs.append(("TOGGLE_EFFECTS_MUTE", True))
            
        
        # elif current_game_state == "GAME_OVER":
            # self.draw_game_over_screen()
        self.draw_background_grid()
        self.draw_elements()
        self.display_MAP(self.data['mapping'])
        self.display_current_room(self.data['mapping'],self.data['position'])

        if game_state == "VICTORY":
                # si on gagne on dessine l'écran de victoire
                self.draw_victory_screen()
        if game_state == "DRAWING_ROOM":
            self.draw_room_choice_screen() 
        
        if game_state == "SETTINGS":
            settings_inputs = self.draw_settings_menu(mouse_pos, mouse_pressed)
            inputs.extend(settings_inputs)

        self.draw_warning_message()
        self.display_Player(self.data['position'],self.data['direction'])

        pygame.display.update()
        self.clock.tick(60)
        return inputs