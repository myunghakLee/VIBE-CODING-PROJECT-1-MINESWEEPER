import pygame
import sys
import os
import time

from constants import *
from board import BoardFinite, BoardInfinite
from renderer import Renderer
from ui import InputBox, Button, MessageBox

class Game:
    def __init__(self, asset_path):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = 'menu'  # 'menu', 'game'

        self.font_path = os.path.join(asset_path, 'assets', 'font', 'D2Coding.ttf')
        try:
            self.ui_font = pygame.font.Font(self.font_path, UI_FONT_SIZE)
        except FileNotFoundError:
            print(f"Warning: Font not found at {self.font_path}. Falling back to default font.")
            self.ui_font = pygame.font.Font(None, UI_FONT_SIZE)

        self.assets = self._load_assets(asset_path)
        self.renderer = Renderer(self.screen, self.ui_font, self.assets, self.font_path)
        
        self.game_state = {}
        self._init_menu()

    def _load_assets(self, asset_path):
        tile_size = TILE_SIZE_DEFAULT
        try:
            flag_img = pygame.image.load(os.path.join(asset_path, 'assets', 'images', 'flag.png')).convert_alpha()
            mine_img = pygame.image.load(os.path.join(asset_path, 'assets', 'images', 'mine.png')).convert_alpha()
            mine_bomb_img = pygame.image.load(os.path.join(asset_path, 'assets', 'images', 'mine_bomb.png')).convert_alpha()
        except FileNotFoundError:
            print("Warning: Image files not found. Using colored squares as placeholders.")
            flag_img = pygame.Surface((tile_size, tile_size))
            flag_img.fill(pygame.Color('yellow'))
            mine_img = pygame.Surface((tile_size, tile_size))
            mine_img.fill(pygame.Color('black'))
            mine_bomb_img = pygame.Surface((tile_size, tile_size))
            mine_bomb_img.fill(pygame.Color('red'))

        return {
            'flag_img': flag_img,
            'mine_img': mine_img,
            'mine_bomb_img': mine_bomb_img,
            'flag_img_scaled': pygame.transform.scale(flag_img, (tile_size, tile_size)),
            'mine_img_scaled': pygame.transform.scale(mine_img, (tile_size, tile_size)),
            'mine_bomb_img_scaled': pygame.transform.scale(mine_bomb_img, (tile_size, tile_size)),
        }
    
    def _update_scaled_assets(self):
        tile_size = self.renderer.tile_size
        self.assets['flag_img_scaled'] = pygame.transform.scale(self.assets['flag_img'], (tile_size, tile_size))
        self.assets['mine_img_scaled'] = pygame.transform.scale(self.assets['mine_img'], (tile_size, tile_size))
        self.assets['mine_bomb_img_scaled'] = pygame.transform.scale(self.assets['mine_bomb_img'], (tile_size, tile_size))


    def _init_menu(self):
        self.scene = 'menu'
        center_x = SCREEN_WIDTH / 2
        input_y = 250
        try:
            label_font = pygame.font.Font(self.font_path, 24)
        except FileNotFoundError:
            label_font = pygame.font.Font(None, 24)

        ui_elements = {
            'width_label': {
                'surface': label_font.render("Width:", True, COLOR_WHITE),
                'rect': pygame.Rect(center_x - 240, input_y, 80, 40)
            },
            'width_input': InputBox(center_x - 150, input_y, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, self.ui_font, "30"),
            'height_label': {
                'surface': label_font.render("Height:", True, COLOR_WHITE),
                'rect': pygame.Rect(center_x + 20, input_y, 90, 40)
            },
            'height_input': InputBox(center_x + 120, input_y, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, self.ui_font, "20"),
            'mines_label': {
                'surface': label_font.render("Mines:", True, COLOR_WHITE),
                'rect': pygame.Rect(center_x - 240, input_y + 70, 80, 40)
            },
            'mines_input': InputBox(center_x - 150, input_y + 70, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, self.ui_font, "100"),
            
            'start_button': Button(center_x - BUTTON_WIDTH - 10, 450, BUTTON_WIDTH, BUTTON_HEIGHT, self.ui_font, "Start Finite"),
            'infinite_button': Button(center_x + 10, 450, BUTTON_WIDTH, BUTTON_HEIGHT, self.ui_font, "Start Infinite"),
            'message_box': MessageBox(600, 250, label_font)
        }
        self.game_state = {'ui_elements': ui_elements}

    def _start_game(self, settings):
        self.scene = 'game'
        self.renderer.tile_size = TILE_SIZE_DEFAULT
        self.renderer.update_font_size()
        self._update_scaled_assets()
        
        is_infinite = settings.get('infinite', False)
        
        if is_infinite:
            board = BoardInfinite()
        else:
            solvable = settings.get('solvable', True)
            board = BoardFinite(settings['width'], settings['height'], settings['mines'], solvable)

        self.game_state = {
            'board': board,
            'timer': 0,
            'start_time': time.time(),
            'game_active': True,
            'is_infinite': is_infinite,
            'camera_offset': (0, 0),
            'dragging': False,
            'drag_start_pos': (0, 0),
            'reset_button': Button(SCREEN_WIDTH - 170, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 5, 150, 50, self.ui_font, "Reset/Menu"),
        }

    def _validate_and_start(self):
        ui = self.game_state['ui_elements']
        msg_box = ui['message_box']
        
        try:
            w = int(ui['width_input'].text)
            h = int(ui['height_input'].text)
            m = int(ui['mines_input'].text)
        except ValueError:
            msg_box.show("Width, Height, and Mines must be valid numbers.")
            return

        if not (10 <= w <= 200 and 10 <= h <= 200):
            msg_box.show("Width and Height must be between 10 and 200.")
            return
        
        max_mines = w * h - 9  # 9 = 3x3 safe zone for first click
        if not (0 <= m <= max_mines):
            msg_box.show(f"For this board size, Mines must be between 0 and {max_mines}\\n to guarantee a safe first click area.", True)
            self.game_state['pending_start_settings'] = {'width': w, 'height': h, 'mines': m, 'infinite': False}
            return

        # Mine density check for solvable board generation
        density = m / (w * h)
        if density > 0.25:
            msg_box.show("'No-Guess' generation is disabled for mine density > 25%.\nThe board may require guessing. Proceed?", True)
            self.game_state['pending_start_settings'] = {'width': w, 'height': h, 'mines': m, 'infinite': False, 'solvable': False}
            return

        self._start_game({'width': w, 'height': h, 'mines': m, 'infinite': False, 'solvable': True})

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.scene == 'menu':
                self._handle_menu_events(event)
            elif self.scene == 'game':
                self._handle_game_events(event)

    def _handle_menu_events(self, event):
        ui = self.game_state['ui_elements']
        msg_box = ui['message_box']

        if msg_box.active:
            result = msg_box.handle_event(event)
            if result == 'proceed' and 'pending_start_settings' in self.game_state:
                # User chose to proceed despite warning
                self._start_game(self.game_state.pop('pending_start_settings'))
            elif result == 'cancel':
                self.game_state.pop('pending_start_settings', None)
            return

        for key, element in ui.items():
            if isinstance(element, InputBox):
                element.handle_event(event)

        if ui['start_button'].is_clicked(event):
            self._validate_and_start()

        if ui['infinite_button'].is_clicked(event):
            self._start_game({'infinite': True})

    def _handle_game_events(self, event):
        board = self.game_state['board']

        if self.game_state['reset_button'].is_clicked(event):
            self._init_menu()
            return
            
        if not self.game_state['game_active']:
            return

        cam_x, cam_y = self.game_state['camera_offset']
        ts = self.renderer.tile_size
        
        # Mouse wheel for zoom
        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x_before_zoom = (cam_x + mouse_x) / ts
            world_y_before_zoom = (cam_y + mouse_y) / ts
            
            self.renderer.tile_size = max(TILE_SIZE_MIN, min(TILE_SIZE_MAX, ts + event.y))
            self.renderer.update_font_size()
            self._update_scaled_assets()
            ts = self.renderer.tile_size # update ts
            
            new_cam_x = world_x_before_zoom * ts - mouse_x
            new_cam_y = world_y_before_zoom * ts - mouse_y
            self.game_state['camera_offset'] = (int(new_cam_x), int(new_cam_y))


        if event.type == pygame.MOUSEBUTTONDOWN:
            # Ignore clicks on the UI panel
            if event.pos[1] > SCREEN_HEIGHT - UI_PANEL_HEIGHT:
                return
            
            world_x = (event.pos[0] + cam_x) // ts
            world_y = (event.pos[1] + cam_y) // ts

            if event.button == 1:  # Left click
                shift_pressed = pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]
                if shift_pressed:
                    board.chord(world_x, world_y)
                else:
                    board.reveal_cell(world_x, world_y)
            elif event.button == 3:  # Right click
                cell = board.get_cell(world_x, world_y)
                if cell and cell.is_revealed:
                    board.chord(world_x, world_y)
                else:
                    board.toggle_flag(world_x, world_y)
            elif event.button == 2:  # Middle click (drag)
                self.game_state['dragging'] = True
                self.game_state['drag_start_pos'] = event.pos
                self.game_state['drag_start_cam'] = self.game_state['camera_offset']
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                self.game_state['dragging'] = False

        if event.type == pygame.MOUSEMOTION and self.game_state.get('dragging', False):
            dx = event.pos[0] - self.game_state['drag_start_pos'][0]
            dy = event.pos[1] - self.game_state['drag_start_pos'][1]
            start_cam_x, start_cam_y = self.game_state['drag_start_cam']
            self.game_state['camera_offset'] = (start_cam_x - dx, start_cam_y - dy)
    
    def _update(self):
        if self.scene == 'game':
            board = self.game_state['board']
            
            # Camera movement with keys
            keys = pygame.key.get_pressed()
            cam_speed = 15
            cam_x, cam_y = self.game_state['camera_offset']
            if keys[pygame.K_w] or keys[pygame.K_UP]: cam_y -= cam_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: cam_y += cam_speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: cam_x -= cam_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: cam_x += cam_speed
            self.game_state['camera_offset'] = (cam_x, cam_y)

            if self.game_state['game_active']:
                if board.game_over:
                    self.game_state['game_active'] = False
                else:
                    self.game_state['timer'] = time.time() - self.game_state['start_time']
                
                # Update stats for UI
                self.game_state['revealed_count'] = board.revealed_count
                self.game_state['flag_count'] = board.flag_count
                if not self.game_state['is_infinite']:
                    self.game_state['mine_count'] = board.mine_count
                self.game_state['win'] = board.win
                self.game_state['game_over'] = board.game_over

    def _draw(self):
        game_draw_state = self.game_state
        if self.scene == 'game':
            game_draw_state = {
                'board': self.game_state['board'],
                'camera_offset': self.game_state['camera_offset'],
                'timer': self.game_state.get('timer', 0),
                'is_infinite': self.game_state.get('is_infinite', False),
                'revealed_count': self.game_state.get('revealed_count', 0),
                'flag_count': self.game_state.get('flag_count', 0),
                'mine_count': self.game_state.get('mine_count', 0),
                'game_over': self.game_state.get('game_over', False),
                'win': self.game_state.get('win', False),
                'reset_button': self.game_state['reset_button']
            }
        
        self.renderer.draw(self.scene, game_draw_state)
