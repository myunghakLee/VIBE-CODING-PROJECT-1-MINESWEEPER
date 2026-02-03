# Minesweeper (지뢰찾기)

Windows에서 실행 가능한 Pygame 기반 지뢰찾기 게임입니다. "운에 맡기는 상황 배제" 및 "무한맵" 모드를 지원합니다.

---

### 1) 요구사항 충족 설계 요약

#### "운 강요 금지" 설계 (유한맵)
- **첫 클릭 안전 보장**: 게임은 첫 클릭이 이루어지기 전까지 지뢰를 배치하지 않습니다.
- **초기 영역 확장 보장**: 사용자가 첫 번째 칸을 클릭(`(x, y)`)하면, 해당 칸과 그 주변 8칸(총 9칸의 3x3 영역)을 '안전 구역'으로 설정합니다. 지뢰는 이 안전 구역을 제외한 나머지 칸 중에서 무작위로 선택되어 배치됩니다.
- **결과**: 이 설계 덕분에 첫 클릭은 반드시 인접 지뢰 수가 0인 칸이 되며, 주변 8칸도 안전하므로 자동으로 넓은 영역이 열리게 됩니다. 이를 통해 사용자는 운에 의존하지 않고 논리적인 추론으로 게임을 시작할 수 있습니다.
- **과도한 지뢰 경고**: 사용자가 설정한 지뢰 수가 `(가로 * 세로 - 9)`를 초과하면, 안전 구역 보장이 불가능하므로 시작 메뉴에서 경고 메시지를 표시합니다. 추천 상한선(전체 칸의 30%) 초과 시에도 논리적 플레이가 어려울 수 있다는 경고를 표시합니다.

#### "무한맵" 생성 규칙
- **Lazy Generation (지연 생성)**: 맵 데이터는 사용자가 상호작용하는 지역을 중심으로 동적으로 생성됩니다. `dict` 자료구조를 사용해 `(x, y)` 좌표를 키로 셀 데이터를 저장하여 무한한 격자를 효율적으로 관리합니다.
- **안전 클릭 및 주변 생성**: 사용자가 아직 생성되지 않은 칸을 클릭하면, 그 주변의 일정 영역(Chunk)에 대한 셀 데이터를 생성합니다. 이때 클릭한 칸과 그 주변 반경(기본 1칸)은 지뢰가 생성되지 않도록 보장합니다.
- **일관성 있는 지뢰 배치**: 각 Chunk의 지뢰 배치는 해당 Chunk의 좌표를 `seed` 값으로 사용하는 무작위 생성기를 통해 이루어집니다. 이로 인해 사용자가 맵을 스크롤했다가 다시 돌아와도 동일한 지뢰 배치가 유지됩니다.
- **초기 상태**: 무한맵 모드 시작 시, (0,0)을 중심으로 한 초기 영역을 안전하게 생성하고 열어둔 상태로 시작하여 즉시 플레이가 가능합니다.
- **카메라**: 마우스 휠 드래그 또는 WASD/방향키로 맵을 이동하고, 마우스 휠 스크롤로 확대/축소가 가능하여 무한한 맵을 편리하게 탐색할 수 있습니다.

---

### 2) 프로젝트 폴더 구조

```
minesweeper/
├── assets/
│   ├── font/
│   │   └── D2Coding.ttf         # D2Coding 폰트 또는 다른 무료 폰트
│   └── images/
│       ├── flag.png             # 깃발 이미지 (24x24 px)
│       └── mine.png             # 지뢰 이미지 (24x24 px)
├── src/
│   ├── __init__.py
│   ├── board.py                 # BoardFinite, BoardInfinite 클래스
│   ├── cell.py                  # Cell 데이터 클래스
│   ├── constants.py             # 색상, 크기 등 상수
│   ├── game.py                  # 메인 Game 클래스 및 게임 루프
│   ├── main.py                  # 프로그램 진입점
│   ├── renderer.py              # 렌더링 담당 클래스
│   └── ui.py                    # UI 요소(버튼, 입력창, 메시지박스) 클래스
└── README.md
```

