# Conferatur - 파일/폴더 비교 도구 - Claude AI 가이드

> 이 문서는 Claude AI가 Conferatur 프로젝트를 이해하고 효과적으로 작업할 수 있도록 작성된 상세 가이드입니다.

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처 및 기술 스택](#아키텍처-및-기술-스택)
3. [코드베이스 구조](#코드베이스-구조)
4. [주요 클래스](#주요-클래스)
5. [핵심 기능](#핵심-기능)
6. [데이터 흐름](#데이터-흐름)
7. [UI 구조](#ui-구조)
8. [플랫폼별 고려사항](#플랫폼별-고려사항)
9. [설정 및 저장소](#설정-및-저장소)
10. [개발 가이드라인](#개발-가이드라인)
11. [주요 함수 레퍼런스](#주요-함수-레퍼런스)
12. [향후 개선 사항](#향후-개선-사항)

---

## 프로젝트 개요

**Conferatur**는 Python tkinter 기반의 크로스 플랫폼 파일/폴더 비교 도구입니다.

### 주요 특징
- **세 가지 비교 모드**: 폴더 비교, 텍스트 비교, 파일 비교
- **크로스 플랫폼**: macOS, Windows, Linux 완벽 지원
- **모던 UI**: ttkbootstrap minty 테마 적용
- **히스토리 및 즐겨찾기**: 작업 내역 자동 저장 및 북마크 기능
- **문자 단위 비교**: difflib 기반 정밀 차이점 분석
- **스크롤 동기화**: 양방향 스크롤 완벽 동기화

### 프로젝트 정보
- **파일 수**: 3개 (compare_tool.py, preview_themes.py, requirements.txt)
- **총 라인 수**: ~2,400 라인
- **메인 파일**: compare_tool.py (2,270 라인)
- **Python 버전**: 3.7+
- **라이선스**: MIT

---

## 아키텍처 및 기술 스택

### 아키텍처 패턴

#### MVC 기반 구조
```
Model (DataManager)
  ↓
Controller/View (CompareToolApp)
  ↓
Three Comparison Modes (Tabs)
```

#### 사용된 디자인 패턴
1. **Singleton-like Pattern**: DataManager (단일 인스턴스)
2. **Observer Pattern**: 텍스트 위젯 이벤트 바인딩
3. **Strategy Pattern**: 세 가지 비교 알고리즘 (MD5, Date, Both)
4. **Decorator Pattern**: 텍스트 태그 기반 하이라이팅

### 기술 스택

| 영역 | 기술 |
|------|------|
| **UI 프레임워크** | tkinter, ttkbootstrap |
| **테마** | ttkbootstrap minty |
| **비교 알고리즘** | difflib.SequenceMatcher |
| **해시 계산** | hashlib.md5 |
| **데이터 저장** | JSON (pathlib) |
| **파일 작업** | os, shutil, fnmatch |

---

## 코드베이스 구조

```
conferatur/
├── compare_tool.py          # 메인 애플리케이션 (2,270 라인)
│   ├── DataManager          # 데이터 관리 클래스 (라인 25-208)
│   └── CompareToolApp       # 메인 앱 클래스 (라인 211-2270)
├── preview_themes.py        # 테마 미리보기 도구 (121 라인)
├── requirements.txt         # 의존성 목록 (ttkbootstrap만 필요)
├── README.md               # 사용자 문서
└── ~/.conferatur/          # 설정 디렉토리 (런타임 생성)
    └── config.json         # 설정 및 히스토리 저장
```

### 파일별 책임

#### compare_tool.py
- **DataManager 클래스** (라인 25-208): 설정 및 데이터 관리
- **CompareToolApp 클래스** (라인 211-2270): UI 및 비즈니스 로직
  - 폴더 비교 탭 (라인 296-457)
  - 텍스트 비교 탭 (라인 459-530)
  - 파일 비교 탭 (라인 532-634)
  - 히스토리/즐겨찾기 관리 (라인 1726-2063)
  - 설정 관리 (라인 2065-2259)

#### preview_themes.py
- ttkbootstrap 테마 미리보기
- 테마 선택 가이드
- 독립 실행 가능

---

## 주요 클래스

### 1. DataManager 클래스

**위치**: compare_tool.py:25-208

**책임**:
- 설정 파일 관리 (~/.conferatur/config.json)
- 히스토리 관리 (각 카테고리당 최대 20개)
- 즐겨찾기 관리 (무제한)
- 폰트 설정 저장/로드
- 제외 패턴 관리

**주요 속성**:
```python
self.config_dir = Path.home() / '.conferatur'
self.config_file = self.config_dir / 'config.json'
self.max_history = 20
self.data = {
    'folder_history': [],      # 폴더 비교 히스토리
    'folder_favorites': [],    # 폴더 비교 즐겨찾기
    'text_history': [],        # 텍스트 비교 히스토리
    'text_favorites': [],      # 텍스트 비교 즐겨찾기
    'file_history': [],        # 파일 비교 히스토리
    'file_favorites': [],      # 파일 비교 즐겨찾기
    'font_family': 'Consolas', # 기본 폰트
    'font_size': 10,           # 기본 폰트 크기
    'exclude_patterns': []     # 제외 패턴
}
```

**핵심 메서드**:
- `load()`: config.json 로드
- `save()`: config.json 저장
- `add_folder_history(left, right, method)`: 폴더 비교 히스토리 추가
- `add_file_history(left, right)`: 파일 비교 히스토리 추가
- `add_text_history(left_text, right_text)`: 텍스트 비교 히스토리 추가
- `add_*_favorite(name, ...)`: 즐겨찾기 추가
- `delete_history(category, index)`: 히스토리 삭제
- `delete_favorite(category, index)`: 즐겨찾기 삭제
- `rename_favorite(category, index, new_name)`: 즐겨찾기 이름 변경
- `get_*_history()` / `get_*_favorites()`: 데이터 조회
- `get/set_font_settings()`: 폰트 설정 관리
- `get/set_exclude_patterns()`: 제외 패턴 관리

### 2. CompareToolApp 클래스

**위치**: compare_tool.py:211-2270

**책임**:
- 메인 윈도우 및 UI 생성
- 세 가지 비교 모드 탭 관리
- 파일/폴더 작업 (복사, 삭제, 비교)
- 텍스트 차이점 감지 및 하이라이팅
- 스크롤 동기화
- 플랫폼별 키보드/마우스 처리
- 히스토리/즐겨찾기 UI
- 설정 UI

**주요 속성**:
```python
# 플랫폼 감지
self.system = platform.system()
self.is_macos = (self.system == 'Darwin')
self.is_windows = (self.system == 'Windows')
self.is_linux = (self.system == 'Linux')

# 데이터 관리자
self.data_manager = DataManager()

# 폰트 설정
self.font_family = 'Consolas'
self.font_size = 10

# 차이점 블록 정보
self.file_diff_blocks = []   # 파일 비교 모드
self.text_diff_blocks = []   # 텍스트 비교 모드

# UI 컴포넌트
self.notebook               # 탭 컨테이너
self.folder_tree           # 폴더 비교 트리뷰
self.folder_preview_left   # 폴더 비교 미리보기 (왼쪽)
self.folder_preview_right  # 폴더 비교 미리보기 (오른쪽)
self.text_left            # 텍스트 비교 (왼쪽)
self.text_right           # 텍스트 비교 (오른쪽)
self.file_text_left       # 파일 비교 (왼쪽)
self.file_text_right      # 파일 비교 (오른쪽)
```

---

## 핵심 기능

### 1. 폴더 비교 (라인 1011-1284)

**세 가지 비교 방법**:

#### A. MD5 비교
```python
# compare_tool.py:947-956
def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
```
- 파일 내용의 MD5 해시 비교
- 4096 바이트 청크로 읽어 대용량 파일 처리
- 내용이 동일하면 파일명/날짜와 무관하게 "동일" 판정

#### B. 날짜 비교
```python
# compare_tool.py:958-968
def get_file_info(file_path):
    stat_info = os.stat(file_path)
    size = stat_info.st_size
    mtime = stat_info.st_mtime
    mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    return size, mtime_str, mtime
```
- 수정 시간 비교 (st_mtime)
- "왼쪽이 최신" / "오른쪽이 최신" 표시

#### C. MD5 + 날짜 (복합 비교)
- MD5로 내용 비교 후, 날짜도 함께 표시
- 가장 상세한 비교 방법

**상태 표시**:
- `"동일"`: 완전히 같음 (표시 안 함)
- `"내용 다름 (MD5)"`: MD5 해시 불일치
- `"왼쪽만 존재"`: 왼쪽 폴더에만 존재
- `"오른쪽만 존재"`: 오른쪽 폴더에만 존재
- `"왼쪽이 최신"`: 왼쪽 파일이 더 최근
- `"오른쪽이 최신"`: 오른쪽 파일이 더 최근

**제외 패턴** (라인 970-1009):
```python
def should_exclude(self, path, is_dir=False):
    """
    .gitignore 스타일 패턴 매칭
    - 폴더: 'node_modules/', '__pycache__/'
    - 파일: '*.pyc', '*.log'
    - 주석: '#'로 시작
    """
    patterns = self.data_manager.get_exclude_patterns()
    path_normalized = path.replace('\\', '/')

    for pattern in patterns:
        if is_dir and pattern.endswith('/'):
            if fnmatch.fnmatch(path_normalized + '/', pattern):
                return True
        elif fnmatch.fnmatch(path_normalized, pattern):
            return True
    return False
```

**파일 작업**:
- **복사** (라인 1166-1234): `shutil.copy2()` 사용, 폴더 자동 생성
- **삭제** (라인 1236-1284): 파일/폴더 재귀 삭제, 확인 대화상자

**트리 구조**:
- 계층적 폴더 표시
- 펼치기/접기 지원
- 열: 상태, 왼쪽 크기, 왼쪽 수정일, 오른쪽 크기, 오른쪽 수정일

### 2. 텍스트 비교 (라인 1448-1480)

**기능**:
- 직접 입력한 텍스트 비교
- 문자 단위 차이점 감지
- 양방향 적용 (왼쪽 → 오른쪽, 오른쪽 → 왼쪽)

**핵심 알고리즘** (라인 1377-1446):
```python
def compare_text_detailed(self, left_lines, right_lines):
    """
    difflib.SequenceMatcher 사용
    - 라인 단위 비교
    - 단일 라인 변경 시 문자 단위 비교
    - 연한 노란색 배경 + 빨간색 텍스트로 하이라이트
    """
    diff_blocks = []
    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # 문자 단위 비교
            if i2 - i1 == 1 and j2 - j1 == 1:
                # 단일 라인 변경: 문자 단위 비교
                char_matcher = difflib.SequenceMatcher(None,
                    left_lines[i1], right_lines[j1])
                # ...
        elif tag == 'delete':
            # 왼쪽에만 존재
        elif tag == 'insert':
            # 오른쪽에만 존재
```

### 3. 파일 비교 (라인 1510-1724)

**주요 기능**:
- 파일 내용 로드 및 비교
- 문자 단위 차이점 하이라이트
- 차이점 블록 단위 복사
- 전체 파일 덮어쓰기
- 수정 후 저장
- 재비교 (recompare)

**Diff 블록 구조**:
```python
{
    'tag': 'delete' | 'insert' | 'replace',
    'left_start': int,    # 시작 라인 (1-based)
    'left_end': int,      # 끝 라인
    'right_start': int,
    'right_end': int,
    'left_lines': [],     # 실제 텍스트 라인
    'right_lines': []
}
```

**차이점 블록 작업**:
- `find_diff_block_at_cursor()` (라인 1576-1602): 커서 위치의 diff 블록 찾기
- `copy_diff_to_left()` (라인 1635-1664): 오른쪽 → 왼쪽 블록 복사
- `copy_diff_to_right()` (라인 1604-1633): 왼쪽 → 오른쪽 블록 복사
- `copy_all_to_left()` (라인 1704-1723): 전체 덮어쓰기
- `copy_all_to_right()` (라인 1683-1702): 전체 덮어쓰기

### 4. 히스토리 및 즐겨찾기 (라인 1726-2063)

**히스토리**:
- 모든 비교 작업 자동 저장
- 최대 20개 (오래된 것 자동 삭제)
- 중복 제거 (같은 경로 조합은 타임스탬프 갱신)
- 카테고리별 관리 (folder, file, text)

**즐겨찾기**:
- 사용자가 이름을 지정하여 저장
- 개수 제한 없음
- 이름 변경 가능
- 삭제 가능

**관리 UI**:
- `show_history_manager()`: 히스토리 관리 창
- `show_favorite_manager()`: 즐겨찾기 관리 창
- `show_selection_window()`: 선택 및 로드 창
- `show_manager_window()`: 통합 관리 창

### 5. 폰트 설정 (라인 2065-2179)

**기능**:
- 폰트 패밀리 선택 (16가지 프리셋)
- 폰트 크기 조절 (8-20pt)
- 실시간 미리보기
- 모든 텍스트 위젯에 일괄 적용

**프리셋 폰트**:
```python
fonts = [
    'Consolas', 'Monaco', 'Courier New',
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono',
    'Ubuntu Mono', 'Courier', 'Lucida Console',
    'Andale Mono', 'SF Mono', 'JetBrains Mono',
    'Fira Code', 'Source Code Pro', 'Cascadia Code',
    'Roboto Mono'
]
```

### 6. 제외 패턴 (라인 2181-2259)

**기능**:
- .gitignore 스타일 패턴 편집
- 폴더 패턴 (`node_modules/`)
- 파일 패턴 (`*.pyc`)
- 주석 지원 (`#`)

**기본 패턴 제안**:
```
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
venv/

# Node.js
node_modules/
npm-debug.log

# 기타
.git/
.DS_Store
Thumbs.db
```

---

## 데이터 흐름

### 폴더 비교 플로우
```
1. 사용자 폴더 선택 (왼쪽, 오른쪽)
2. 비교 방법 선택 (MD5/Date/Both)
3. compare_folders() 실행
   ├─ os.walk()로 디렉토리 순회
   ├─ should_exclude()로 제외 패턴 필터링
   ├─ MD5/날짜 계산
   └─ 결과를 트리뷰에 표시
4. 파일 선택 시 on_folder_tree_select()
   ├─ 파일 내용 읽기 (UTF-8)
   ├─ compare_text_detailed()로 차이점 분석
   └─ 미리보기 패널에 하이라이트 표시
5. 히스토리 자동 저장 (add_folder_history)
```

### 파일 비교 플로우
```
1. 사용자 파일 선택 (왼쪽, 오른쪽)
2. compare_files() 실행
   ├─ 파일 읽기 (UTF-8)
   ├─ 라인 분할
   ├─ compare_text_detailed()로 분석
   └─ self.file_diff_blocks에 저장
3. 텍스트 위젯에 하이라이트 표시
4. 사용자 편집 가능
5. recompare_files()로 재분석
6. save_file()로 저장
7. 히스토리 자동 저장
```

### 설정 저장/로드 플로우
```
[애플리케이션 시작]
    ↓
DataManager.__init__()
    ↓
load() → config.json 읽기
    ↓
CompareToolApp에 설정 적용
    ↓
[사용자 작업]
    ↓
add_*_history() / add_*_favorite()
    ↓
save() → config.json 쓰기
    ↓
[애플리케이션 종료]
```

---

## UI 구조

### 탭 구조
```
Notebook (ttk.Notebook)
├─ Tab 1: 폴더 비교 (📁)
│   ├─ 컨트롤 영역
│   │   ├─ 히스토리/즐겨찾기 버튼
│   │   ├─ 폴더 선택 Entry + Browse 버튼
│   │   ├─ 비교 방법 라디오버튼 (MD5/Date/Both)
│   │   └─ 비교 시작/제외 패턴/초기화 버튼
│   ├─ 결과 영역
│   │   ├─ Treeview (파일 목록)
│   │   └─ 작업 버튼 (복사/삭제)
│   └─ 미리보기 영역
│       ├─ 왼쪽 ScrolledText (read-only)
│       └─ 오른쪽 ScrolledText (read-only)
│
├─ Tab 2: 텍스트 비교 (📝)
│   ├─ 컨트롤 영역
│   │   ├─ 히스토리/즐겨찾기 버튼
│   │   └─ 비교/적용/초기화 버튼
│   └─ 비교 영역
│       ├─ 왼쪽 ScrolledText (editable)
│       └─ 오른쪽 ScrolledText (editable)
│
└─ Tab 3: 파일 비교 (📄)
    ├─ 컨트롤 영역
    │   ├─ 히스토리/즐겨찾기 버튼
    │   ├─ 파일 선택 Entry + Browse 버튼
    │   └─ 비교/블록 복사/덮어쓰기/저장/초기화 버튼
    └─ 비교 영역
        ├─ 왼쪽 ScrolledText (editable)
        └─ 오른쪽 ScrolledText (editable)
```

### 메뉴바
```
MenuBar
├─ 히스토리
│   ├─ 폴더 비교 히스토리
│   ├─ 파일 비교 히스토리
│   └─ 텍스트 비교 히스토리
├─ 즐겨찾기
│   ├─ 폴더 비교 즐겨찾기
│   ├─ 파일 비교 즐겨찾기
│   └─ 텍스트 비교 즐겨찾기
└─ 설정
    └─ 폰트 설정
```

### 컨텍스트 메뉴

#### 1. 폴더 트리 컨텍스트 메뉴
```python
# 우클릭 시 표시
- 📤 왼쪽 → 오른쪽 복사
- 📥 오른쪽 → 왼쪽 복사
- ────────────────────
- 🗑️ 선택 항목 삭제
```

#### 2. 텍스트 위젯 컨텍스트 메뉴
```python
# 모든 텍스트 입력 영역
- 복사 (Cmd/Ctrl+C)
- 잘라내기 (Cmd/Ctrl+X)
- 붙여넣기 (Cmd/Ctrl+V)
- 전체 선택 (Cmd/Ctrl+A)
```

#### 3. 파일 비교 컨텍스트 메뉴
```python
# 파일 비교 텍스트 위젯 전용
- 복사 (Cmd/Ctrl+C)
- 잘라내기 (Cmd/Ctrl+X)
- 붙여넣기 (Cmd/Ctrl+V)
- 전체 선택 (Cmd/Ctrl+A)
- ────────────────────
- 📥 이 부분을 왼쪽으로 복사
- 📤 이 부분을 오른쪽으로 복사
```

### 스크롤 동기화 (라인 851-895)

**구현 방식**:
```python
def setup_scroll_sync(self, left_widget, right_widget):
    """
    양방향 스크롤 동기화
    - 마우스 휠 이벤트
    - Button-4/5 (Linux/Unix 스크롤)
    - 스크롤바 드래그
    """
    def on_mousewheel(event):
        # 양쪽 위젯 동시 스크롤
        left_widget.yview_scroll(delta, "units")
        right_widget.yview_scroll(delta, "units")
        return "break"

    # 이벤트 바인딩
    left_widget.bind("<MouseWheel>", on_mousewheel)
    right_widget.bind("<MouseWheel>", on_mousewheel)
    left_widget.bind("<Button-4>", on_mousewheel)  # Linux
    left_widget.bind("<Button-5>", on_mousewheel)
    # ...
```

---

## 플랫폼별 고려사항

### 운영체제 감지 (라인 215-235)
```python
import platform
self.system = platform.system()
self.is_macos = (self.system == 'Darwin')
self.is_windows = (self.system == 'Windows')
self.is_linux = (self.system == 'Linux')
```

### 키보드 단축키

| 작업 | macOS | Windows/Linux |
|------|-------|---------------|
| 복사 | Cmd+C | Ctrl+C |
| 잘라내기 | Cmd+X | Ctrl+X |
| 붙여넣기 | Cmd+V | Ctrl+V |
| 전체 선택 | Cmd+A | Ctrl+A |
| 대체 복사 | - | Ctrl+Insert |
| 대체 붙여넣기 | - | Shift+Insert |
| 대체 잘라내기 | - | Shift+Delete |

### macOS 특수 처리 (라인 695-727)
```python
def on_mac_key_event(event, action):
    """
    macOS Command 키 감지
    state & 0x0008 == Command 키
    """
    if event.state & 0x0008:  # Command key
        if action == 'copy':
            widget.event_generate('<<Copy>>')
        elif action == 'paste':
            widget.event_generate('<<Paste>>')
        # ...
        return "break"
```

**이유**: tkinter의 macOS Command 키 지원이 불완전하여 직접 구현

### 우클릭 이벤트 바인딩
```python
# Linux/Windows: Button-3 (표준 우클릭)
widget.bind('<Button-3>', show_context_menu)

# macOS: Button-2 (중간 클릭) 또는 Control+Button-1
widget.bind('<Button-2>', show_context_menu)
widget.bind('<Control-Button-1>', show_context_menu)
```

### 타이틀 바 OS 표시
```python
os_name = "macOS" if self.is_macos else (
    "Windows" if self.is_windows else "Linux"
)
self.root.title(f"📂 파일/폴더 비교 도구 [{os_name}]")
```

---

## 설정 및 저장소

### 설정 파일 위치
```
~/.conferatur/config.json
```
- **Linux/macOS**: `/home/username/.conferatur/config.json`
- **Windows**: `C:\Users\username\.conferatur\config.json`

### config.json 구조
```json
{
  "folder_history": [
    {
      "left": "/path/to/left",
      "right": "/path/to/right",
      "method": "md5",
      "timestamp": "2024-01-15 10:30:45"
    }
  ],
  "folder_favorites": [
    {
      "name": "프로젝트 A 백업",
      "left": "/home/user/project-a",
      "right": "/backup/project-a",
      "method": "both"
    }
  ],
  "text_history": [
    {
      "left_text": "전체 텍스트...",
      "right_text": "전체 텍스트...",
      "left_preview": "처음 200자...",
      "right_preview": "처음 200자...",
      "timestamp": "2024-01-15 11:00:00"
    }
  ],
  "text_favorites": [
    {
      "name": "템플릿 비교",
      "left_text": "...",
      "right_text": "...",
      "left_preview": "...",
      "right_preview": "..."
    }
  ],
  "file_history": [
    {
      "left": "/path/to/file1.py",
      "right": "/path/to/file2.py",
      "timestamp": "2024-01-15 12:00:00"
    }
  ],
  "file_favorites": [
    {
      "name": "설정 파일 비교",
      "left": "/etc/config.ini",
      "right": "/backup/config.ini"
    }
  ],
  "font_family": "Consolas",
  "font_size": 10,
  "exclude_patterns": [
    "node_modules/",
    "*.pyc",
    "__pycache__/",
    ".git/"
  ]
}
```

### 데이터 제약
- **히스토리 최대 개수**: 각 카테고리당 20개 (오래된 것 자동 삭제)
- **텍스트 미리보기**: 200자로 제한
- **중복 제거**: 같은 경로 조합은 타임스탬프만 갱신
- **인코딩**: UTF-8 (ensure_ascii=False)

---

## 개발 가이드라인

### 코드 스타일

#### 1. 명명 규칙
- **클래스**: PascalCase (`DataManager`, `CompareToolApp`)
- **함수/메서드**: snake_case (`compare_folders`, `add_to_favorite`)
- **상수**: UPPER_SNAKE_CASE (현재는 사용 안 함)
- **UI 컴포넌트**: self.{component_name} (`self.folder_tree`, `self.text_left`)

#### 2. 주석 스타일
```python
def function_name(param):
    """
    간단한 설명

    더 자세한 설명 (선택)
    """
    pass
```

#### 3. UI 컴포넌트 명명
```python
# 탭별 접두어
self.folder_*    # 폴더 비교 탭
self.text_*      # 텍스트 비교 탭
self.file_*      # 파일 비교 탭

# 위젯 종류별 접미어
*_var            # StringVar, IntVar 등
*_entry          # Entry 위젯
*_tree           # Treeview 위젯
*_text           # ScrolledText 위젯
*_frame          # Frame 컨테이너
```

### 새 기능 추가 시 체크리스트

#### 1. 새 비교 방법 추가
```
□ DataManager에 히스토리/즐겨찾기 키 추가
□ DataManager에 add/get 메서드 추가
□ CompareToolApp에 새 탭 추가
□ setup_*_tab() 메서드 구현
□ 비교 알고리즘 구현
□ 히스토리 자동 저장 추가
□ 메뉴바에 항목 추가
□ README.md 업데이트
```

#### 2. UI 위젯 추가
```
□ ttkbootstrap 스타일 사용 (bootstyle 파라미터)
□ 폰트 설정 적용 (self.font_family, self.font_size)
□ 테마 색상 사용 (#78C2AD 등)
□ 플랫폼별 이벤트 바인딩 확인
□ 스크롤 동기화 필요 시 setup_scroll_sync() 호출
```

#### 3. 파일 작업 추가
```
□ try-except로 에러 처리
□ UTF-8 인코딩 명시
□ 확인 대화상자 추가 (삭제/덮어쓰기 등)
□ 히스토리 자동 저장
□ 경로 정규화 (os.path.normpath)
```

### 테마 커스터마이징

**현재 테마**: ttkbootstrap minty

**주요 색상**:
- **Primary**: #78C2AD (민트/틸)
- **Success**: 녹색 계열
- **Danger**: 빨간색 계열
- **Info**: 파란색 계열
- **Warning**: 노란색 계열
- **Diff Highlight**: 배경 #fff9e6, 텍스트 #ff6b6b

**bootstyle 사용**:
```python
ttk.Button(..., bootstyle='primary')  # 민트색 버튼
ttk.Button(..., bootstyle='success')  # 녹색 버튼
ttk.Button(..., bootstyle='danger')   # 빨간색 버튼
ttk.Button(..., bootstyle='info')     # 파란색 버튼
ttk.Button(..., bootstyle='warning')  # 노란색 버튼
```

**테마 변경 방법**:
```python
# compare_tool.py의 main() 함수 (라인 2262-2270)
root = ttk.Window(themename='minty')  # 다른 테마로 변경
```

**사용 가능한 테마**:
- cosmo, flatly, litera, minty, lumen, sandstone, yeti
- pulse, united, morph, journal
- darkly, superhero, solar, cyborg, vapor (다크 모드)
- simplex, cerulean

---

## 주요 함수 레퍼런스

### 파일 작업

| 함수 | 위치 | 설명 |
|------|------|------|
| `calculate_md5(file_path)` | 947-956 | MD5 해시 계산 (4096 바이트 청크) |
| `get_file_info(file_path)` | 958-968 | 파일 크기, 수정일 추출 |
| `browse_folder(var, entry)` | 929-936 | 폴더 선택 대화상자 |
| `browse_file(var, entry)` | 938-945 | 파일 선택 대화상자 |
| `should_exclude(path, is_dir)` | 970-1009 | 제외 패턴 매칭 |

### 비교 알고리즘

| 함수 | 위치 | 설명 |
|------|------|------|
| `compare_folders()` | 1011-1164 | 폴더 비교 메인 로직 |
| `compare_files()` | 1510-1554 | 파일 내용 비교 |
| `compare_text()` | 1448-1467 | 텍스트 비교 |
| `compare_text_detailed(left, right)` | 1377-1446 | 라인/문자 단위 비교 (difflib) |
| `recompare_files()` | 1666-1681 | 편집 후 재비교 |

### UI 업데이트

| 함수 | 위치 | 설명 |
|------|------|------|
| `setup_folder_compare_tab()` | 296-457 | 폴더 비교 UI 초기화 |
| `setup_text_compare_tab()` | 459-530 | 텍스트 비교 UI 초기화 |
| `setup_file_compare_tab()` | 532-634 | 파일 비교 UI 초기화 |
| `on_folder_tree_select(event)` | 1304-1369 | 트리 선택 시 미리보기 로드 |
| `highlight_text_diff(widget, blocks, side)` | 1371-1375 | 차이점 하이라이트 |

### 파일 조작

| 함수 | 위치 | 설명 |
|------|------|------|
| `copy_file(direction)` | 1166-1234 | 파일 복사 (left_to_right / right_to_left) |
| `delete_selected()` | 1236-1284 | 선택 항목 삭제 |
| `save_file(side)` | 1556-1574 | 파일 저장 (left / right) |
| `apply_text(direction)` | 1469-1480 | 텍스트 적용 (to_left / to_right) |

### Diff 블록 작업

| 함수 | 위치 | 설명 |
|------|------|------|
| `find_diff_block_at_cursor(widget, side)` | 1576-1602 | 커서 위치의 diff 블록 찾기 |
| `copy_diff_to_left()` | 1635-1664 | 오른쪽 → 왼쪽 블록 복사 |
| `copy_diff_to_right()` | 1604-1633 | 왼쪽 → 오른쪽 블록 복사 |
| `copy_all_to_left()` | 1704-1723 | 전체 왼쪽으로 복사 |
| `copy_all_to_right()` | 1683-1702 | 전체 오른쪽으로 복사 |

### 히스토리/즐겨찾기

| 함수 | 위치 | 설명 |
|------|------|------|
| `load_from_history(category)` | 1726-1740 | 히스토리에서 불러오기 |
| `load_from_favorite(category)` | 1742-1756 | 즐겨찾기에서 불러오기 |
| `show_selection_window(...)` | 1758-1888 | 선택 창 표시 |
| `add_to_favorite(category)` | 1890-1918 | 즐겨찾기에 추가 |
| `show_history_manager(category)` | 1920-1932 | 히스토리 관리 창 |
| `show_favorite_manager(category)` | 1934-1946 | 즐겨찾기 관리 창 |
| `show_manager_window(...)` | 1948-2063 | 통합 관리 창 |

### 설정

| 함수 | 위치 | 설명 |
|------|------|------|
| `show_font_settings()` | 2065-2146 | 폰트 설정 대화상자 |
| `apply_fonts()` | 2148-2179 | 모든 위젯에 폰트 적용 |
| `open_exclude_patterns_dialog()` | 2181-2259 | 제외 패턴 편집 창 |

### 유틸리티

| 함수 | 위치 | 설명 |
|------|------|------|
| `setup_scroll_sync(left, right)` | 851-895 | 스크롤 동기화 설정 |
| `enable_clipboard_operations(widget)` | 637-757 | 클립보드 작업 활성화 |
| `enable_file_compare_context_menu(widget, side)` | 759-849 | 파일 비교 컨텍스트 메뉴 |
| `get_tree_item_path(item)` | 897-910 | 트리 아이템 → 전체 경로 |
| `get_all_files_from_tree_item(item)` | 912-927 | 트리 아이템의 모든 파일 가져오기 |

---

## 향후 개선 사항

### 1. 성능 최적화
- **대용량 파일 처리**: 메모리 맵핑 또는 스트리밍 비교
- **병렬 처리**: 멀티스레딩으로 MD5 계산 속도 향상
- **캐싱**: 이미 계산한 MD5 해시 캐싱
- **가상 스크롤**: 매우 긴 파일의 경우 가상 스크롤 적용

### 2. 기능 확장
- **3-way 병합**: Git 스타일 3-way 병합 지원
- **문법 강조**: Pygments를 사용한 코드 하이라이팅
- **이미지 비교**: 이미지 파일 시각적 비교
- **압축 파일 비교**: ZIP, TAR 등 압축 파일 내부 비교
- **네트워크 경로**: SMB, FTP 등 원격 경로 지원
- **Git 통합**: Git 저장소 커밋 간 비교

### 3. UI/UX 개선
- **다크 모드**: 다크 테마 지원
- **창 분할 조절**: Resizable PanedWindow
- **줄 번호**: 에디터에 줄 번호 표시
- **미니맵**: Sublime Text 스타일 미니맵
- **검색 기능**: 텍스트 검색 및 하이라이트
- **차이점 네비게이션**: 다음/이전 차이점 이동 버튼

### 4. 설정 및 커스터마이징
- **테마 선택**: UI에서 테마 변경 기능
- **단축키 커스터마이징**: 사용자 정의 키 바인딩
- **레이아웃 저장**: 창 크기/위치 저장
- **기본 설정**: 기본 비교 방법 등 설정

### 5. 품질 개선
- **단위 테스트**: pytest 기반 테스트 추가
- **에러 로깅**: logging 모듈 사용
- **국제화**: gettext를 사용한 다국어 지원
- **문서화**: Sphinx 기반 API 문서

### 6. 배포 개선
- **패키징**: PyInstaller로 실행 파일 생성
- **자동 업데이트**: 버전 체크 및 업데이트 기능
- **CI/CD**: GitHub Actions 자동 빌드
- **크로스 플랫폼 테스트**: 각 OS별 자동 테스트

---

## 트러블슈팅

### 일반적인 문제

#### 1. ttkbootstrap import 에러
```bash
# 해결 방법
pip install ttkbootstrap
# 또는
pip3 install ttkbootstrap
```

#### 2. tkinter 없음 (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/CentOS
sudo dnf install python3-tkinter
```

#### 3. macOS에서 키보드 단축키 작동 안 함
- **원인**: macOS의 tkinter Command 키 지원 제한
- **해결**: 이미 구현됨 (라인 695-727의 커스텀 핸들러)

#### 4. 파일 인코딩 에러
- **원인**: UTF-8이 아닌 파일
- **해결**: 에러 메시지 표시 (이미 구현됨)
- **향후**: 인코딩 자동 감지 (chardet 라이브러리)

#### 5. 대용량 폴더 비교 느림
- **원인**: 재귀 MD5 계산
- **해결**:
  - 제외 패턴 사용
  - 날짜 비교 사용
  - 향후: 병렬 처리 구현

---

## 코드 예제

### 새 비교 모드 추가 예제

```python
# 1. DataManager에 데이터 구조 추가 (compare_tool.py:37-47)
self.data = {
    # ...
    'my_mode_history': [],
    'my_mode_favorites': [],
}

# 2. DataManager에 메서드 추가 (compare_tool.py:70-187)
def add_my_mode_history(self, param1, param2):
    item = {
        'param1': param1,
        'param2': param2,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    self.data['my_mode_history'].insert(0, item)
    self.data['my_mode_history'] = self.data['my_mode_history'][:self.max_history]
    self.save()

def get_my_mode_history(self):
    return self.data['my_mode_history']

# 3. CompareToolApp에 탭 추가 (compare_tool.py:253-269)
self.my_mode_tab = ttk.Frame(self.notebook)
self.notebook.add(self.my_mode_tab, text=" 🔧 My Mode ")

# 4. 탭 초기화 메서드 추가
def setup_my_mode_tab(self):
    frame = self.my_mode_tab

    # 컨트롤 영역
    control_frame = ttk.Frame(frame)
    control_frame.pack(fill='x', padx=10, pady=10)

    # 히스토리/즐겨찾기 버튼
    ttk.Button(control_frame, text="📜 히스토리에서 불러오기",
              command=lambda: self.load_from_history('my_mode')).pack(side='left', padx=5)

    # ... 나머지 UI 구성

# 5. 비교 로직 구현
def compare_my_mode(self):
    # 비교 알고리즘 구현
    # ...

    # 히스토리 저장
    self.data_manager.add_my_mode_history(param1, param2)

# 6. 메뉴바에 추가 (compare_tool.py:272-294)
history_menu.add_command(label="My Mode 히스토리",
                        command=lambda: self.show_history_manager('my_mode'))
```

---

## 참고 자료

### 공식 문서
- [ttkbootstrap 문서](https://ttkbootstrap.readthedocs.io/)
- [tkinter 문서](https://docs.python.org/3/library/tkinter.html)
- [difflib 문서](https://docs.python.org/3/library/difflib.html)

### 관련 프로젝트
- [Meld](https://meldmerge.org/) - GTK 기반 비교 도구
- [WinMerge](https://winmerge.org/) - Windows 비교 도구
- [Beyond Compare](https://www.scootersoftware.com/) - 상용 비교 도구

---

## 마무리

이 문서는 Claude AI가 Conferatur 프로젝트를 효과적으로 이해하고 작업할 수 있도록 작성되었습니다.

**주요 포인트**:
1. **코드 구조**: 2개의 주요 클래스 (DataManager, CompareToolApp)
2. **비교 모드**: 3가지 (폴더, 텍스트, 파일)
3. **데이터 관리**: JSON 기반, 히스토리/즐겨찾기 지원
4. **크로스 플랫폼**: macOS, Windows, Linux 모두 지원
5. **확장성**: 새 기능 추가 용이한 구조

**코드 수정 시 주의사항**:
- DataManager는 항상 save() 호출
- UI 위젯은 ttkbootstrap 스타일 사용
- 파일 작업은 try-except로 감싸기
- 플랫폼별 이벤트 바인딩 확인
- 히스토리는 자동 저장되도록 구현

**질문이 있을 때**:
- README.md: 사용자 관점 문서
- claude.md (이 문서): 개발자/AI 관점 문서
- 코드 주석: 각 함수의 상세 설명

---

**문서 버전**: 1.0
**최종 수정**: 2024-11-18
**작성자**: Claude AI Analysis
