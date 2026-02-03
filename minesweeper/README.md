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

### 3) 실행 방법

1.  **가상 환경 생성 및 활성화 (권장)**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```

2.  **의존성 설치**
    필요한 라이브러리는 `pygame` 뿐입니다.
    ```bash
    pip install pygame
    ```

3.  **애셋 준비**
    -   위의 **프로젝트 폴더 구조**에 맞춰 `assets/font/`와 `assets/images/` 폴더를 만드세요.
    -   `assets/font/`에 `D2Coding.ttf` 또는 사용할 `.ttf` 폰트 파일을 넣으세요.
    -   `assets/images/`에 `flag.png`와 `mine.png` (권장 크기: 24x24 픽셀) 파일을 넣으세요.

4.  **게임 실행**
    프로젝트의 최상위 폴더(`minesweeper/`)에서 다음 명령어를 실행합니다.
    ```bash
    python src/main.py
    ```

---

### 4) Windows exe 빌드 방법

1.  **PyInstaller 설치**
    ```bash
    pip install pyinstaller
    ```

2.  **빌드 명령어 실행**
    프로젝트의 최상위 폴더(`minesweeper/`)에서 다음 명령어를 실행합니다. 이 명령어는 `assets` 폴더를 데이터로 포함하여 하나의 실행 파일을 만듭니다.

    ```bash
    pyinstaller --name Minesweeper --onefile --windowed --add-data "assets;assets" src/main.py
    ```
    -   `--name Minesweeper`: 생성될 exe 파일의 이름을 지정합니다.
    -   `--onefile`: 모든 파일을 하나의 `.exe` 파일로 묶습니다.
    -   `--windowed`: 실행 시 뒤에 콘솔 창이 뜨지 않도록 합니다.
    -   `--add-data "assets;assets"`: `assets` 폴더 전체를 빌드 결과물에 포함시킵니다. `(원본;대상)` 형식이며, Windows에서는 구분자로 `;`를 사용합니다.

3.  **결과물 확인**
    -   빌드가 성공적으로 완료되면 `dist` 폴더가 생성됩니다.
    -   `dist/Minesweeper.exe` 파일을 실행하면 게임이 시작됩니다.

4.  **흔한 문제 해결**
    -   **"file not found" 에러**: `.exe` 실행 시 폰트나 이미지를 찾을 수 없다는 에러가 발생하면, `--add-data` 경로가 올바른지, 빌드 명령어를 프로젝트 최상위 폴더에서 실행했는지 확인하세요. `sys._MEIPASS`를 이용한 경로 설정 코드가 `main.py`에 포함되어 있어 대부분의 경로 문제를 해결합니다.
    -   **백신 오진**: PyInstaller로 만든 `.exe` 파일은 일부 백신 프로그램에서 오진할 수 있습니다. 이는 알려진 이슈로, 신뢰하는 소스에서 직접 빌드했다면 안전합니다.

---

### 5) 체크리스트

| 요구사항 | 충족 여부 | 구현 위치/설명 |
| :--- | :--- | :--- |
| **0) 목표** | | |
| Windows 실행 가능 | O | `PyInstaller`를 이용한 `.exe` 빌드 방법 제공. |
| 마우스 클릭 기반 | O | `game.py`의 `_handle_game_events`에서 좌/우/가운데 클릭 및 Shift 조합 처리. |
| 사용자 입력 설정 | O | `game.py`의 `_init_menu`, `ui.py`의 `InputBox` 클래스를 통해 시작 메뉴에서 설정 가능. |
| 무한맵 모드 | O | `board.py`의 `BoardInfinite` 클래스에서 동적 청크 생성 방식으로 구현. |
| 운 강요 금지 설계 | O | `board.py`의 `BoardFinite.generate`, `BoardInfinite._ensure_chunk_generated`에서 구현. |
| **1) 기술 스택** | | |
| Python 3.11+ | O | 제공된 코드는 Python 3.11+와 호환됩니다. |
| Pygame | O | 게임 전체가 Pygame 라이브러리를 기반으로 제작되었습니다. |
| PyInstaller | O | `.exe` 빌드 방법 및 명령어 제공. |
| 산출물 제공 | O | 이 문서에 모든 산출물(구조, 코드, 방법, 체크리스트)이 포함되어 있습니다. |
| **2) 게임 규칙/UX** | | |
| 첫 클릭 안전/확장 | O | `BoardFinite.generate()`: 첫 클릭 후 3x3 안전 구역을 제외하고 지뢰를 배치. |
| 과도 지뢰 경고 | O | `game.py`의 `_validate_and_start()`: 지뢰 수 상한/추천선 초과 시 `MessageBox`로 경고. |
| 마우스 조작 | O | 좌클릭(열기), 우클릭(깃발), Shift+좌클릭(Chord) 모두 `_handle_game_events`에서 구현. |
| 타일 표시 규칙 | O | `renderer.py`의 `draw_board()`: 인접 지뢰 0인 칸(`COLOR_REVEALED_INNER`)과 숫자가 있는 칸(`COLOR_REVEALED`)을 다른 배경색으로 렌더링. |
| Chord 동작 | O | `board.py`의 `chord()` 메서드에서 구현. 열린 숫자칸에서 우클릭 또는 Shift+좌클릭으로 동작. |
| 보드 크기 설정 | O | 시작 메뉴의 `InputBox`를 통해 `width`, `height` 입력 가능. |
| 지뢰 수 설정/경고 | O | 시작 메뉴에서 `mines` 입력 가능하며 `_validate_and_start`에서 검증 및 경고. |
| **3) 무한맵 모드** | | |
| 초기 일부 개방 | O | `BoardInfinite.__init__()`: (0,0) 주변을 안전하게 생성하고 즉시 `reveal_cell(0,0)` 호출. |
| 동적 지뢰 생성 | O | `BoardInfinite._ensure_chunk_generated()`: 클릭 시점 주변 청크를 시드 기반으로 생성. |
| 클릭 지점 안전 | O | `_ensure_chunk_generated()`의 `safe_center` 인자를 통해 클릭 지점 및 주변 반경을 지뢰로부터 보호. |
| 무한 좌표계 관리 | O | `BoardInfinite`에서 `self.cells`를 딕셔너리로 사용하여 `(x,y)` 좌표로 셀 관리. |
| 카메라/스크롤/줌 | O | `game.py`의 `_handle_game_events`: 마우스 휠 드래그/줌, 키보드(WASD/방향키)로 카메라 이동. |
| **4) 게임 상태/기능** | | |
| 승리/패배 조건 | O | 유한: `BoardFinite.check_win_condition`. 무한: 점수(열린 칸 수) 표시. 패배는 `board.game_over`. |
| 타이머, 카운터 | O | `renderer.py`의 `draw_ui()`에서 타이머와 지뢰/스코어 카운터 렌더링. |
| 리셋 버튼 | O | UI 패널에 "Reset/Menu" 버튼을 추가하여 시작 메뉴로 돌아갈 수 있음. |
| 성능 (BFS, 렌더링) | O | `board.py`의 `reveal_cell()`에서 `collections.deque`를 사용한 BFS 구현. `renderer.py`의 `draw_board()`에서 화면에 보이는 영역만 렌더링. |
| **5) 구현 상세** | | |
| 클래스/모듈 설계 | O | `Game`, `Board`, `Renderer`, `UI` 등 제안된 구조에 따라 모듈화. |
| 데이터 모델 | O | `cell.py`의 `Cell` 클래스에 상태 정보(`is_mine`, `is_revealed` 등) 명시. |
| 입력 처리 | O | `game.py`의 이벤트 핸들러에서 마우스/키보드 입력과 Shift 조합을 처리. |
| 경고 메시지 | O | `ui.py`의 `MessageBox` 클래스를 통해 화면 중앙에 모달 형태의 경고창 표시. |