**참고**: `assets` 폴더와 그 안의 파일들은 직접 준비해야 합니다. `D2Coding.ttf`는 네이버에서 무료로 배포하는 코딩용 폰트이며, `flag.png`와 `mine.png`는 24x24 픽셀 크기의 간단한 아이콘 이미지를 사용하면 됩니다.

---

### 3) 전체 소스코드

**`src/main.py`**
```python
import os
import sys

# PyInstaller가 생성한 임시 폴더에서 실행될 때 asset 경로를 올바르게 찾도록 설정
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    # src 폴더에서 실행하므로 상위 폴더로 이동
    application_path = os.path.join(application_path, '..')

sys.path.append(os.path.join(application_path, 'src'))

from game import Game

def main():
    """게임 인스턴스를 생성하고 실행합니다."""
    game_instance = Game(application_path)
    game_instance.run()

if __name__ == '__main__':
    main()
```

**`src/constants.py`**
```python
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
```

**`src/cell.py`**
```python
class Cell:
    """게임 보드의 각 칸(셀)을 나타내는 클래스."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
        self.is_chunk_boundary = False # For infinite mode visualization

    def toggle_flag(self):
        """깃발 상태를 토글합니다."""
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged
            return True
        return False
```

**`src/ui.py`**
```python
import pygame
from constants import *

class InputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_GRAY
        self.text = text
        self.font = font
        self.txt_surface = self.font.render(text, True, COLOR_WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_LIGHT_GRAY if self.active else COLOR_GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = COLOR_GRAY
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isdigit():
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, COLOR_WHITE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Button:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

    def draw(self, screen, color=COLOR_GRAY):
        pygame.draw.rect(screen, color, self.rect)
        txt_surface = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = txt_surface.get_rect(center=self.rect.center)
        screen.blit(txt_surface, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class MessageBox:
    def __init__(self, w, h, font):
        self.rect = pygame.Rect((SCREEN_WIDTH - w) / 2, (SCREEN_HEIGHT - h) / 2, w, h)
        self.font = font
        self.message = ""
        self.active = False
        self.ok_button = Button(self.rect.centerx - 50, self.rect.bottom - 60, 100, 40, font, "OK")
        self.proceed_button = Button(self.rect.centerx - 110, self.rect.bottom - 60, 100, 40, font, "Proceed")
        self.cancel_button = Button(self.rect.centerx + 10, self.rect.bottom - 60, 100, 40, font, "Cancel")
        self.show_proceed_cancel = False

    def show(self, message, show_proceed_cancel=False):
        self.message = message
        self.active = True
        self.show_proceed_cancel = show_proceed_cancel

    def handle_event(self, event):
        if not self.active:
            return None
        if self.show_proceed_cancel:
            if self.proceed_button.is_clicked(event):
                self.active = False
                return "proceed"
            if self.cancel_button.is_clicked(event):
                self.active = False
                return "cancel"
        else:
            if self.ok_button.is_clicked(event):
                self.active = False
                return "ok"
        return None

    def draw(self, screen):
        if self.active:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, COLOR_DARK_GRAY, self.rect)
            pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2)
            
            lines = self.message.split('\n')
            y_offset = self.rect.top + 20
            for line in lines:
                txt_surface = self.font.render(line, True, COLOR_WHITE)
                text_rect = txt_surface.get_rect(center=(self.rect.centerx, y_offset))
                screen.blit(txt_surface, text_rect)
                y_offset += self.font.get_height() + 5

            if self.show_proceed_cancel:
                self.proceed_button.draw(screen, COLOR_GREEN)
                self.cancel_button.draw(screen, COLOR_RED)
            else:
                self.ok_button.draw(screen, COLOR_BLUE)
```

