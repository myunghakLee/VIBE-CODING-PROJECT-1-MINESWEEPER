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
