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