**`src/board.py`**
```python
import random
from collections import deque
from cell import Cell

class Board:
    """지뢰찾기 보드의 기본 동작을 정의하는 추상 클래스."""
    def __init__(self):
        self.game_over = False
        self.win = False

    def get_cell(self, x, y):
        raise NotImplementedError

    def get_neighbors(self, x, y):
        raise NotImplementedError

    def reveal_cell(self, x, y):
        raise NotImplementedError

    def toggle_flag(self, x, y):
        raise NotImplementedError

    def chord(self, x, y):
        raise NotImplementedError

class BoardFinite(Board):
    """유한 크기 보드 클래스."""
    def __init__(self, width, height, mine_count):
        super().__init__()
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.cells = [[Cell(x, y) for x in range(width)] for y in range(height)]
        self.is_generated = False
        self.revealed_count = 0
        self.flag_count = 0
        self.total_safe_cells = width * height - mine_count

    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None

    def get_neighbors(self, x, y):
        neighbors = []
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self.cells[ny][nx])
        return neighbors

    def generate(self, first_click_x, first_click_y):
        """첫 클릭 후 지뢰를 배치하고 인접 지뢰 수를 계산합니다."""
        safe_zone = set()
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                safe_zone.add((first_click_x + dx, first_click_y + dy))

        possible_mine_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in safe_zone:
                    possible_mine_positions.append((x, y))

        mine_positions = random.sample(possible_mine_positions, self.mine_count)

        for x, y in mine_positions:
            self.cells[y][x].is_mine = True

        for y in range(self.height):
            for x in range(self.width):
                if not self.cells[y][x].is_mine:
                    count = 0
                    for neighbor in self.get_neighbors(x, y):
                        if neighbor.is_mine:
                            count += 1
                    self.cells[y][x].adjacent_mines = count
        
        self.is_generated = True

    def reveal_cell(self, x, y):
        if not self.is_generated:
            self.generate(x, y)

        cell = self.get_cell(x, y)
        if not cell or cell.is_revealed or cell.is_flagged:
            return

        if cell.is_mine:
            self.game_over = True
            cell.is_revealed = True
            return

        q = deque([cell])
        visited = {cell}

        while q:
            current_cell = q.popleft()
            if not current_cell.is_revealed and not current_cell.is_flagged:
                current_cell.is_revealed = True
                self.revealed_count += 1

                if current_cell.adjacent_mines == 0:
                    for neighbor in self.get_neighbors(current_cell.x, current_cell.y):
                        if neighbor not in visited:
                            q.append(neighbor)
                            visited.add(neighbor)
        
        self.check_win_condition()

    def toggle_flag(self, x, y):
        cell = self.get_cell(x, y)
        if cell and cell.toggle_flag():
            if cell.is_flagged:
                self.flag_count += 1
            else:
                self.flag_count -= 1

    def chord(self, x, y):
        cell = self.get_cell(x, y)
        if not cell or not cell.is_revealed or cell.adjacent_mines == 0:
            return

        neighbors = self.get_neighbors(x, y)
        flagged_neighbors = sum(1 for n in neighbors if n.is_flagged)

        if flagged_neighbors == cell.adjacent_mines:
            for neighbor in neighbors:
                if not neighbor.is_flagged and not neighbor.is_revealed:
                    self.reveal_cell(neighbor.x, neighbor.y)
                    if self.game_over:
                        break

    def check_win_condition(self):
        if self.revealed_count == self.total_safe_cells:
            self.win = True
            self.game_over = True

class BoardInfinite(Board):
    """무한맵 보드 클래스."""
    CHUNK_SIZE = 16
    SAFE_RADIUS = 1

    def __init__(self, mine_density=0.15):
        super().__init__()
        self.mine_density = mine_density
        self.cells = {}
        self.generated_chunks = set()
        self.revealed_count = 0
        self.flag_count = 0
        # Start with an initial safe area
        self._ensure_chunk_generated(0, 0, is_initial=True)
        self.reveal_cell(0, 0)

    def _get_chunk_coord(self, x, y):
        return x // self.CHUNK_SIZE, y // self.CHUNK_SIZE

    def get_cell(self, x, y):
        return self.cells.get((x, y))

    def get_neighbors(self, x, y):
        neighbors = []
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                cell = self.get_cell(nx, ny)
                if cell:
                    neighbors.append(cell)
        return neighbors

    def _ensure_chunk_generated(self, x, y, safe_center=None, is_initial=False):
        chunk_x, chunk_y = self._get_chunk_coord(x, y)
        if (chunk_x, chunk_y) in self.generated_chunks:
            return

        # Generate this chunk
        self.generated_chunks.add((chunk_x, chunk_y))
        
        # Use chunk coordinates for a consistent seed
        seed = f"{chunk_x},{chunk_y}"
        rng = random.Random(seed)

        start_x = chunk_x * self.CHUNK_SIZE
        start_y = chunk_y * self.CHUNK_SIZE

        # Create cells and place mines
        for cy in range(start_y, start_y + self.CHUNK_SIZE):
            for cx in range(start_x, start_x + self.CHUNK_SIZE):
                if (cx, cy) not in self.cells:
                    self.cells[(cx, cy)] = Cell(cx, cy)
                
                # Check safe zone around the first click in this generation
                is_safe = False
                if safe_center:
                    if abs(cx - safe_center[0]) <= self.SAFE_RADIUS and abs(cy - safe_center[1]) <= self.SAFE_RADIUS:
                        is_safe = True
                if is_initial and abs(cx) <= 2 and abs(cy) <= 2: # Initial safe area
                     is_safe = True

                if not is_safe and rng.random() < self.mine_density:
                    self.cells[(cx, cy)].is_mine = True

        # Calculate adjacent mines for the new chunk and its borders
        for cy in range(start_y - 1, start_y + self.CHUNK_SIZE + 1):
            for cx in range(start_x - 1, start_x + self.CHUNK_SIZE + 1):
                if (cx, cy) in self.cells and not self.cells[(cx, cy)].is_mine:
                    count = 0
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0: continue
                            neighbor_pos = (cx + dx, cy + dy)
                            if self.cells.get(neighbor_pos, Cell(0,0)).is_mine:
                                count += 1
                    self.cells[(cx, cy)].adjacent_mines = count


    def reveal_cell(self, x, y):
        # Generate chunk if it doesn't exist
        if not self.get_cell(x,y):
            self._ensure_chunk_generated(x,y, safe_center=(x,y))
        
        # Ensure neighbors are generated for correct adjacency counts
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                self._ensure_chunk_generated(x + dx * self.CHUNK_SIZE, y + dy * self.CHUNK_SIZE)

        cell = self.get_cell(x, y)
        if not cell or cell.is_revealed or cell.is_flagged:
            return

        if cell.is_mine:
            self.game_over = True
            cell.is_revealed = True
            return

        q = deque([cell])
        visited = {cell}
        
        while q:
            current_cell = q.popleft()
            if not current_cell.is_revealed and not current_cell.is_flagged:
                current_cell.is_revealed = True
                self.revealed_count += 1

                if current_cell.adjacent_mines == 0:
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0: continue
                            nx, ny = current_cell.x + dx, current_cell.y + dy
                            
                            # Ensure neighbor chunk is generated before trying to access
                            if not self.get_cell(nx, ny):
                                self._ensure_chunk_generated(nx, ny)

                            neighbor = self.get_cell(nx, ny)
                            if neighbor and neighbor not in visited:
                                q.append(neighbor)
                                visited.add(neighbor)

    def toggle_flag(self, x, y):
        if not self.get_cell(x, y):
            self._ensure_chunk_generated(x, y)
        
        cell = self.get_cell(x, y)
        if cell and cell.toggle_flag():
            if cell.is_flagged:
                self.flag_count += 1
            else:
                self.flag_count -= 1

    def chord(self, x, y):
        cell = self.get_cell(x, y)
        if not cell or not cell.is_revealed or cell.adjacent_mines == 0:
            return

        # Generate surrounding chunks before checking neighbors
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                self._ensure_chunk_generated(x + dx * self.CHUNK_SIZE, y + dy * self.CHUNK_SIZE)

        neighbors = self.get_neighbors(x, y)
        flagged_neighbors = sum(1 for n in neighbors if n.is_flagged)

        if flagged_neighbors == cell.adjacent_mines:
            for neighbor in neighbors:
                if not neighbor.is_flagged and not neighbor.is_revealed:
                    self.reveal_cell(neighbor.x, neighbor.y)
                    if self.game_over:
                        break