import pygame

# 화면 크기 및 프레임
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 타일 크기
TILE_SIZE_DEFAULT = 24
TILE_SIZE_MIN = 8
TILE_SIZE_MAX = 64

# 색상
COLOR_WHITE = pygame.Color(255, 255, 255)
COLOR_BLACK = pygame.Color(0, 0, 0)
COLOR_GRAY = pygame.Color(128, 128, 128)
COLOR_DARK_GRAY = pygame.Color(50, 50, 50)
COLOR_LIGHT_GRAY = pygame.Color(192, 192, 192)
COLOR_REVEALED = pygame.Color(220, 220, 220)
COLOR_REVEALED_INNER = pygame.Color(235, 235, 235) # 내부 칸 색상
COLOR_GRID = pygame.Color(160, 160, 160)
COLOR_RED = pygame.Color(255, 50, 50)
COLOR_BLUE = pygame.Color(0, 0, 255)
COLOR_GREEN = pygame.Color(0, 128, 0)
COLOR_INCORRECT_FLAG = pygame.Color(255, 100, 100)

# 숫자 색상
NUMBER_COLORS = {
    1: pygame.Color(0, 0, 255),
    2: pygame.Color(0, 128, 0),
    3: pygame.Color(255, 0, 0),
    4: pygame.Color(0, 0, 128),
    5: pygame.Color(128, 0, 0),
    6: pygame.Color(0, 128, 128),
    7: pygame.Color(0, 0, 0),
    8: pygame.Color(128, 128, 128)
}

# UI
UI_PANEL_HEIGHT = 60
UI_FONT_SIZE = 32
INPUT_BOX_WIDTH = 140
INPUT_BOX_HEIGHT = 40
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
