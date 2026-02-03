import pygame
from constants import *

class Renderer:
    """모든 그리기 작업을 처리하는 클래스."""
    def __init__(self, screen, font, assets):
        self.screen = screen
        self.font = font
        self.assets = assets
        self.tile_size = TILE_SIZE_DEFAULT
        self.number_font = pygame.font.Font(self.font.get_name(), self.tile_size - 4)

    def update_font_size(self):
        self.number_font = pygame.font.Font(self.font.get_name(), int(self.tile_size * 0.75))

    def draw_menu(self, ui_elements):
        self.screen.fill(COLOR_DARK_GRAY)
        title_font = pygame.font.Font(self.font.get_name(), 64)
        title_surf = title_font.render("Minesweeper", True, COLOR_WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 100))
        self.screen.blit(title_surf, title_rect)

        for key, element in ui_elements.items():
            if 'label' in key:
                 self.screen.blit(element['surface'], element['rect'])
            else:
                element.draw(self.screen)
    
    def draw_board(self, board, camera_offset=(0, 0)):
        start_x, start_y = camera_offset
        
        # 화면에 보일 셀의 범위를 계산
        view_start_col = int(start_x // self.tile_size)
        view_end_col = int((start_x + SCREEN_WIDTH) // self.tile_size) + 1
        view_start_row = int(start_y // self.tile_size)
        view_end_row = int((start_y + SCREEN_HEIGHT - UI_PANEL_HEIGHT) // self.tile_size) + 1

        cells_to_draw = []
        if hasattr(board, 'width'): # Finite board
            for y in range(view_start_row, view_end_row):
                for x in range(view_start_col, view_end_col):
                    if 0 <= x < board.width and 0 <= y < board.height:
                        cells_to_draw.append(board.cells[y][x])
        else: # Infinite board
            for y in range(view_start_row, view_end_row):
                for x in range(view_start_col, view_end_col):
                    cell = board.get_cell(x, y)
                    if cell:
                        cells_to_draw.append(cell)

        for cell in cells_to_draw:
            rect = pygame.Rect(
                cell.x * self.tile_size - start_x,
                cell.y * self.tile_size - start_y,
                self.tile_size,
                self.tile_size
            )
            
            # 화면 밖 셀은 그리지 않음
            if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.bottom < 0 or rect.top > SCREEN_HEIGHT - UI_PANEL_HEIGHT:
                continue

            if cell.is_revealed:
                if cell.is_mine:
                    pygame.draw.rect(self.screen, COLOR_RED, rect)
                    self.screen.blit(self.assets['mine_img_scaled'], rect.topleft)
                else:
                    # 인접 지뢰 0인 내부 칸과 숫자가 있는 경계 칸 색상 구분
                    is_inner = True
                    neighbors = board.get_neighbors(cell.x, cell.y)
                    if len(neighbors) < 8: # 맵 가장자리
                        is_inner = False
                    else:
                        for n in neighbors:
                             if not n.is_revealed:
                                is_inner = False
                                break
                    
                    # 더 간단한 규칙: adjacent_mines가 0이면 내부 스타일
                    if cell.adjacent_mines == 0:
                        pygame.draw.rect(self.screen, COLOR_REVEALED_INNER, rect)
                    else:
                        pygame.draw.rect(self.screen, COLOR_REVEALED, rect)

                    if cell.adjacent_mines > 0:
                        num_surf = self.number_font.render(str(cell.adjacent_mines), True, NUMBER_COLORS[cell.adjacent_mines])
                        num_rect = num_surf.get_rect(center=rect.center)
                        self.screen.blit(num_surf, num_rect)
            else:
                pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, rect)
                if cell.is_flagged:
                    self.screen.blit(self.assets['flag_img_scaled'], rect.topleft)

            pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_ui(self, game_state):
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - UI_PANEL_HEIGHT, SCREEN_WIDTH, UI_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, panel_rect)

        is_infinite = game_state['is_infinite']
        
        if is_infinite:
            # Score
            text = f"Score: {game_state['revealed_count']}"
        else:
             # Mine Counter
            text = f"Mines: {game_state['mine_count'] - game_state['flag_count']}"
        
        surf = self.font.render(text, True, COLOR_WHITE)
        self.screen.blit(surf, (20, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 15))

        # Timer
        time_text = f"Time: {int(game_state['timer'])}"
        time_surf = self.font.render(time_text, True, COLOR_WHITE)
        time_rect = time_surf.get_rect(centerx=SCREEN_WIDTH / 2)
        time_rect.y = SCREEN_HEIGHT - UI_PANEL_HEIGHT + 15
        self.screen.blit(time_surf, time_rect)

        # Reset Button
        game_state['reset_button'].draw(self.screen, COLOR_BLUE)
        
        # Game Over/Win message
        if game_state['game_over']:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - UI_PANEL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            msg = "You Win!" if game_state['win'] else "Game Over"
            msg_font = pygame.font.Font(self.font.get_name(), 72)
            msg_surf = msg_font.render(msg, True, COLOR_WHITE)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH / 2, (SCREEN_HEIGHT - UI_PANEL_HEIGHT) / 2))
            self.screen.blit(msg_surf, msg_rect)

    def draw(self, scene, game_state):
        self.screen.fill(COLOR_GRAY)
        if scene == 'menu':
            self.draw_menu(game_state['ui_elements'])
        elif scene == 'game':
            self.draw_board(game_state['board'], game_state['camera_offset'])
            self.draw_ui(game_state)
        
        if 'message_box' in game_state and game_state['message_box'].active:
            game_state['message_box'].draw(self.screen)

        pygame.display.flip()
