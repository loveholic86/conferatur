#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 및 폴더 비교 도구
세 가지 모드를 지원:
1. 폴더 비교 (MD5/날짜)
2. 텍스트 직접 비교
3. 파일 내용 비교
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import hashlib
import difflib
import shutil
import json
from datetime import datetime
from pathlib import Path


class DataManager:
    """히스토리 및 즐겨찾기 데이터 관리"""

    def __init__(self):
        self.config_dir = Path.home() / '.conferatur'
        self.config_file = self.config_dir / 'config.json'
        self.max_history = 20

        # 디렉토리 생성
        self.config_dir.mkdir(exist_ok=True)

        # 데이터 구조
        self.data = {
            'folder_history': [],
            'folder_favorites': [],
            'text_history': [],
            'text_favorites': [],
            'file_history': [],
            'file_favorites': []
        }

        self.load()

    def load(self):
        """설정 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # 기존 데이터와 병합 (새 키가 추가되었을 경우 대비)
                    self.data.update(loaded_data)
            except Exception as e:
                print(f"설정 파일 로드 실패: {e}")

    def save(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 파일 저장 실패: {e}")

    def add_folder_history(self, left, right, method):
        """폴더 비교 히스토리 추가"""
        item = {
            'left': left,
            'right': right,
            'method': method,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        # 중복 제거
        self.data['folder_history'] = [h for h in self.data['folder_history']
                                       if not (h['left'] == left and h['right'] == right)]
        self.data['folder_history'].insert(0, item)
        # 최대 개수 제한
        self.data['folder_history'] = self.data['folder_history'][:self.max_history]
        self.save()

    def add_file_history(self, left, right):
        """파일 비교 히스토리 추가"""
        item = {
            'left': left,
            'right': right,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        # 중복 제거
        self.data['file_history'] = [h for h in self.data['file_history']
                                     if not (h['left'] == left and h['right'] == right)]
        self.data['file_history'].insert(0, item)
        self.data['file_history'] = self.data['file_history'][:self.max_history]
        self.save()

    def add_text_history(self, left_text, right_text):
        """텍스트 비교 히스토리 추가"""
        # 텍스트는 너무 길 수 있으므로 앞부분만 저장
        preview_len = 200
        item = {
            'left_text': left_text,
            'right_text': right_text,
            'left_preview': left_text[:preview_len] + ('...' if len(left_text) > preview_len else ''),
            'right_preview': right_text[:preview_len] + ('...' if len(right_text) > preview_len else ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.data['text_history'].insert(0, item)
        self.data['text_history'] = self.data['text_history'][:self.max_history]
        self.save()

    def add_folder_favorite(self, name, left, right, method):
        """폴더 비교 즐겨찾기 추가"""
        item = {
            'name': name,
            'left': left,
            'right': right,
            'method': method
        }
        self.data['folder_favorites'].append(item)
        self.save()

    def add_file_favorite(self, name, left, right):
        """파일 비교 즐겨찾기 추가"""
        item = {
            'name': name,
            'left': left,
            'right': right
        }
        self.data['file_favorites'].append(item)
        self.save()

    def add_text_favorite(self, name, left_text, right_text):
        """텍스트 비교 즐겨찾기 추가"""
        preview_len = 200
        item = {
            'name': name,
            'left_text': left_text,
            'right_text': right_text,
            'left_preview': left_text[:preview_len] + ('...' if len(left_text) > preview_len else ''),
            'right_preview': right_text[:preview_len] + ('...' if len(right_text) > preview_len else '')
        }
        self.data['text_favorites'].append(item)
        self.save()

    def delete_history(self, category, index):
        """히스토리 삭제"""
        key = f"{category}_history"
        if 0 <= index < len(self.data[key]):
            self.data[key].pop(index)
            self.save()

    def delete_favorite(self, category, index):
        """즐겨찾기 삭제"""
        key = f"{category}_favorites"
        if 0 <= index < len(self.data[key]):
            self.data[key].pop(index)
            self.save()

    def rename_favorite(self, category, index, new_name):
        """즐겨찾기 이름 변경"""
        key = f"{category}_favorites"
        if 0 <= index < len(self.data[key]):
            self.data[key][index]['name'] = new_name
            self.save()

    def get_folder_history(self):
        return self.data['folder_history']

    def get_folder_favorites(self):
        return self.data['folder_favorites']

    def get_text_history(self):
        return self.data['text_history']

    def get_text_favorites(self):
        return self.data['text_favorites']

    def get_file_history(self):
        return self.data['file_history']

    def get_file_favorites(self):
        return self.data['file_favorites']


class CompareToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("파일/폴더 비교 도구")
        self.root.geometry("1200x800")

        # 데이터 매니저 초기화
        self.data_manager = DataManager()

        # 메뉴바 생성
        self.create_menubar()

        # 탭 생성
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 세 가지 모드 탭 생성
        self.folder_compare_tab = ttk.Frame(self.notebook)
        self.text_compare_tab = ttk.Frame(self.notebook)
        self.file_compare_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.folder_compare_tab, text="폴더 비교")
        self.notebook.add(self.text_compare_tab, text="텍스트 비교")
        self.notebook.add(self.file_compare_tab, text="파일 비교")

        # 각 탭 초기화
        self.setup_folder_compare_tab()
        self.setup_text_compare_tab()
        self.setup_file_compare_tab()

    def create_menubar(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 히스토리 메뉴
        history_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="히스토리", menu=history_menu)
        history_menu.add_command(label="폴더 비교 히스토리", command=lambda: self.show_history_manager('folder'))
        history_menu.add_command(label="파일 비교 히스토리", command=lambda: self.show_history_manager('file'))
        history_menu.add_command(label="텍스트 비교 히스토리", command=lambda: self.show_history_manager('text'))

        # 즐겨찾기 메뉴
        favorite_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="즐겨찾기", menu=favorite_menu)
        favorite_menu.add_command(label="폴더 비교 즐겨찾기", command=lambda: self.show_favorite_manager('folder'))
        favorite_menu.add_command(label="파일 비교 즐겨찾기", command=lambda: self.show_favorite_manager('file'))
        favorite_menu.add_command(label="텍스트 비교 즐겨찾기", command=lambda: self.show_favorite_manager('text'))

    def setup_folder_compare_tab(self):
        """첫 번째 모드: 폴더 비교"""
        frame = self.folder_compare_tab

        # 상단 컨트롤 영역
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 히스토리 및 즐겨찾기 버튼
        history_fav_frame = ttk.Frame(control_frame)
        history_fav_frame.grid(row=0, column=0, columnspan=3, sticky='w', pady=5)

        ttk.Button(history_fav_frame, text="📜 히스토리에서 불러오기",
                  command=lambda: self.load_from_history('folder')).pack(side='left', padx=5)
        ttk.Button(history_fav_frame, text="⭐ 즐겨찾기에서 불러오기",
                  command=lambda: self.load_from_favorite('folder')).pack(side='left', padx=5)
        ttk.Button(history_fav_frame, text="⭐ 즐겨찾기에 추가",
                  command=lambda: self.add_to_favorite('folder')).pack(side='left', padx=5)

        # 왼쪽 폴더 선택
        ttk.Label(control_frame, text="왼쪽 폴더:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.left_folder_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.left_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_folder(self.left_folder_var)).grid(row=1, column=2, padx=5, pady=5)

        # 오른쪽 폴더 선택
        ttk.Label(control_frame, text="오른쪽 폴더:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.right_folder_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.right_folder_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_folder(self.right_folder_var)).grid(row=2, column=2, padx=5, pady=5)

        # 비교 옵션
        option_frame = ttk.Frame(control_frame)
        option_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.compare_method_var = tk.StringVar(value="md5")
        ttk.Radiobutton(option_frame, text="MD5 비교", variable=self.compare_method_var, value="md5").pack(side='left', padx=10)
        ttk.Radiobutton(option_frame, text="날짜 비교", variable=self.compare_method_var, value="date").pack(side='left', padx=10)
        ttk.Radiobutton(option_frame, text="MD5 + 날짜", variable=self.compare_method_var, value="both").pack(side='left', padx=10)

        ttk.Button(option_frame, text="비교 시작", command=self.compare_folders).pack(side='left', padx=20)
        ttk.Button(option_frame, text="초기화", command=self.clear_folder_comparison).pack(side='left', padx=5)

        # 결과 영역
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 트리뷰 생성
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill='both', expand=True)

        # 스크롤바
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')

        # 트리뷰
        self.folder_tree = ttk.Treeview(tree_frame,
                                        columns=('상태', '왼쪽_크기', '왼쪽_수정일', '오른쪽_크기', '오른쪽_수정일'),
                                        yscrollcommand=tree_scroll_y.set,
                                        xscrollcommand=tree_scroll_x.set)
        self.folder_tree.pack(fill='both', expand=True)

        tree_scroll_y.config(command=self.folder_tree.yview)
        tree_scroll_x.config(command=self.folder_tree.xview)

        # 트리뷰 열 설정
        self.folder_tree.heading('#0', text='파일 경로')
        self.folder_tree.heading('상태', text='상태')
        self.folder_tree.heading('왼쪽_크기', text='왼쪽 크기')
        self.folder_tree.heading('왼쪽_수정일', text='왼쪽 수정일')
        self.folder_tree.heading('오른쪽_크기', text='오른쪽 크기')
        self.folder_tree.heading('오른쪽_수정일', text='오른쪽 수정일')

        self.folder_tree.column('#0', width=300)
        self.folder_tree.column('상태', width=100)
        self.folder_tree.column('왼쪽_크기', width=100)
        self.folder_tree.column('왼쪽_수정일', width=150)
        self.folder_tree.column('오른쪽_크기', width=100)
        self.folder_tree.column('오른쪽_수정일', width=150)

        # 트리뷰 선택 이벤트 바인딩
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_tree_select)

        # 버튼 영역
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="왼쪽 → 오른쪽 복사", command=lambda: self.copy_file('left_to_right')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="오른쪽 → 왼쪽 복사", command=lambda: self.copy_file('right_to_left')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="선택 항목 삭제", command=self.delete_selected).pack(side='left', padx=5)

        # 파일 내용 미리보기 영역
        preview_label = ttk.Label(result_frame, text="파일 내용 미리보기 (파일을 선택하세요)", font=('', 10, 'bold'))
        preview_label.pack(fill='x', pady=(10, 5))

        preview_frame = ttk.Frame(result_frame)
        preview_frame.pack(fill='both', expand=True, pady=5)

        # 왼쪽 파일 미리보기
        left_preview_frame = ttk.Frame(preview_frame)
        left_preview_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(left_preview_frame, text="왼쪽 파일", font=('', 9, 'bold')).pack()
        self.folder_preview_left = scrolledtext.ScrolledText(left_preview_frame, wrap='word', width=40, height=15, state='disabled')
        self.folder_preview_left.pack(fill='both', expand=True)

        # 오른쪽 파일 미리보기
        right_preview_frame = ttk.Frame(preview_frame)
        right_preview_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(right_preview_frame, text="오른쪽 파일", font=('', 9, 'bold')).pack()
        self.folder_preview_right = scrolledtext.ScrolledText(right_preview_frame, wrap='word', width=40, height=15, state='disabled')
        self.folder_preview_right.pack(fill='both', expand=True)

        # 차이점 표시를 위한 태그 설정
        self.folder_preview_left.tag_config('diff', background='#ffcccc')
        self.folder_preview_right.tag_config('diff', background='#ffcccc')

        # 스크롤 동기화
        self.setup_scroll_sync(self.folder_preview_left, self.folder_preview_right)

    def setup_text_compare_tab(self):
        """두 번째 모드: 텍스트 직접 비교"""
        frame = self.text_compare_tab

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 히스토리 및 즐겨찾기 버튼
        history_fav_frame = ttk.Frame(control_frame)
        history_fav_frame.pack(fill='x', pady=5)

        ttk.Button(history_fav_frame, text="📜 히스토리에서 불러오기",
                  command=lambda: self.load_from_history('text')).pack(side='left', padx=5)
        ttk.Button(history_fav_frame, text="⭐ 즐겨찾기에서 불러오기",
                  command=lambda: self.load_from_favorite('text')).pack(side='left', padx=5)
        ttk.Button(history_fav_frame, text="⭐ 즐겨찾기에 추가",
                  command=lambda: self.add_to_favorite('text')).pack(side='left', padx=5)

        # 비교 버튼
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="비교하기", command=self.compare_text).pack(side='left', padx=5)
        ttk.Button(button_frame, text="왼쪽으로 적용", command=lambda: self.apply_text('to_left')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="오른쪽으로 적용", command=lambda: self.apply_text('to_right')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="초기화", command=self.clear_text_comparison).pack(side='left', padx=5)

        # 텍스트 입력 영역
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 왼쪽 텍스트
        left_frame = ttk.Frame(text_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(left_frame, text="왼쪽 텍스트", font=('', 12, 'bold')).pack()
        self.text_left = scrolledtext.ScrolledText(left_frame, wrap='word', width=40, height=30)
        self.text_left.pack(fill='both', expand=True)

        # 오른쪽 텍스트
        right_frame = ttk.Frame(text_frame)
        right_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(right_frame, text="오른쪽 텍스트", font=('', 12, 'bold')).pack()
        self.text_right = scrolledtext.ScrolledText(right_frame, wrap='word', width=40, height=30)
        self.text_right.pack(fill='both', expand=True)

        # 복사/붙여넣기 바인딩 추가 (명시적으로 복사/붙여넣기 기능 활성화)
        def enable_copy_paste(widget):
            """복사/붙여넣기 기능 활성화"""
            # 붙여넣기
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-V>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Shift-Insert>', lambda e: widget.event_generate('<<Paste>>'))

            # 복사
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-C>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-Insert>', lambda e: widget.event_generate('<<Copy>>'))

            # 잘라내기
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-X>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Shift-Delete>', lambda e: widget.event_generate('<<Cut>>'))

            # 전체 선택
            widget.bind('<Control-a>', lambda e: widget.tag_add('sel', '1.0', 'end'))
            widget.bind('<Control-A>', lambda e: widget.tag_add('sel', '1.0', 'end'))

        enable_copy_paste(self.text_left)
        enable_copy_paste(self.text_right)

        # 차이점 표시를 위한 태그 설정
        self.text_left.tag_config('diff', background='#ffcccc')
        self.text_right.tag_config('diff', background='#ffcccc')

        # 스크롤 동기화
        self.setup_scroll_sync(self.text_left, self.text_right)

    def setup_file_compare_tab(self):
        """세 번째 모드: 파일 내용 비교"""
        frame = self.file_compare_tab

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 히스토리 및 즐겨찾기 버튼
        history_fav_frame = ttk.Frame(control_frame)
        history_fav_frame.grid(row=0, column=0, columnspan=3, sticky='w', pady=5)

        ttk.Button(history_fav_frame, text="📜 히스토리에서 불러오기",
                  command=lambda: self.load_from_history('file')).pack(side='left', padx=5)
        ttk.Button(history_fav_frame, text="⭐ 즐겨찾기에서 불러오기",
                  command=lambda: self.load_from_favorite('file')).pack(side='left', padx=5)
        ttk.Button(history_fav_frame, text="⭐ 즐겨찾기에 추가",
                  command=lambda: self.add_to_favorite('file')).pack(side='left', padx=5)

        # 왼쪽 파일 선택
        ttk.Label(control_frame, text="왼쪽 파일:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.file_left_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_left_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_file(self.file_left_var)).grid(row=1, column=2, padx=5, pady=5)

        # 오른쪽 파일 선택
        ttk.Label(control_frame, text="오른쪽 파일:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.file_right_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_right_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_file(self.file_right_var)).grid(row=2, column=2, padx=5, pady=5)

        # 버튼
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="비교하기", command=self.compare_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="왼쪽 파일 저장", command=lambda: self.save_file('left')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="오른쪽 파일 저장", command=lambda: self.save_file('right')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="초기화", command=self.clear_file_comparison).pack(side='left', padx=5)

        # 파일 내용 표시 영역
        file_text_frame = ttk.Frame(frame)
        file_text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 왼쪽 파일 내용
        left_file_frame = ttk.Frame(file_text_frame)
        left_file_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(left_file_frame, text="왼쪽 파일 내용", font=('', 12, 'bold')).pack()
        self.file_text_left = scrolledtext.ScrolledText(left_file_frame, wrap='word', width=40, height=30)
        self.file_text_left.pack(fill='both', expand=True)

        # 오른쪽 파일 내용
        right_file_frame = ttk.Frame(file_text_frame)
        right_file_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(right_file_frame, text="오른쪽 파일 내용", font=('', 12, 'bold')).pack()
        self.file_text_right = scrolledtext.ScrolledText(right_file_frame, wrap='word', width=40, height=30)
        self.file_text_right.pack(fill='both', expand=True)

        # 차이점 표시를 위한 태그 설정
        self.file_text_left.tag_config('diff', background='#ffcccc')
        self.file_text_right.tag_config('diff', background='#ffcccc')

        # 스크롤 동기화
        self.setup_scroll_sync(self.file_text_left, self.file_text_right)

    # 유틸리티 메서드
    def setup_scroll_sync(self, widget1, widget2):
        """두 텍스트 위젯의 스크롤 동기화"""
        def on_scroll(*args):
            """스크롤 이벤트 핸들러"""
            widget1.yview(*args)
            widget2.yview(*args)

        def on_mousewheel(event, widget_source):
            """마우스 휠 이벤트 핸들러"""
            # 양쪽 위젯 동시에 스크롤
            delta = -1 if event.delta > 0 else 1
            widget1.yview_scroll(delta, "units")
            widget2.yview_scroll(delta, "units")
            return "break"  # 이벤트 전파 방지

        # 각 위젯에 마우스 휠 이벤트 바인딩
        widget1.bind("<MouseWheel>", lambda e: on_mousewheel(e, widget1))
        widget2.bind("<MouseWheel>", lambda e: on_mousewheel(e, widget2))

        # 리눅스/맥용 마우스 휠 이벤트
        def scroll_up(event):
            widget1.yview_scroll(-1, "units")
            widget2.yview_scroll(-1, "units")
            return "break"

        def scroll_down(event):
            widget1.yview_scroll(1, "units")
            widget2.yview_scroll(1, "units")
            return "break"

        widget1.bind("<Button-4>", scroll_up)
        widget1.bind("<Button-5>", scroll_down)
        widget2.bind("<Button-4>", scroll_up)
        widget2.bind("<Button-5>", scroll_down)

        # 스크롤바 드래그 동기화
        # ScrolledText의 내부 스크롤바 command를 동기화 함수로 재설정
        def on_scrollbar(*args):
            """스크롤바 드래그 이벤트 핸들러"""
            widget1.yview(*args)
            widget2.yview(*args)

        # ScrolledText의 내부 스크롤바에 접근하여 command 재설정
        widget1.vbar.config(command=on_scrollbar)
        widget2.vbar.config(command=on_scrollbar)

    def get_tree_item_path(self, item):
        """트리 아이템의 전체 경로를 가져오기"""
        path_parts = []
        current = item

        while current:
            text = self.folder_tree.item(current, 'text')
            # 폴더 아이콘 제거
            if text.startswith("📁 "):
                text = text[2:]
            path_parts.insert(0, text)
            current = self.folder_tree.parent(current)

        return os.path.join(*path_parts) if path_parts else ""

    def browse_folder(self, var):
        """폴더 선택 대화상자"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    def browse_file(self, var):
        """파일 선택 대화상자"""
        file = filedialog.askopenfilename()
        if file:
            var.set(file)

    def calculate_md5(self, filepath):
        """파일의 MD5 해시 계산"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return None

    def get_file_info(self, filepath):
        """파일 정보 가져오기"""
        try:
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'mtime_raw': stat.st_mtime
            }
        except Exception as e:
            return None

    def compare_folders(self):
        """폴더 비교 실행"""
        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        if not left_folder or not right_folder:
            messagebox.showwarning("경고", "두 폴더를 모두 선택해주세요.")
            return

        if not os.path.exists(left_folder) or not os.path.exists(right_folder):
            messagebox.showerror("오류", "선택한 폴더가 존재하지 않습니다.")
            return

        # 히스토리에 추가
        self.data_manager.add_folder_history(left_folder, right_folder, self.compare_method_var.get())

        # 트리뷰 초기화
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        compare_method = self.compare_method_var.get()

        # 파일 목록 수집
        left_files = {}
        right_files = {}

        for root, dirs, files in os.walk(left_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, left_folder)
                left_files[rel_path] = full_path

        for root, dirs, files in os.walk(right_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, right_folder)
                right_files[rel_path] = full_path

        # 모든 파일 경로 합치기
        all_paths = set(left_files.keys()) | set(right_files.keys())

        # 트리 구조를 위한 딕셔너리 (폴더 경로 -> 트리 아이템 ID)
        folder_nodes = {}
        diff_count = 0

        for rel_path in sorted(all_paths):
            left_path = left_files.get(rel_path)
            right_path = right_files.get(rel_path)

            status = ""
            left_info = self.get_file_info(left_path) if left_path else None
            right_info = self.get_file_info(right_path) if right_path else None

            if not left_path:
                status = "오른쪽만 존재"
            elif not right_path:
                status = "왼쪽만 존재"
            else:
                # 비교 수행
                different = False

                if compare_method == "md5":
                    left_md5 = self.calculate_md5(left_path)
                    right_md5 = self.calculate_md5(right_path)
                    if left_md5 != right_md5:
                        different = True
                        status = "내용 다름 (MD5)"

                elif compare_method == "date":
                    if left_info and right_info:
                        if left_info['mtime_raw'] != right_info['mtime_raw']:
                            different = True
                            if left_info['mtime_raw'] > right_info['mtime_raw']:
                                status = "왼쪽이 최신"
                            else:
                                status = "오른쪽이 최신"

                elif compare_method == "both":
                    left_md5 = self.calculate_md5(left_path)
                    right_md5 = self.calculate_md5(right_path)
                    if left_md5 != right_md5:
                        different = True
                        status = "내용 다름 (MD5)"
                    elif left_info and right_info and left_info['mtime_raw'] != right_info['mtime_raw']:
                        different = True
                        if left_info['mtime_raw'] > right_info['mtime_raw']:
                            status = "내용 같음, 왼쪽이 최신"
                        else:
                            status = "내용 같음, 오른쪽이 최신"

                if not different and status == "":
                    status = "동일"

            # 차이가 있는 파일만 표시
            if status != "동일":
                diff_count += 1
                left_size = left_info['size'] if left_info else ""
                left_mtime = left_info['mtime'] if left_info else ""
                right_size = right_info['size'] if right_info else ""
                right_mtime = right_info['mtime'] if right_info else ""

                # 경로를 분리하여 트리 구조 생성
                path_parts = rel_path.split(os.sep)

                # 폴더가 있는 경우 폴더 노드 생성
                if len(path_parts) > 1:
                    parent_id = ''
                    cumulative_path = ''

                    # 폴더 경로 생성
                    for i, part in enumerate(path_parts[:-1]):
                        if cumulative_path:
                            cumulative_path = os.path.join(cumulative_path, part)
                        else:
                            cumulative_path = part

                        # 폴더 노드가 없으면 생성
                        if cumulative_path not in folder_nodes:
                            folder_nodes[cumulative_path] = self.folder_tree.insert(
                                parent_id, 'end', text=f"📁 {part}",
                                values=('', '', '', '', ''), open=True
                            )
                        parent_id = folder_nodes[cumulative_path]

                    # 파일을 폴더 노드 아래에 추가
                    file_name = path_parts[-1]
                    self.folder_tree.insert(parent_id, 'end', text=file_name,
                                            values=(status, left_size, left_mtime, right_size, right_mtime))
                else:
                    # 루트에 있는 파일
                    self.folder_tree.insert('', 'end', text=rel_path,
                                            values=(status, left_size, left_mtime, right_size, right_mtime))

        messagebox.showinfo("완료", f"비교가 완료되었습니다.\n차이가 있는 파일: {diff_count}개")

    def copy_file(self, direction):
        """파일 복사"""
        selected = self.folder_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "복사할 파일을 선택해주세요.")
            return

        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        copied_count = 0
        error_count = 0

        for item in selected:
            # 폴더 노드는 스킵
            item_values = self.folder_tree.item(item, 'values')
            if not item_values or not item_values[0]:  # 상태가 없으면 폴더
                continue

            rel_path = self.get_tree_item_path(item)
            left_path = os.path.join(left_folder, rel_path)
            right_path = os.path.join(right_folder, rel_path)

            try:
                if direction == 'left_to_right':
                    if os.path.exists(left_path):
                        os.makedirs(os.path.dirname(right_path), exist_ok=True)
                        shutil.copy2(left_path, right_path)
                        copied_count += 1
                elif direction == 'right_to_left':
                    if os.path.exists(right_path):
                        os.makedirs(os.path.dirname(left_path), exist_ok=True)
                        shutil.copy2(right_path, left_path)
                        copied_count += 1
            except Exception as e:
                error_count += 1
                messagebox.showerror("오류", f"파일 복사 실패: {rel_path}\n{str(e)}")

        if copied_count > 0:
            messagebox.showinfo("완료", f"{copied_count}개 파일이 복사되었습니다.")
            # 비교 다시 실행
            self.compare_folders()

    def delete_selected(self):
        """선택한 항목 삭제"""
        selected = self.folder_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 파일을 선택해주세요.")
            return

        # 파일만 카운트
        file_count = 0
        for item in selected:
            item_values = self.folder_tree.item(item, 'values')
            if item_values and item_values[0]:  # 상태가 있으면 파일
                file_count += 1

        if file_count == 0:
            messagebox.showwarning("경고", "삭제할 파일을 선택해주세요. (폴더는 선택할 수 없습니다)")
            return

        if not messagebox.askyesno("확인", f"{file_count}개 파일을 삭제하시겠습니까?"):
            return

        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        deleted_count = 0

        for item in selected:
            # 폴더 노드는 스킵
            item_values = self.folder_tree.item(item, 'values')
            if not item_values or not item_values[0]:  # 상태가 없으면 폴더
                continue

            rel_path = self.get_tree_item_path(item)
            left_path = os.path.join(left_folder, rel_path)
            right_path = os.path.join(right_folder, rel_path)

            try:
                if os.path.exists(left_path):
                    os.remove(left_path)
                    deleted_count += 1
                if os.path.exists(right_path):
                    os.remove(right_path)
                    deleted_count += 1
            except Exception as e:
                messagebox.showerror("오류", f"파일 삭제 실패: {rel_path}\n{str(e)}")

        if deleted_count > 0:
            messagebox.showinfo("완료", f"{deleted_count}개 파일이 삭제되었습니다.")
            self.compare_folders()

    def on_folder_tree_select(self, event):
        """폴더 트리뷰에서 파일 선택 시 미리보기 표시"""
        selected = self.folder_tree.selection()
        if not selected:
            return

        # 첫 번째 선택 항목만 처리
        item = selected[0]

        # 폴더 노드인 경우 미리보기 표시 안 함
        item_values = self.folder_tree.item(item, 'values')
        if not item_values or not item_values[0]:  # 상태가 없으면 폴더
            return

        rel_path = self.get_tree_item_path(item)

        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        if not left_folder or not right_folder:
            return

        left_path = os.path.join(left_folder, rel_path)
        right_path = os.path.join(right_folder, rel_path)

        # 미리보기 영역 초기화
        self.folder_preview_left.config(state='normal')
        self.folder_preview_right.config(state='normal')
        self.folder_preview_left.delete('1.0', 'end')
        self.folder_preview_right.delete('1.0', 'end')
        self.folder_preview_left.tag_remove('diff', '1.0', 'end')
        self.folder_preview_right.tag_remove('diff', '1.0', 'end')

        left_content = ""
        right_content = ""

        # 왼쪽 파일 읽기
        if os.path.exists(left_path) and os.path.isfile(left_path):
            try:
                with open(left_path, 'r', encoding='utf-8') as f:
                    left_content = f.read()
                self.folder_preview_left.insert('1.0', left_content)
            except Exception as e:
                self.folder_preview_left.insert('1.0', f"[파일을 읽을 수 없습니다]\n{str(e)}")
        else:
            self.folder_preview_left.insert('1.0', "[파일이 존재하지 않습니다]")

        # 오른쪽 파일 읽기
        if os.path.exists(right_path) and os.path.isfile(right_path):
            try:
                with open(right_path, 'r', encoding='utf-8') as f:
                    right_content = f.read()
                self.folder_preview_right.insert('1.0', right_content)
            except Exception as e:
                self.folder_preview_right.insert('1.0', f"[파일을 읽을 수 없습니다]\n{str(e)}")
        else:
            self.folder_preview_right.insert('1.0', "[파일이 존재하지 않습니다]")

        # 두 파일이 모두 존재하면 차이점 하이라이트
        if left_content and right_content:
            left_lines = left_content.splitlines()
            right_lines = right_content.splitlines()
            self.compare_text_detailed(self.folder_preview_left, self.folder_preview_right, left_lines, right_lines)

        self.folder_preview_left.config(state='disabled')
        self.folder_preview_right.config(state='disabled')

    def highlight_text_diff(self, text_widget, text, line_num, start_col, end_col):
        """텍스트 위젯의 특정 위치에 diff 태그 추가"""
        start_pos = f"{line_num}.{start_col}"
        end_pos = f"{line_num}.{end_col}"
        text_widget.tag_add('diff', start_pos, end_pos)

    def compare_text_detailed(self, left_widget, right_widget, left_lines, right_lines):
        """문자 단위로 상세 비교하여 하이라이트"""
        # 라인 단위 비교
        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
            elif tag == 'delete':
                # 왼쪽에만 있는 라인들
                for i in range(i1, i2):
                    self.highlight_text_diff(left_widget, left_lines[i], i+1, 0, len(left_lines[i]))
            elif tag == 'insert':
                # 오른쪽에만 있는 라인들
                for j in range(j1, j2):
                    self.highlight_text_diff(right_widget, right_lines[j], j+1, 0, len(right_lines[j]))
            elif tag == 'replace':
                # 변경된 라인들 - 문자 단위로 상세 비교
                left_block = left_lines[i1:i2]
                right_block = right_lines[j1:j2]

                # 단일 라인 대 단일 라인 비교인 경우 문자 단위 비교
                if len(left_block) == 1 and len(right_block) == 1:
                    left_line = left_block[0]
                    right_line = right_block[0]

                    # 문자 단위 비교
                    char_matcher = difflib.SequenceMatcher(None, left_line, right_line)

                    for char_tag, c_i1, c_i2, c_j1, c_j2 in char_matcher.get_opcodes():
                        if char_tag != 'equal':
                            # 왼쪽 차이 표시
                            if char_tag in ('replace', 'delete'):
                                self.highlight_text_diff(left_widget, left_line, i1+1, c_i1, c_i2)
                            # 오른쪽 차이 표시
                            if char_tag in ('replace', 'insert'):
                                self.highlight_text_diff(right_widget, right_line, j1+1, c_j1, c_j2)
                else:
                    # 여러 라인이 변경된 경우 라인 단위로 표시
                    for i in range(i1, i2):
                        self.highlight_text_diff(left_widget, left_lines[i], i+1, 0, len(left_lines[i]))
                    for j in range(j1, j2):
                        self.highlight_text_diff(right_widget, right_lines[j], j+1, 0, len(right_lines[j]))

    def compare_text(self):
        """텍스트 비교"""
        # 태그 제거
        self.text_left.tag_remove('diff', '1.0', 'end')
        self.text_right.tag_remove('diff', '1.0', 'end')

        left_text = self.text_left.get('1.0', 'end-1c')
        right_text = self.text_right.get('1.0', 'end-1c')

        # 히스토리에 추가
        if left_text or right_text:
            self.data_manager.add_text_history(left_text, right_text)

        left_lines = left_text.splitlines()
        right_lines = right_text.splitlines()

        # 상세 비교 (문자 단위)
        self.compare_text_detailed(self.text_left, self.text_right, left_lines, right_lines)

        messagebox.showinfo("완료", "텍스트 비교가 완료되었습니다.\n차이나는 부분이 연한 붉은색으로 표시됩니다.")

    def apply_text(self, direction):
        """텍스트 적용"""
        if direction == 'to_left':
            right_text = self.text_right.get('1.0', 'end-1c')
            self.text_left.delete('1.0', 'end')
            self.text_left.insert('1.0', right_text)
        elif direction == 'to_right':
            left_text = self.text_left.get('1.0', 'end-1c')
            self.text_right.delete('1.0', 'end')
            self.text_right.insert('1.0', left_text)

        messagebox.showinfo("완료", "텍스트가 적용되었습니다.")

    def clear_text_comparison(self):
        """텍스트 비교 초기화"""
        self.text_left.delete('1.0', 'end')
        self.text_right.delete('1.0', 'end')
        self.text_left.tag_remove('diff', '1.0', 'end')
        self.text_right.tag_remove('diff', '1.0', 'end')

    def clear_folder_comparison(self):
        """폴더 비교 초기화"""
        # 트리뷰 초기화
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        # 미리보기 영역 초기화
        self.folder_preview_left.config(state='normal')
        self.folder_preview_right.config(state='normal')
        self.folder_preview_left.delete('1.0', 'end')
        self.folder_preview_right.delete('1.0', 'end')
        self.folder_preview_left.config(state='disabled')
        self.folder_preview_right.config(state='disabled')

    def clear_file_comparison(self):
        """파일 비교 초기화"""
        self.file_text_left.delete('1.0', 'end')
        self.file_text_right.delete('1.0', 'end')
        self.file_text_left.tag_remove('diff', '1.0', 'end')
        self.file_text_right.tag_remove('diff', '1.0', 'end')

    def compare_files(self):
        """파일 내용 비교"""
        left_file = self.file_left_var.get()
        right_file = self.file_right_var.get()

        if not left_file or not right_file:
            messagebox.showwarning("경고", "두 파일을 모두 선택해주세요.")
            return

        if not os.path.exists(left_file) or not os.path.exists(right_file):
            messagebox.showerror("오류", "선택한 파일이 존재하지 않습니다.")
            return

        # 히스토리에 추가
        self.data_manager.add_file_history(left_file, right_file)

        try:
            # 파일 읽기
            with open(left_file, 'r', encoding='utf-8') as f:
                left_content = f.read()

            with open(right_file, 'r', encoding='utf-8') as f:
                right_content = f.read()

            # 텍스트 위젯에 표시
            self.file_text_left.delete('1.0', 'end')
            self.file_text_right.delete('1.0', 'end')
            self.file_text_left.insert('1.0', left_content)
            self.file_text_right.insert('1.0', right_content)

            # 태그 제거
            self.file_text_left.tag_remove('diff', '1.0', 'end')
            self.file_text_right.tag_remove('diff', '1.0', 'end')

            # 차이점 하이라이트 (문자 단위 상세 비교)
            left_lines = left_content.splitlines()
            right_lines = right_content.splitlines()

            self.compare_text_detailed(self.file_text_left, self.file_text_right, left_lines, right_lines)

            messagebox.showinfo("완료", "파일 비교가 완료되었습니다.\n차이나는 부분이 연한 붉은색으로 표시됩니다.")

        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{str(e)}")

    def save_file(self, side):
        """파일 저장"""
        if side == 'left':
            filepath = self.file_left_var.get()
            content = self.file_text_left.get('1.0', 'end-1c')
        else:
            filepath = self.file_right_var.get()
            content = self.file_text_right.get('1.0', 'end-1c')

        if not filepath:
            messagebox.showwarning("경고", "저장할 파일을 선택해주세요.")
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("완료", "파일이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 실패:\n{str(e)}")

    # 히스토리 및 즐겨찾기 관련 메서드
    def load_from_history(self, category):
        """히스토리에서 불러오기"""
        if category == 'folder':
            history = self.data_manager.get_folder_history()
        elif category == 'file':
            history = self.data_manager.get_file_history()
        else:
            history = self.data_manager.get_text_history()

        if not history:
            messagebox.showinfo("알림", "히스토리가 비어있습니다.")
            return

        # 선택 창 열기
        self.show_selection_window(category, 'history', history)

    def load_from_favorite(self, category):
        """즐겨찾기에서 불러오기"""
        if category == 'folder':
            favorites = self.data_manager.get_folder_favorites()
        elif category == 'file':
            favorites = self.data_manager.get_file_favorites()
        else:
            favorites = self.data_manager.get_text_favorites()

        if not favorites:
            messagebox.showinfo("알림", "즐겨찾기가 비어있습니다.")
            return

        # 선택 창 열기
        self.show_selection_window(category, 'favorite', favorites)

    def show_selection_window(self, category, data_type, items):
        """선택 창 표시"""
        win = tk.Toplevel(self.root)
        win.title(f"{'히스토리' if data_type == 'history' else '즐겨찾기'} 선택")
        win.geometry("900x500")

        # 상단 정보 레이블
        info_frame = ttk.Frame(win)
        info_frame.pack(fill='x', padx=10, pady=(10, 5))

        info_text = f"{'히스토리' if data_type == 'history' else '즐겨찾기'} 목록 (총 {len(items)}개)"
        ttk.Label(info_frame, text=info_text, font=('', 11, 'bold')).pack(anchor='w')

        # 리스트박스
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set,
                            font=('Consolas', 11), height=15,
                            selectmode='single', activestyle='dotbox')
        listbox.pack(fill='both', expand=True)
        scrollbar.config(command=listbox.yview)

        def refresh_list():
            """목록 새로고침"""
            listbox.delete(0, 'end')
            # 현재 데이터 다시 가져오기
            if category == 'folder':
                current_items = self.data_manager.get_folder_history() if data_type == 'history' else self.data_manager.get_folder_favorites()
            elif category == 'file':
                current_items = self.data_manager.get_file_history() if data_type == 'history' else self.data_manager.get_file_favorites()
            else:
                current_items = self.data_manager.get_text_history() if data_type == 'history' else self.data_manager.get_text_favorites()

            # 항목 추가
            for idx, item in enumerate(current_items):
                if category == 'folder':
                    if data_type == 'favorite':
                        display = f"⭐ {item['name']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                    else:
                        display = f"📅 {item['timestamp']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                elif category == 'file':
                    if data_type == 'favorite':
                        display = f"⭐ {item['name']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                    else:
                        display = f"📅 {item['timestamp']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                else:  # text
                    if data_type == 'favorite':
                        display = f"⭐ {item['name']}\n   왼쪽: {item['left_preview']}\n   오른쪽: {item['right_preview']}"
                    else:
                        display = f"📅 {item['timestamp']}\n   왼쪽: {item['left_preview']}\n   오른쪽: {item['right_preview']}"
                listbox.insert('end', display)
                # 구분선 추가
                if idx < len(current_items) - 1:
                    listbox.insert('end', '─' * 80)

            # 정보 레이블 업데이트
            info_text = f"{'히스토리' if data_type == 'history' else '즐겨찾기'} 목록 (총 {len(current_items)}개)"
            for widget in info_frame.winfo_children():
                widget.destroy()
            ttk.Label(info_frame, text=info_text, font=('', 11, 'bold')).pack(anchor='w')

            return current_items

        current_items = refresh_list()

        # 버튼
        button_frame = ttk.Frame(win)
        button_frame.pack(fill='x', padx=10, pady=10)

        def load_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "항목을 선택해주세요.")
                return

            # 구분선 제외 (홀수 인덱스는 구분선)
            index = selection[0]
            if index % 2 == 1:  # 구분선 선택
                messagebox.showwarning("경고", "항목을 선택해주세요. (구분선이 아닌 항목을 선택하세요)")
                return

            actual_index = index // 2
            item = current_items[actual_index]

            if category == 'folder':
                self.left_folder_var.set(item['left'])
                self.right_folder_var.set(item['right'])
                if 'method' in item:
                    self.compare_method_var.set(item['method'])
            elif category == 'file':
                self.file_left_var.set(item['left'])
                self.file_right_var.set(item['right'])
            else:  # text
                self.text_left.delete('1.0', 'end')
                self.text_right.delete('1.0', 'end')
                self.text_left.insert('1.0', item['left_text'])
                self.text_right.insert('1.0', item['right_text'])

            win.destroy()
            messagebox.showinfo("완료", "불러오기 완료!")

        def delete_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "삭제할 항목을 선택해주세요.")
                return

            # 구분선 제외
            index = selection[0]
            if index % 2 == 1:  # 구분선 선택
                messagebox.showwarning("경고", "항목을 선택해주세요. (구분선이 아닌 항목을 선택하세요)")
                return

            actual_index = index // 2

            if messagebox.askyesno("확인", "선택한 항목을 삭제하시겠습니까?"):
                if data_type == 'history':
                    self.data_manager.delete_history(category, actual_index)
                else:
                    self.data_manager.delete_favorite(category, actual_index)

                nonlocal current_items
                current_items = refresh_list()

        ttk.Button(button_frame, text="불러오기", command=load_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="삭제", command=delete_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="취소", command=win.destroy).pack(side='left', padx=5)

    def add_to_favorite(self, category):
        """즐겨찾기에 추가"""
        name = simpledialog.askstring("즐겨찾기 추가", "즐겨찾기 이름을 입력하세요:")
        if not name:
            return

        if category == 'folder':
            left = self.left_folder_var.get()
            right = self.right_folder_var.get()
            if not left or not right:
                messagebox.showwarning("경고", "폴더를 선택해주세요.")
                return
            self.data_manager.add_folder_favorite(name, left, right, self.compare_method_var.get())
        elif category == 'file':
            left = self.file_left_var.get()
            right = self.file_right_var.get()
            if not left or not right:
                messagebox.showwarning("경고", "파일을 선택해주세요.")
                return
            self.data_manager.add_file_favorite(name, left, right)
        else:  # text
            left_text = self.text_left.get('1.0', 'end-1c')
            right_text = self.text_right.get('1.0', 'end-1c')
            if not left_text and not right_text:
                messagebox.showwarning("경고", "텍스트를 입력해주세요.")
                return
            self.data_manager.add_text_favorite(name, left_text, right_text)

        messagebox.showinfo("완료", "즐겨찾기에 추가되었습니다.")

    def show_history_manager(self, category):
        """히스토리 관리 창"""
        if category == 'folder':
            items = self.data_manager.get_folder_history()
            title = "폴더 비교 히스토리"
        elif category == 'file':
            items = self.data_manager.get_file_history()
            title = "파일 비교 히스토리"
        else:
            items = self.data_manager.get_text_history()
            title = "텍스트 비교 히스토리"

        self.show_manager_window(category, 'history', items, title)

    def show_favorite_manager(self, category):
        """즐겨찾기 관리 창"""
        if category == 'folder':
            items = self.data_manager.get_folder_favorites()
            title = "폴더 비교 즐겨찾기"
        elif category == 'file':
            items = self.data_manager.get_file_favorites()
            title = "파일 비교 즐겨찾기"
        else:
            items = self.data_manager.get_text_favorites()
            title = "텍스트 비교 즐겨찾기"

        self.show_manager_window(category, 'favorite', items, title)

    def show_manager_window(self, category, data_type, items, title):
        """관리 창 표시"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("1000x600")

        # 상단 정보 레이블
        info_frame = ttk.Frame(win)
        info_frame.pack(fill='x', padx=10, pady=(10, 5))

        info_text = f"{title} (총 {len(items)}개)"
        ttk.Label(info_frame, text=info_text, font=('', 12, 'bold')).pack(anchor='w')

        # 리스트박스
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set,
                            font=('Consolas', 11), height=20,
                            selectmode='single', activestyle='dotbox')
        listbox.pack(fill='both', expand=True)
        scrollbar.config(command=listbox.yview)

        def refresh_list():
            listbox.delete(0, 'end')
            current_items = items if data_type == 'history' else \
                           (self.data_manager.get_folder_favorites() if category == 'folder' else \
                            self.data_manager.get_file_favorites() if category == 'file' else \
                            self.data_manager.get_text_favorites())

            for idx, item in enumerate(current_items):
                if category == 'folder':
                    # 폴더 경로만 표시
                    if data_type == 'favorite':
                        display = f"⭐ {item['name']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                    else:
                        display = f"📅 {item['timestamp']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                elif category == 'file':
                    # 파일 경로 및 이름만 표시
                    if data_type == 'favorite':
                        display = f"⭐ {item['name']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                    else:
                        display = f"📅 {item['timestamp']}\n   왼쪽: {item['left']}\n   오른쪽: {item['right']}"
                else:  # text
                    if data_type == 'favorite':
                        display = f"⭐ {item['name']}\n   왼쪽: {item['left_preview']}\n   오른쪽: {item['right_preview']}"
                    else:
                        display = f"📅 {item['timestamp']}\n   왼쪽: {item['left_preview']}\n   오른쪽: {item['right_preview']}"
                listbox.insert('end', display)
                # 구분선 추가
                if idx < len(current_items) - 1:
                    listbox.insert('end', '─' * 90)

            # 정보 레이블 업데이트
            info_text = f"{title} (총 {len(current_items)}개)"
            for widget in info_frame.winfo_children():
                widget.destroy()
            ttk.Label(info_frame, text=info_text, font=('', 12, 'bold')).pack(anchor='w')

        refresh_list()

        # 버튼
        button_frame = ttk.Frame(win)
        button_frame.pack(fill='x', padx=10, pady=10)

        def delete_item():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "삭제할 항목을 선택해주세요.")
                return

            # 구분선 제외
            index = selection[0]
            if index % 2 == 1:  # 구분선 선택
                messagebox.showwarning("경고", "항목을 선택해주세요. (구분선이 아닌 항목을 선택하세요)")
                return

            actual_index = index // 2

            if messagebox.askyesno("확인", "선택한 항목을 삭제하시겠습니까?"):
                if data_type == 'history':
                    self.data_manager.delete_history(category, actual_index)
                else:
                    self.data_manager.delete_favorite(category, actual_index)
                refresh_list()

        def rename_item():
            if data_type == 'history':
                messagebox.showinfo("알림", "히스토리는 이름을 변경할 수 없습니다.")
                return

            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "이름을 변경할 항목을 선택해주세요.")
                return

            # 구분선 제외
            index = selection[0]
            if index % 2 == 1:  # 구분선 선택
                messagebox.showwarning("경고", "항목을 선택해주세요. (구분선이 아닌 항목을 선택하세요)")
                return

            actual_index = index // 2

            new_name = simpledialog.askstring("이름 변경", "새 이름을 입력하세요:")
            if new_name:
                self.data_manager.rename_favorite(category, actual_index, new_name)
                refresh_list()

        ttk.Button(button_frame, text="삭제", command=delete_item).pack(side='left', padx=5)
        if data_type == 'favorite':
            ttk.Button(button_frame, text="이름 변경", command=rename_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="닫기", command=win.destroy).pack(side='left', padx=5)


def main():
    root = tk.Tk()
    app = CompareToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
