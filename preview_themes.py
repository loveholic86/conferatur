#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ttkbootstrap 테마 미리보기
사용 가능한 모든 테마를 확인할 수 있습니다
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def show_themes():
    """사용 가능한 모든 테마 보기"""
    print("=== ttkbootstrap 사용 가능한 테마 ===\n")

    themes = [
        'cosmo',      # 깔끔하고 현대적
        'flatly',     # 평면 디자인
        'litera',     # 읽기 좋은
        'minty',      # 파스텔 민트
        'lumen',      # 밝은 테마
        'sandstone',  # 따뜻한 느낌
        'yeti',       # 심플한 회색 계열
        'pulse',      # 보라색 계열
        'united',     # 주황색 계열
        'morph',      # 현대적인 그라데이션
        'journal',    # 신문 스타일
        'darkly',     # 다크 모드
        'superhero',  # 다크 파란색
        'solar',      # 다크 주황색
        'cyborg',     # 다크 회색
        'vapor',      # 다크 보라색
        'simplex',    # 심플한 빨간색
        'cerulean',   # 파란색 계열 (파스텔 블루와 유사)
    ]

    for i, theme in enumerate(themes, 1):
        print(f"{i:2d}. {theme:12s}", end="  ")
        if i % 3 == 0:
            print()
    print("\n")

    # 추천
    print("📌 추천 테마:")
    print("  - cerulean : 파스텔 블루 계열 (현재 디자인과 유사)")
    print("  - cosmo    : 깔끔하고 현대적")
    print("  - minty    : 파스텔 민트 계열")
    print("  - flatly   : 평면적이고 모던한 디자인")

if __name__ == '__main__':
    show_themes()

    # 간단한 미리보기 창
    print("\n미리보기 창을 띄웁니다...")
    print("여러 테마를 선택해서 확인해보세요.\n")

    # cerulean 테마로 미리보기
    root = ttk.Window(themename="cerulean")
    root.title("ttkbootstrap 미리보기 - cerulean 테마")
    root.geometry("600x400")

    # 샘플 위젯들
    ttk.Label(root, text="📂 파일/폴더 비교 도구", font=("Segoe UI", 16, "bold")).pack(pady=20)

    frame = ttk.LabelFrame(root, text="샘플 컨트롤", padding=20)
    frame.pack(fill='both', expand=True, padx=20, pady=10)

    ttk.Label(frame, text="이것이 cerulean 테마입니다").pack(pady=5)

    ttk.Button(frame, text="Primary 버튼", bootstyle="primary").pack(pady=5, fill='x')
    ttk.Button(frame, text="Success 버튼", bootstyle="success").pack(pady=5, fill='x')
    ttk.Button(frame, text="Info 버튼", bootstyle="info").pack(pady=5, fill='x')
    ttk.Button(frame, text="Warning 버튼", bootstyle="warning").pack(pady=5, fill='x')
    ttk.Button(frame, text="Danger 버튼", bootstyle="danger").pack(pady=5, fill='x')

    entry = ttk.Entry(frame)
    entry.pack(pady=5, fill='x')
    entry.insert(0, "텍스트 입력 필드")

    # 테마 변경 버튼
    def change_theme():
        themes = ['cerulean', 'cosmo', 'flatly', 'minty', 'litera', 'pulse', 'darkly']
        current = root.style.theme_use()
        current_idx = themes.index(current) if current in themes else 0
        next_theme = themes[(current_idx + 1) % len(themes)]
        root.style.theme_use(next_theme)
        root.title(f"ttkbootstrap 미리보기 - {next_theme} 테마")

    ttk.Button(root, text="🎨 다음 테마 보기", command=change_theme, bootstyle="info-outline").pack(pady=10)

    root.mainloop()
