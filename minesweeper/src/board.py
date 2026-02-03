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
