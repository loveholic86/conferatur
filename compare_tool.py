#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 및 폴더 비교 도구
세 가지 모드를 지원:
1. 폴더 비교 (MD5/날짜)
2. 텍스트 직접 비교
3. 파일 내용 비교
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import tkinter as tk
import tkinter.font as tkfont
import os
import sys
import platform as _platform_mod
import hashlib
import difflib
import shutil
import json
import fnmatch
import re
from datetime import datetime
from pathlib import Path


PRETENDARD_FONT_DIR = Path(__file__).resolve().parent / 'font' / 'PretendardStd'


def register_pretendard_fonts(root=None):
    """Register bundled PretendardStd OTFs so tkinter can resolve 'Pretendard Std'.

    Strategy (in order):
      1) tkextrafont (optional, cross-platform) — silently skipped if not installed.
      2) macOS: copy OTFs into ~/Library/Fonts/Conferatur/ (one-time, user scope, no admin).
      3) Linux: copy OTFs into ~/.fonts/Conferatur/ (one-time, user scope; fc-cache refresh).
      4) Windows: AddFontResourceExW with FR_PRIVATE (no admin needed).
    Returns the number of font files successfully registered/installed.
    """
    if not PRETENDARD_FONT_DIR.is_dir():
        return 0

    otf_files = sorted(PRETENDARD_FONT_DIR.glob('*.otf'))
    if not otf_files:
        return 0

    registered = 0

    try:
        from tkextrafont import Font as _ExtraFont  # type: ignore
    except Exception:
        _ExtraFont = None

    if _ExtraFont is not None:
        for otf in otf_files:
            try:
                _ExtraFont(root=root, file=str(otf))
                registered += 1
            except Exception as exc:  # noqa: BLE001
                print(f"[font] tkextrafont 등록 실패: {otf.name} ({exc})", file=sys.stderr)
        if registered:
            return registered

    system = _platform_mod.system()

    if system == 'Darwin':
        try:
            target_dir = Path.home() / 'Library' / 'Fonts' / 'Conferatur'
            target_dir.mkdir(parents=True, exist_ok=True)
            for otf in otf_files:
                dest = target_dir / otf.name
                if not dest.exists():
                    shutil.copy2(otf, dest)
                registered += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[font] macOS 폰트 설치 실패: {exc}", file=sys.stderr)
        return registered

    if system == 'Linux':
        try:
            target_dir = Path.home() / '.fonts' / 'Conferatur'
            target_dir.mkdir(parents=True, exist_ok=True)
            for otf in otf_files:
                dest = target_dir / otf.name
                if not dest.exists():
                    shutil.copy2(otf, dest)
                registered += 1
            try:
                import subprocess
                subprocess.run(['fc-cache', '-f', str(target_dir)],
                               check=False, capture_output=True, timeout=10)
            except Exception:
                pass
        except Exception as exc:  # noqa: BLE001
            print(f"[font] Linux 폰트 설치 실패: {exc}", file=sys.stderr)
        return registered

    if system == 'Windows':
        try:
            import ctypes
            FR_PRIVATE = 0x10
            gdi32 = ctypes.windll.gdi32
            for otf in otf_files:
                added = gdi32.AddFontResourceExW(str(otf), FR_PRIVATE, 0)
                if added:
                    registered += added
        except Exception as exc:  # noqa: BLE001
            print(f"[font] Windows AddFontResourceExW 실패: {exc}", file=sys.stderr)

    return registered


NOTION_COLORS = {
    'primary': '#6E4FF6',
    'primary_hover': '#5B3FE6',
    'purple_ink': '#5B3FE6',
    'brand_navy': '#1F2937',
    'canvas': '#FFFFFF',
    'surface': '#F7F6F3',
    'hairline': '#E9E9E7',
    'ink': '#37352F',
    'slate': '#787774',
    'link_blue': '#0B6E99',
    'peach': '#FBECDD',
    'rose': '#FBE4E4',
    'rose_ink': '#9B2C2C',
    'diff_line_left_only_bg': '#FBE4E4',
    'diff_line_right_only_bg': '#FBE4E4',
    'diff_line_replace_bg': '#DDEBF1',
    'mint': '#DEF4E8',
    'mint_ink': '#2D6A4F',
    'lavender': '#E8DEEE',
    'sky': '#DDEBF1',
    'yellow': '#FBF3DB',
    'yellow_bold': '#F5C13D',
    'success': '#68B984',
    'warning': '#F0995C',
    'error': '#E25C5C',
}

NOTION_UI_FONT_CANDIDATES = (
    'Pretendard Std',
    'PretendardStd',
    'Pretendard',
    'Inter',
    'SF Pro Display',
    '-apple-system',
    'Segoe UI',
    'Apple SD Gothic Neo',
    'Malgun Gothic',
    'Helvetica',
    'Arial',
)

BUTTON_SPACING = 8
BUTTON_GROUP_SPACING = 12
BUTTON_PADDING = (14, 8)
COMPACT_BUTTON_PADDING = (10, 6)
DEFAULT_TEXT_FONT_SIZE = 14
SECTION_PADDING = 16
SECTION_GAP = 24

BUTTON_STYLE_BY_ROLE = {
    'primary': 'Modern.Primary.TButton',
    'secondary': 'Modern.Secondary.TButton',
    'success': 'Modern.Success.TButton',
    'destructive': 'Modern.Destructive.TButton',
    'ghost': 'Modern.Ghost.TButton',
}

COMPACT_BUTTON_STYLE_BY_ROLE = {
    'primary': 'Modern.Primary.Compact.TButton',
    'secondary': 'Modern.Secondary.Compact.TButton',
    'success': 'Modern.Success.Compact.TButton',
    'destructive': 'Modern.Destructive.Compact.TButton',
    'ghost': 'Modern.Ghost.Compact.TButton',
}


def resolve_ui_font(root):
    """Use Inter when installed, otherwise keep a native-looking fallback."""
    try:
        available_fonts = set(tkfont.families(root))
        for font_family in NOTION_UI_FONT_CANDIDATES:
            if font_family in available_fonts:
                return font_family
    except tk.TclError:
        pass
    return 'Helvetica'


def setup_notion_styles(root):
    """Apply the Notion visual system to ttkbootstrap without changing behavior."""
    colors = NOTION_COLORS
    style = root.style if hasattr(root, 'style') else ttk.Style()
    ui_font = resolve_ui_font(root)
    body_font = (ui_font, DEFAULT_TEXT_FONT_SIZE)
    button_font = (ui_font, DEFAULT_TEXT_FONT_SIZE, 'normal')
    compact_button_font = (ui_font, DEFAULT_TEXT_FONT_SIZE - 1, 'normal')
    heading_font = (ui_font, DEFAULT_TEXT_FONT_SIZE + 1, 'bold')

    try:
        root.configure(bg=colors['surface'])
    except tk.TclError:
        pass

    def configure(style_name, **kwargs):
        try:
            style.configure(style_name, **kwargs)
        except tk.TclError:
            pass

    def map_style(style_name, **kwargs):
        try:
            style.map(style_name, **kwargs)
        except tk.TclError:
            pass

    configure('.', background=colors['surface'], foreground=colors['ink'], font=body_font)
    configure('TFrame', background=colors['surface'])
    configure('TLabel', background=colors['surface'], foreground=colors['ink'], font=body_font)
    configure('TLabelframe', background=colors['surface'], bordercolor=colors['hairline'], relief='solid')
    configure('TLabelframe.Label', background=colors['surface'], foreground=colors['ink'], font=heading_font)
    configure('TEntry',
              fieldbackground=colors['canvas'],
              foreground=colors['ink'],
              bordercolor=colors['hairline'],
              lightcolor=colors['hairline'],
              darkcolor=colors['hairline'],
              insertcolor=colors['primary'],
              padding=(8, 6))
    configure('TCombobox',
              fieldbackground=colors['canvas'],
              foreground=colors['ink'],
              bordercolor=colors['hairline'],
              arrowcolor=colors['slate'],
              padding=(8, 5))
    configure('TSpinbox',
              fieldbackground=colors['canvas'],
              foreground=colors['ink'],
              bordercolor=colors['hairline'],
              arrowcolor=colors['slate'],
              padding=(8, 5))
    configure('TRadiobutton', background=colors['surface'], foreground=colors['ink'], font=body_font)
    configure('TScrollbar',
              background=colors['hairline'],
              troughcolor=colors['surface'],
              bordercolor=colors['surface'],
              arrowcolor=colors['slate'])
    configure('TNotebook',
              background=colors['surface'],
              bordercolor=colors['hairline'],
              tabmargins=(6, 6, 6, 0))
    configure('TNotebook.Tab',
              background=colors['surface'],
              foreground=colors['slate'],
              padding=(16, 8),
              font=button_font)
    map_style('TNotebook.Tab',
              background=[('selected', colors['canvas']), ('active', colors['sky'])],
              foreground=[('selected', colors['ink']), ('active', colors['ink'])])
    configure('Treeview',
              background=colors['canvas'],
              fieldbackground=colors['canvas'],
              foreground=colors['ink'],
              bordercolor=colors['hairline'],
              rowheight=32,
              font=body_font)
    configure('Treeview.Heading',
              background=colors['surface'],
              foreground=colors['ink'],
              bordercolor=colors['hairline'],
              font=heading_font,
              padding=(8, 6))
    map_style('Treeview',
              background=[('selected', colors['lavender'])],
              foreground=[('selected', colors['purple_ink'])])

    button_styles = {
        'TButton': (colors['canvas'], colors['ink'], colors['hairline'], colors['surface']),
        'primary.TButton': (colors['lavender'], colors['purple_ink'], colors['lavender'], colors['sky']),
        'success.TButton': (colors['mint'], colors['mint_ink'], colors['mint'], colors['surface']),
        'info.TButton': (colors['sky'], colors['link_blue'], colors['sky'], colors['surface']),
        'warning.TButton': (colors['yellow'], colors['ink'], colors['yellow'], colors['surface']),
        'danger.TButton': (colors['rose'], colors['rose_ink'], colors['rose'], colors['surface']),
    }

    for style_name, (background, foreground, border, active_background) in button_styles.items():
        configure(style_name,
                  background=background,
                  foreground=foreground,
                  bordercolor=border,
                  lightcolor=border,
                  darkcolor=border,
                  focusthickness=1,
                  focuscolor=border,
                  padding=BUTTON_PADDING,
                  font=button_font)
        map_style(style_name,
                  background=[('pressed', active_background), ('active', active_background), ('disabled', colors['hairline'])],
                  foreground=[('disabled', colors['slate'])])

    modern_button_styles = {
        'Modern.Primary.TButton': {
            'background': colors['lavender'],
            'foreground': colors['purple_ink'],
            'bordercolor': colors['lavender'],
            'active_background': colors['sky'],
            'active_foreground': colors['purple_ink'],
            'padding': BUTTON_PADDING,
            'font': button_font,
        },
        'Modern.Secondary.TButton': {
            'background': colors['surface'],
            'foreground': colors['ink'],
            'bordercolor': colors['hairline'],
            'active_background': colors['canvas'],
            'active_foreground': colors['ink'],
            'padding': BUTTON_PADDING,
            'font': button_font,
        },
        'Modern.Success.TButton': {
            'background': colors['mint'],
            'foreground': colors['mint_ink'],
            'bordercolor': colors['mint'],
            'active_background': colors['surface'],
            'active_foreground': colors['mint_ink'],
            'padding': BUTTON_PADDING,
            'font': button_font,
        },
        'Modern.Destructive.TButton': {
            'background': colors['rose'],
            'foreground': colors['rose_ink'],
            'bordercolor': colors['rose'],
            'active_background': colors['rose'],
            'active_foreground': colors['rose_ink'],
            'padding': BUTTON_PADDING,
            'font': button_font,
        },
        'Modern.Ghost.TButton': {
            'background': colors['canvas'],
            'foreground': colors['ink'],
            'bordercolor': colors['hairline'],
            'active_background': colors['surface'],
            'active_foreground': colors['ink'],
            'padding': BUTTON_PADDING,
            'font': button_font,
        },
        'Modern.Primary.Compact.TButton': {
            'background': colors['lavender'],
            'foreground': colors['purple_ink'],
            'bordercolor': colors['lavender'],
            'active_background': colors['sky'],
            'active_foreground': colors['purple_ink'],
            'padding': COMPACT_BUTTON_PADDING,
            'font': compact_button_font,
        },
        'Modern.Secondary.Compact.TButton': {
            'background': colors['surface'],
            'foreground': colors['ink'],
            'bordercolor': colors['hairline'],
            'active_background': colors['canvas'],
            'active_foreground': colors['ink'],
            'padding': COMPACT_BUTTON_PADDING,
            'font': compact_button_font,
        },
        'Modern.Success.Compact.TButton': {
            'background': colors['mint'],
            'foreground': colors['mint_ink'],
            'bordercolor': colors['mint'],
            'active_background': colors['surface'],
            'active_foreground': colors['mint_ink'],
            'padding': COMPACT_BUTTON_PADDING,
            'font': compact_button_font,
        },
        'Modern.Destructive.Compact.TButton': {
            'background': colors['rose'],
            'foreground': colors['rose_ink'],
            'bordercolor': colors['rose'],
            'active_background': colors['rose'],
            'active_foreground': colors['rose_ink'],
            'padding': COMPACT_BUTTON_PADDING,
            'font': compact_button_font,
        },
        'Modern.Ghost.Compact.TButton': {
            'background': colors['canvas'],
            'foreground': colors['ink'],
            'bordercolor': colors['hairline'],
            'active_background': colors['surface'],
            'active_foreground': colors['ink'],
            'padding': COMPACT_BUTTON_PADDING,
            'font': compact_button_font,
        },
    }

    for style_name, options in modern_button_styles.items():
        border = options['bordercolor']
        configure(style_name,
                  background=options['background'],
                  foreground=options['foreground'],
                  bordercolor=border,
                  lightcolor=border,
                  darkcolor=border,
                  focusthickness=1,
                  focuscolor=border,
                  padding=options['padding'],
                  font=options['font'])
        map_style(style_name,
                  background=[('pressed', options['active_background']),
                              ('active', options['active_background']),
                              ('disabled', colors['hairline'])],
                  foreground=[('pressed', options['active_foreground']),
                              ('active', options['active_foreground']),
                              ('disabled', colors['slate'])],
                  bordercolor=[('pressed', options['active_foreground']),
                               ('active', options['active_foreground']),
                               ('disabled', colors['hairline'])])

    return ui_font


def build_button_text(label, icon=None):
    if icon:
        return f"{icon} {label}"
    return label


def create_action_button(parent, label, command, role='secondary', icon=None,
                         compact=False, width=None, state=None, **kwargs):
    """Create a consistent modern action button while preserving callbacks."""
    style_map = COMPACT_BUTTON_STYLE_BY_ROLE if compact else BUTTON_STYLE_BY_ROLE
    button_options = {
        'text': build_button_text(label, icon),
        'command': command,
        'style': style_map.get(role, BUTTON_STYLE_BY_ROLE['secondary']),
    }
    if width is not None:
        button_options['width'] = width
    if state is not None:
        button_options['state'] = state
    button_options.update(kwargs)
    return ttk.Button(parent, **button_options)


def build_button_row(parent, specs, align='right', gap=BUTTON_SPACING, pady=(8, 0)):
    row = ttk.Frame(parent)
    row.pack(fill='x', pady=pady)

    if align == 'left':
        side = 'left'
        ordered_specs = specs
    else:
        side = 'right'
        ordered_specs = list(reversed(specs))

    buttons = []
    for index, spec in enumerate(ordered_specs):
        button = create_action_button(row, **spec)
        pad = (0, gap) if side == 'right' and index < len(ordered_specs) - 1 else (gap, 0)
        if side == 'left':
            pad = (0, gap) if index < len(ordered_specs) - 1 else (0, 0)
        button.pack(side=side, padx=pad)
        buttons.append(button)

    return row, list(reversed(buttons)) if align != 'left' else buttons


def build_toolbar(parent, left_specs=None, right_specs=None, pady=(8, 8)):
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill='x', pady=pady)

    left_buttons = []
    right_buttons = []
    if left_specs:
        for index, spec in enumerate(left_specs):
            button = create_action_button(toolbar, **spec)
            padx = (0, BUTTON_SPACING) if index < len(left_specs) - 1 else (0, 0)
            button.pack(side='left', padx=padx)
            left_buttons.append(button)

    if right_specs:
        for index, spec in enumerate(reversed(right_specs)):
            button = create_action_button(toolbar, **spec)
            padx = (0, BUTTON_SPACING) if index < len(right_specs) - 1 else (0, 0)
            button.pack(side='right', padx=padx)
            right_buttons.append(button)

    return toolbar, left_buttons, list(reversed(right_buttons))


def build_history_favorite_row(parent, app, category):
    specs = [
        {
            'label': '히스토리',
            'icon': '📜',
            'command': lambda: app.load_from_history(category),
            'role': 'ghost',
            'compact': True,
        },
        {
            'label': '즐겨찾기 불러오기',
            'icon': '⭐',
            'command': lambda: app.load_from_favorite(category),
            'role': 'ghost',
            'compact': True,
        },
        {
            'label': '즐겨찾기 추가',
            'icon': '＋',
            'command': lambda: app.add_to_favorite(category),
            'role': 'ghost',
            'compact': True,
        },
    ]
    return build_button_row(parent, specs, align='left', gap=BUTTON_SPACING, pady=(0, 12))


def notion_text_options(font=None):
    colors = NOTION_COLORS
    options = {
        'bg': colors['canvas'],
        'fg': colors['ink'],
        'insertbackground': colors['primary'],
        'selectbackground': colors['sky'],
        'selectforeground': colors['ink'],
        'relief': 'solid',
        'borderwidth': 1,
        'highlightthickness': 1,
        'highlightbackground': colors['hairline'],
        'highlightcolor': colors['primary'],
    }
    if font is not None:
        options['font'] = font
    return options


def configure_notion_text_widget(widget, font=None):
    if font is None:
        try:
            font = (resolve_ui_font(widget.winfo_toplevel()), DEFAULT_TEXT_FONT_SIZE)
        except tk.TclError:
            font = ('Helvetica', DEFAULT_TEXT_FONT_SIZE)
    widget.config(**notion_text_options(font))


def configure_notion_diff_tag(widget, font_family, font_size):
    widget.tag_configure('diff_line_left_only',
                         background=NOTION_COLORS['diff_line_left_only_bg'])
    widget.tag_configure('diff_line_right_only',
                         background=NOTION_COLORS['diff_line_right_only_bg'])
    widget.tag_configure('diff_line_replace',
                         background=NOTION_COLORS['diff_line_replace_bg'])
    widget.tag_config('diff',
                      background=NOTION_COLORS['yellow'],
                      foreground=NOTION_COLORS['error'],
                      font=(font_family, font_size, 'bold'))
    widget.tag_raise('diff')


def configure_notion_listbox(listbox, font=None):
    colors = NOTION_COLORS
    options = {
        'bg': colors['canvas'],
        'fg': colors['ink'],
        'selectbackground': colors['lavender'],
        'selectforeground': colors['ink'],
        'highlightthickness': 1,
        'highlightbackground': colors['hairline'],
        'highlightcolor': colors['primary'],
        'relief': 'solid',
        'borderwidth': 1,
    }
    if font is not None:
        options['font'] = font
    listbox.config(**options)


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
            'file_favorites': [],
            'font_family': 'Pretendard Std',  # 기본 폰트 (PretendardStd OTF 번들)
            'font_size': DEFAULT_TEXT_FONT_SIZE,  # 신규 사용자 기본 폰트 크기
            'exclude_patterns': []       # 폴더 비교 제외 패턴
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

    def get_font_settings(self):
        """폰트 설정 가져오기"""
        return {
            'family': self.data.get('font_family', 'Pretendard Std'),
            'size': self.data.get('font_size', DEFAULT_TEXT_FONT_SIZE)
        }

    def set_font_settings(self, family, size):
        """폰트 설정 저장"""
        self.data['font_family'] = family
        self.data['font_size'] = size
        self.save()

    def get_exclude_patterns(self):
        """제외 패턴 가져오기"""
        return self.data.get('exclude_patterns', [])

    def set_exclude_patterns(self, patterns):
        """제외 패턴 저장"""
        self.data['exclude_patterns'] = patterns
        self.save()


class CompareToolApp:
    def __init__(self, root):
        self.root = root

        # OS 감지 (한 번만 수행)
        import platform
        self.system = platform.system()
        self.is_macos = (self.system == 'Darwin')
        self.is_windows = (self.system == 'Windows')
        self.is_linux = (self.system == 'Linux')

        # OS별 타이틀 설정
        os_name = "macOS" if self.is_macos else ("Windows" if self.is_windows else "Linux")
        self.root.title(f"📂 파일/폴더 비교 도구 [{os_name}]")
        self.root.geometry("1300x850")
        self.root.minsize(1280, 800)

        # OS 정보 출력
        print(f"=== 파일/폴더 비교 도구 시작 ===")
        print(f"테마: minty + Notion overrides (ttkbootstrap)")
        print(f"운영체제: {self.system} ({os_name})")
        if self.is_macos:
            print(f"키보드 단축키: Cmd+C (복사), Cmd+V (붙여넣기), Cmd+X (잘라내기), Cmd+A (전체선택)")
        else:
            print(f"키보드 단축키: Ctrl+C (복사), Ctrl+V (붙여넣기), Ctrl+X (잘라내기), Ctrl+A (전체선택)")
        print(f"우클릭: 컨텍스트 메뉴")
        print()

        # 데이터 매니저 초기화
        self.data_manager = DataManager()

        # 폰트 설정 로드
        font_settings = self.data_manager.get_font_settings()
        self.font_family = font_settings['family']
        self.font_size = font_settings['size']

        # 파일 비교 차이점 블록 정보 저장
        self.file_diff_blocks = []  # 파일 비교 모드의 차이점 블록 정보
        self.text_diff_blocks = []  # 텍스트 비교 모드의 차이점 블록 정보
        self._folder_tree_raw_names = {}
        self._folder_sort_state = {'col': None, 'reverse': False}
        self._folder_tree_heading_labels = {}

        # 메뉴바 생성
        self.create_menubar()

        # 탭 생성
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 세 가지 모드 탭 생성
        self.folder_compare_tab = ttk.Frame(self.notebook)
        self.text_compare_tab = ttk.Frame(self.notebook)
        self.file_compare_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.folder_compare_tab, text=" 📁 폴더 비교 ")
        self.notebook.add(self.text_compare_tab, text=" 📝 텍스트 비교 ")
        self.notebook.add(self.file_compare_tab, text=" 📄 파일 비교 ")

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

        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="폰트 설정", command=self.show_font_settings)

    def setup_folder_compare_tab(self):
        """첫 번째 모드: 폴더 비교"""
        frame = self.folder_compare_tab

        # 상단 컨트롤 영역
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=SECTION_PADDING, pady=SECTION_PADDING)

        # 히스토리 및 즐겨찾기 버튼
        history_fav_frame = ttk.Frame(control_frame)
        history_fav_frame.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 12))
        build_history_favorite_row(history_fav_frame, self, 'folder')

        # 왼쪽 폴더 선택
        ttk.Label(control_frame, text="왼쪽 폴더:").grid(row=1, column=0, sticky='w', padx=(0, 8), pady=5)
        self.left_folder_var = tk.StringVar()
        self.left_folder_entry = ttk.Entry(control_frame, textvariable=self.left_folder_var)
        self.left_folder_entry.grid(row=1, column=1, sticky='ew', padx=(0, 8), pady=5)
        create_action_button(control_frame, "찾아보기",
                             command=lambda: self.browse_folder(self.left_folder_var, self.left_folder_entry),
                             role='secondary', icon='📁').grid(row=1, column=2, padx=0, pady=5)

        # 오른쪽 폴더 선택
        ttk.Label(control_frame, text="오른쪽 폴더:").grid(row=2, column=0, sticky='w', padx=(0, 8), pady=5)
        self.right_folder_var = tk.StringVar()
        self.right_folder_entry = ttk.Entry(control_frame, textvariable=self.right_folder_var)
        self.right_folder_entry.grid(row=2, column=1, sticky='ew', padx=(0, 8), pady=5)
        create_action_button(control_frame, "찾아보기",
                             command=lambda: self.browse_folder(self.right_folder_var, self.right_folder_entry),
                             role='secondary', icon='📁').grid(row=2, column=2, padx=0, pady=5)

        # Entry 위젯이 확장되도록 column 1에 weight 설정
        control_frame.columnconfigure(1, weight=1)

        # 비교 옵션
        option_frame = ttk.Frame(control_frame)
        option_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(12, 0))

        self.compare_method_var = tk.StringVar(value="md5")
        method_frame = ttk.Frame(option_frame)
        method_frame.pack(side='left', fill='x', expand=True)
        ttk.Radiobutton(method_frame, text="🔍 MD5 비교", variable=self.compare_method_var, value="md5").pack(side='left', padx=(0, 12))
        ttk.Radiobutton(method_frame, text="📅 날짜 비교", variable=self.compare_method_var, value="date").pack(side='left', padx=(0, 12))
        ttk.Radiobutton(method_frame, text="🔍📅 MD5 + 날짜", variable=self.compare_method_var, value="both").pack(side='left')

        action_frame = ttk.Frame(option_frame)
        action_frame.pack(side='right')
        build_button_row(action_frame, [
            {'label': '초기화', 'icon': '↻', 'command': self.clear_folder_comparison, 'role': 'ghost'},
            {'label': '제외 패턴', 'icon': '⚙️', 'command': self.open_exclude_patterns_dialog, 'role': 'secondary'},
            {'label': '비교 시작', 'icon': '▶', 'command': self.compare_folders, 'role': 'primary'},
        ], align='right', pady=(0, 0))

        # 결과 영역
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill='both', expand=True, padx=SECTION_PADDING, pady=(0, SECTION_PADDING))

        # 트리뷰 생성
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill='both', expand=True)

        build_toolbar(tree_frame,
                      left_specs=[
                          {'label': '왼쪽 → 오른쪽 복사', 'icon': '📤',
                           'command': lambda: self.copy_file('left_to_right'), 'role': 'secondary'},
                          {'label': '오른쪽 → 왼쪽 복사', 'icon': '📥',
                           'command': lambda: self.copy_file('right_to_left'), 'role': 'secondary'},
                          {'label': '모두 펼치기', 'icon': '⊞',
                           'command': self.expand_all_folder_tree, 'role': 'ghost'},
                          {'label': '모두 접기', 'icon': '⊟',
                           'command': self.collapse_all_folder_tree, 'role': 'ghost'},
                      ],
                      right_specs=[
                          {'label': '선택 항목 삭제', 'icon': '🗑️',
                           'command': self.delete_selected, 'role': 'destructive'},
                      ],
                      pady=(0, 8))

        # 스크롤바
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')

        # 트리뷰
        self.folder_tree = ttk.Treeview(tree_frame,
                                        columns=('상태', '왼쪽_크기', '왼쪽_수정일', '오른쪽_크기', '오른쪽_수정일'),
                                        displaycolumns=('상태', '왼쪽_크기', '오른쪽_크기', '왼쪽_수정일', '오른쪽_수정일'),
                                        yscrollcommand=tree_scroll_y.set,
                                        xscrollcommand=tree_scroll_x.set)
        self.folder_tree.pack(fill='both', expand=True)
        self._configure_folder_tree_tags()

        tree_scroll_y.config(command=self.folder_tree.yview)
        tree_scroll_x.config(command=self.folder_tree.xview)

        # 트리뷰 열 설정
        self._folder_tree_heading_labels = {
            '#0': '파일 경로',
            '상태': '상태',
            '왼쪽_크기': '왼쪽 크기',
            '오른쪽_크기': '오른쪽 크기',
            '왼쪽_수정일': '왼쪽 수정일',
            '오른쪽_수정일': '오른쪽 수정일',
        }
        self._update_folder_tree_headings()

        self.folder_tree.column('#0', width=360, minwidth=220)
        self.folder_tree.column('상태', width=150, minwidth=120)
        self.folder_tree.column('왼쪽_크기', width=85, minwidth=70, anchor='e')
        self.folder_tree.column('오른쪽_크기', width=85, minwidth=70, anchor='e')
        self.folder_tree.column('왼쪽_수정일', width=155, minwidth=135)
        self.folder_tree.column('오른쪽_수정일', width=155, minwidth=135)

        # 트리뷰 선택 이벤트 바인딩
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_tree_select)

        # 컨텍스트 메뉴 생성 (루트 윈도우에 연결)
        self.folder_tree_context_menu = tk.Menu(self.root, tearoff=0)
        self.folder_tree_context_menu.add_command(
            label="📤 왼쪽 → 오른쪽 복사",
            command=lambda: self.copy_file('left_to_right')
        )
        self.folder_tree_context_menu.add_command(
            label="📥 오른쪽 → 왼쪽 복사",
            command=lambda: self.copy_file('right_to_left')
        )
        self.folder_tree_context_menu.add_separator()
        self.folder_tree_context_menu.add_command(
            label="🗑️ 선택 항목 삭제",
            command=self.delete_selected
        )

        # 우클릭 이벤트 바인딩 (플랫폼별 지원)
        # Linux/Windows: Button-3, macOS: Button-2 or Control-Button-1
        self.folder_tree.bind('<Button-3>', self.show_folder_tree_context_menu)
        self.folder_tree.bind('<Button-2>', self.show_folder_tree_context_menu)
        self.folder_tree.bind('<Control-Button-1>', self.show_folder_tree_context_menu)

        # 파일 내용 미리보기 영역
        preview_label = ttk.Label(
            result_frame,
            text="파일 내용 미리보기 (파일을 선택하세요)",
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE, 'bold')
        )
        preview_label.pack(fill='x', pady=(16, 5))

        preview_frame = ttk.Frame(result_frame)
        preview_frame.pack(fill='both', expand=True, pady=5)

        # 왼쪽 파일 미리보기
        left_preview_frame = ttk.Frame(preview_frame)
        left_preview_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(
            left_preview_frame,
            text="왼쪽 파일",
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE - 1, 'bold')
        ).pack()
        self.folder_preview_left = scrolledtext.ScrolledText(left_preview_frame, wrap='word', width=40, height=15, state='disabled')
        self.folder_preview_left.pack(fill='both', expand=True)

        # 오른쪽 파일 미리보기
        right_preview_frame = ttk.Frame(preview_frame)
        right_preview_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(
            right_preview_frame,
            text="오른쪽 파일",
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE - 1, 'bold')
        ).pack()
        self.folder_preview_right = scrolledtext.ScrolledText(right_preview_frame, wrap='word', width=40, height=15, state='disabled')
        self.folder_preview_right.pack(fill='both', expand=True)

        # 텍스트 위젯 Notion 스타일
        configure_notion_text_widget(self.folder_preview_left, (self.font_family, self.font_size))
        configure_notion_text_widget(self.folder_preview_right, (self.font_family, self.font_size))

        # 차이점 표시
        configure_notion_diff_tag(self.folder_preview_left, self.font_family, self.font_size)
        configure_notion_diff_tag(self.folder_preview_right, self.font_family, self.font_size)

        # 스크롤 동기화
        self.setup_scroll_sync(self.folder_preview_left, self.folder_preview_right)

    def _configure_folder_tree_tags(self):
        """폴더 비교 트리의 상태별 시각 태그를 등록."""
        self.folder_tree.tag_configure('diff',
                                       background='#FCE7E7',
                                       foreground=NOTION_COLORS['rose_ink'])
        self.folder_tree.tag_configure('left_only',
                                       background='#F2F2F0',
                                       foreground='#6F6E69')
        self.folder_tree.tag_configure('right_only',
                                       background='#F2F2F0',
                                       foreground='#6F6E69')
        self.folder_tree.tag_configure('left_newer',
                                       background=NOTION_COLORS['peach'],
                                       foreground='#9C4221')
        self.folder_tree.tag_configure('right_newer',
                                       background=NOTION_COLORS['peach'],
                                       foreground='#9C4221')
        self.folder_tree.tag_configure('folder',
                                       background=NOTION_COLORS['canvas'],
                                       foreground=NOTION_COLORS['ink'],
                                       font=(self.font_family, DEFAULT_TEXT_FONT_SIZE, 'bold'))

    def _set_folder_tree_open_state(self, open_state, parent=''):
        """폴더 비교 Treeview의 자식 노드를 재귀적으로 펼치거나 접음.

        파일 노드(상태 values 있음)는 자식이 없으므로 open 상태 변경 효과 없음.
        item text/values/tags는 건드리지 않고 open 속성만 수정한다.
        """
        tree = getattr(self, 'folder_tree', None)
        if tree is None:
            return
        for child in tree.get_children(parent):
            tree.item(child, open=open_state)
            self._set_folder_tree_open_state(open_state, child)

    def expand_all_folder_tree(self):
        """폴더 비교 트리의 모든 폴더 노드를 펼침."""
        self._set_folder_tree_open_state(True)

    def collapse_all_folder_tree(self):
        """폴더 비교 트리의 모든 폴더 노드를 접음."""
        self._set_folder_tree_open_state(False)

    def _get_folder_status_visual(self, status):
        """상태 텍스트를 Treeview tag와 경로 아이콘으로 변환."""
        status_visuals = {
            '내용 다름 (MD5)': ('diff', '≠ '),
            '왼쪽만 존재': ('left_only', '◀ '),
            '오른쪽만 존재': ('right_only', '▶ '),
            '왼쪽이 최신': ('left_newer', '⏱ '),
            '오른쪽이 최신': ('right_newer', '⏱ '),
            '내용 같음, 왼쪽이 최신': ('left_newer', '⏱ '),
            '내용 같음, 오른쪽이 최신': ('right_newer', '⏱ '),
        }
        return status_visuals.get(status, ('', ''))

    def _get_folder_diff_count_key(self, status):
        """폴더 배지에서 사용할 상태 카운트 키를 반환."""
        if status == '내용 다름 (MD5)':
            return 'differ'
        if status == '왼쪽만 존재':
            return 'left_only'
        if status == '오른쪽만 존재':
            return 'right_only'
        if status in (
            '왼쪽이 최신',
            '오른쪽이 최신',
            '내용 같음, 왼쪽이 최신',
            '내용 같음, 오른쪽이 최신',
        ):
            return 'newer'
        return None

    def _annotate_folder_diff_counts(self, folder_nodes, folder_stats):
        """폴더 노드 #0 텍스트에 하위 차이 요약 배지를 붙임."""
        label_specs = (
            ('differ', 'differ'),
            ('left_only', 'left-only'),
            ('right_only', 'right-only'),
            ('newer', 'newer'),
        )
        for folder_path, item_id in folder_nodes.items():
            stats = folder_stats.get(folder_path, {})
            label_parts = [
                f"{stats[key]} {label}"
                for key, label in label_specs
                if stats.get(key)
            ]
            badge = f" ({', '.join(label_parts)})" if label_parts else ''
            folder_name = self._folder_tree_raw_names.get(item_id, os.path.basename(folder_path))
            self.folder_tree.item(item_id, text=f"📁 {folder_name}{badge}")

    def _clean_folder_tree_text(self, text):
        """raw name dict가 없을 때 표시용 아이콘/배지를 제거하는 fallback."""
        clean_text = text
        for prefix in ('📁 ', '≠ ', '◀ ', '▶ ', '⏱ '):
            if clean_text.startswith(prefix):
                clean_text = clean_text[len(prefix):]
                break
        return re.sub(
            r'\s+\(\d+ (?:differ|left-only|right-only|newer)'
            r'(?:, \d+ (?:differ|left-only|right-only|newer))*\)$',
            '',
            clean_text
        )

    def _update_folder_tree_headings(self):
        """정렬 상태 화살표를 포함해 폴더 Treeview heading을 갱신."""
        if not getattr(self, 'folder_tree', None):
            return

        current_col = self._folder_sort_state.get('col')
        reverse = self._folder_sort_state.get('reverse', False)
        for col, label in self._folder_tree_heading_labels.items():
            arrow = ''
            if col == current_col:
                arrow = ' ▼' if reverse else ' ▲'
            self.folder_tree.heading(
                col,
                text=f'{label}{arrow}',
                command=lambda c=col: self._sort_folder_tree(
                    c,
                    reverse=(
                        self._folder_sort_state.get('col') == c
                        and not self._folder_sort_state.get('reverse', False)
                    )
                )
            )

    def _get_folder_sort_value(self, item, col):
        """컬럼별 정렬 값을 반환. 크기 컬럼은 숫자로 비교."""
        if col == '#0':
            value = self._folder_tree_raw_names.get(
                item,
                self._clean_folder_tree_text(self.folder_tree.item(item, 'text'))
            )
        else:
            column_indexes = {
                '상태': 0,
                '왼쪽_크기': 1,
                '왼쪽_수정일': 2,
                '오른쪽_크기': 3,
                '오른쪽_수정일': 4,
            }
            values = self.folder_tree.item(item, 'values')
            index = column_indexes.get(col)
            value = values[index] if index is not None and len(values) > index else ''

        if col in ('왼쪽_크기', '오른쪽_크기'):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0
        return str(value).lower()

    def _sort_folder_tree_children(self, parent, col, reverse):
        """폴더 우선 그룹을 유지하면서 자식 노드를 재귀 정렬."""
        children = list(self.folder_tree.get_children(parent))
        folders = []
        files = []

        for child in children:
            values = self.folder_tree.item(child, 'values')
            if values and values[0]:
                files.append(child)
            else:
                folders.append(child)

        folders.sort(key=lambda item: self._get_folder_sort_value(item, col), reverse=reverse)
        files.sort(key=lambda item: self._get_folder_sort_value(item, col), reverse=reverse)

        for index, child in enumerate(folders + files):
            self.folder_tree.move(child, parent, index)
            self._sort_folder_tree_children(child, col, reverse)

    def _sort_folder_tree(self, col, reverse=False):
        """폴더 비교 트리를 컬럼 기준으로 정렬."""
        self._folder_sort_state = {'col': col, 'reverse': reverse}
        self._sort_folder_tree_children('', col, reverse)
        self._update_folder_tree_headings()

    def setup_text_compare_tab(self):
        """두 번째 모드: 텍스트 직접 비교"""
        frame = self.text_compare_tab

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 히스토리 및 즐겨찾기 버튼 (compact ghost row)
        history_fav_frame = ttk.Frame(control_frame)
        history_fav_frame.pack(fill='x', pady=(0, SECTION_PADDING // 2))
        build_history_favorite_row(history_fav_frame, self, 'text')

        # 액션 toolbar: 비교 primary 좌측, 적용/초기화 우측
        build_toolbar(
            control_frame,
            left_specs=[
                {'label': '비교하기', 'icon': '▶', 'command': self.compare_text, 'role': 'primary'},
            ],
            right_specs=[
                {'label': '왼쪽으로 적용', 'icon': '📥',
                 'command': lambda: self.apply_text('to_left'), 'role': 'success'},
                {'label': '오른쪽으로 적용', 'icon': '📤',
                 'command': lambda: self.apply_text('to_right'), 'role': 'success'},
                {'label': '초기화', 'icon': '🔄',
                 'command': self.clear_text_comparison, 'role': 'ghost'},
            ],
            pady=(0, SECTION_PADDING // 2),
        )

        # 텍스트 입력 영역
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 왼쪽 텍스트
        left_frame = ttk.Labelframe(text_frame, text=" 📝 왼쪽 텍스트 ", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 8))
        self.text_left = scrolledtext.ScrolledText(left_frame, wrap='word', width=40, height=30,
                                                   font=(self.font_family, self.font_size))
        self.text_left.pack(fill='both', expand=True)
        configure_notion_text_widget(self.text_left, (self.font_family, self.font_size))

        # 오른쪽 텍스트
        right_frame = ttk.Labelframe(text_frame, text=" 📝 오른쪽 텍스트 ", padding=10)
        right_frame.pack(side='left', fill='both', expand=True, padx=(8, 0))
        self.text_right = scrolledtext.ScrolledText(right_frame, wrap='word', width=40, height=30,
                                                    font=(self.font_family, self.font_size))
        self.text_right.pack(fill='both', expand=True)
        configure_notion_text_widget(self.text_right, (self.font_family, self.font_size))

        # 복사/붙여넣기 기능 활성화
        self.enable_clipboard_operations(self.text_left)
        self.enable_clipboard_operations(self.text_right)

        # 차이점 표시
        configure_notion_diff_tag(self.text_left, self.font_family, self.font_size)
        configure_notion_diff_tag(self.text_right, self.font_family, self.font_size)

        # 스크롤 동기화
        self.setup_scroll_sync(self.text_left, self.text_right)

    def setup_file_compare_tab(self):
        """세 번째 모드: 파일 내용 비교"""
        frame = self.file_compare_tab

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 히스토리 및 즐겨찾기 버튼 (compact ghost row)
        history_fav_frame = ttk.Frame(control_frame)
        history_fav_frame.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 12))
        build_history_favorite_row(history_fav_frame, self, 'file')

        # 왼쪽 파일 선택
        ttk.Label(control_frame, text="왼쪽 파일:").grid(row=1, column=0, sticky='w', padx=(0, 8), pady=5)
        self.file_left_var = tk.StringVar()
        self.file_left_entry = ttk.Entry(control_frame, textvariable=self.file_left_var)
        self.file_left_entry.grid(row=1, column=1, sticky='ew', padx=(0, 8), pady=5)
        create_action_button(control_frame, "찾아보기",
                             command=lambda: self.browse_file(self.file_left_var, self.file_left_entry),
                             role='secondary', icon='📄').grid(row=1, column=2, padx=0, pady=5)

        # 오른쪽 파일 선택
        ttk.Label(control_frame, text="오른쪽 파일:").grid(row=2, column=0, sticky='w', padx=(0, 8), pady=5)
        self.file_right_var = tk.StringVar()
        self.file_right_entry = ttk.Entry(control_frame, textvariable=self.file_right_var)
        self.file_right_entry.grid(row=2, column=1, sticky='ew', padx=(0, 8), pady=5)
        create_action_button(control_frame, "찾아보기",
                             command=lambda: self.browse_file(self.file_right_var, self.file_right_entry),
                             role='secondary', icon='📄').grid(row=2, column=2, padx=0, pady=5)

        # Entry 위젯이 확장되도록 column 1에 weight 설정
        control_frame.columnconfigure(1, weight=1)

        # 액션 버튼 영역 (두 개의 toolbar)
        button_container = ttk.Frame(control_frame)
        button_container.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(12, 0))

        # Row 1: 비교/재비교 (좌) · 초기화 (우)
        build_toolbar(
            button_container,
            left_specs=[
                {'label': '비교하기', 'icon': '▶', 'command': self.compare_files, 'role': 'primary'},
                {'label': '재비교 (편집 후)', 'icon': '🔄', 'command': self.recompare_files, 'role': 'secondary'},
            ],
            right_specs=[
                {'label': '초기화', 'icon': '↻', 'command': self.clear_file_comparison, 'role': 'ghost'},
            ],
            pady=(0, 6),
        )

        # Row 2: 블록/전체 덮어쓰기 (좌) · 좌·우 저장 (우)
        build_toolbar(
            button_container,
            left_specs=[
                {'label': '왼쪽 블록 복사', 'icon': '◀',
                 'command': self.copy_diff_to_left, 'role': 'secondary'},
                {'label': '오른쪽 블록 복사', 'icon': '▶',
                 'command': self.copy_diff_to_right, 'role': 'secondary'},
                {'label': '왼쪽 전체 덮어쓰기', 'icon': '◀◀',
                 'command': self.copy_all_to_left, 'role': 'destructive'},
                {'label': '오른쪽 전체 덮어쓰기', 'icon': '▶▶',
                 'command': self.copy_all_to_right, 'role': 'destructive'},
            ],
            right_specs=[
                {'label': '왼쪽 파일 저장', 'icon': '💾',
                 'command': lambda: self.save_file('left'), 'role': 'success'},
                {'label': '오른쪽 파일 저장', 'icon': '💾',
                 'command': lambda: self.save_file('right'), 'role': 'success'},
            ],
            pady=(0, 0),
        )

        # Row 3: diff 점프 nav (ghost)
        build_toolbar(
            button_container,
            left_specs=[
                {'label': '이전 diff', 'icon': '⏮',
                 'command': self.goto_prev_diff, 'role': 'ghost'},
                {'label': '다음 diff', 'icon': '⏭',
                 'command': self.goto_next_diff, 'role': 'ghost'},
            ],
            right_specs=None,
            pady=(6, 0),
        )

        # 파일 내용 표시 영역
        file_text_frame = ttk.Frame(frame)
        file_text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 왼쪽 파일 내용 (편집 가능)
        left_file_frame = ttk.Labelframe(file_text_frame, text=" 📄 왼쪽 파일 내용 (편집 가능) ", padding=10)
        left_file_frame.pack(side='left', fill='both', expand=True, padx=(0, 8))
        self.file_status_left = ttk.Label(
            left_file_frame, text="1:1",
            foreground=NOTION_COLORS['slate'],
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE - 1),
            anchor='w'
        )
        self.status_label_left = self.file_status_left
        self.file_status_left.pack(side='bottom', fill='x', pady=(6, 0))
        self.file_text_left = scrolledtext.ScrolledText(left_file_frame, wrap='word', width=40, height=30,
                                                        font=(self.font_family, self.font_size),
                                                        state='normal')  # 편집 가능 상태
        self.file_text_left.pack(fill='both', expand=True)
        configure_notion_text_widget(self.file_text_left, (self.font_family, self.font_size))

        # 오른쪽 파일 내용 (편집 가능)
        right_file_frame = ttk.Labelframe(file_text_frame, text=" 📄 오른쪽 파일 내용 (편집 가능) ", padding=10)
        right_file_frame.pack(side='left', fill='both', expand=True, padx=(8, 0))
        self.file_status_right = ttk.Label(
            right_file_frame, text="1:1",
            foreground=NOTION_COLORS['slate'],
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE - 1),
            anchor='w'
        )
        self.status_label_right = self.file_status_right
        self.file_status_right.pack(side='bottom', fill='x', pady=(6, 0))
        self.file_text_right = scrolledtext.ScrolledText(right_file_frame, wrap='word', width=40, height=30,
                                                         font=(self.font_family, self.font_size),
                                                         state='normal')  # 편집 가능 상태
        self.file_text_right.pack(fill='both', expand=True)
        configure_notion_text_widget(self.file_text_right, (self.font_family, self.font_size))

        # 차이점 표시
        configure_notion_diff_tag(self.file_text_left, self.font_family, self.font_size)
        configure_notion_diff_tag(self.file_text_right, self.font_family, self.font_size)

        # 복사/붙여넣기 및 차이점 복사 기능 활성화
        self.enable_file_compare_context_menu(self.file_text_left, is_left=True)
        self.enable_file_compare_context_menu(self.file_text_right, is_left=False)

        # 스크롤 동기화
        self.setup_scroll_sync(self.file_text_left, self.file_text_right)

        # 라인:컬럼 status bar 이벤트 바인딩 및 active widget 추적
        self._last_active_file_side = 'left'
        self._bind_file_status_events(self.file_text_left, self.file_status_left, 'left')
        self._bind_file_status_events(self.file_text_right, self.file_status_right, 'right')

    # 유틸리티 메서드
    def enable_clipboard_operations(self, widget):
        """텍스트 위젯에 클립보드 작업 활성화"""

        # 복사 함수 - 가상 이벤트 사용
        def do_copy(event=None):
            try:
                widget.event_generate("<<Copy>>")
            except:
                # 대체 구현
                try:
                    if widget.tag_ranges('sel'):
                        widget.clipboard_clear()
                        text = widget.get('sel.first', 'sel.last')
                        widget.clipboard_append(text)
                except:
                    pass
            return "break"

        # 잘라내기 함수 - 가상 이벤트 사용
        def do_cut(event=None):
            try:
                widget.event_generate("<<Cut>>")
            except:
                # 대체 구현
                try:
                    if widget.tag_ranges('sel'):
                        widget.clipboard_clear()
                        text = widget.get('sel.first', 'sel.last')
                        widget.clipboard_append(text)
                        widget.delete('sel.first', 'sel.last')
                except:
                    pass
            return "break"

        # 붙여넣기 함수 - 가상 이벤트 사용
        def do_paste(event=None):
            try:
                widget.event_generate("<<Paste>>")
            except:
                # 대체 구현
                try:
                    # 선택 영역이 있으면 삭제
                    if widget.tag_ranges('sel'):
                        widget.delete('sel.first', 'sel.last')
                    # 클립보드에서 가져와서 삽입
                    text = widget.clipboard_get()
                    widget.insert('insert', text)
                except:
                    pass
            return "break"

        # 전체 선택
        def do_select_all(event=None):
            widget.tag_add('sel', "1.0", "end-1c")
            widget.mark_set('insert', "1.0")
            widget.see('insert')
            return 'break'

        # OS별 키 바인딩 설정 (self.is_macos는 __init__에서 감지됨)
        if self.is_macos:  # macOS
            # macOS에서는 KeyPress 이벤트로 Command 키 조합 감지
            # (<Command-c> 바인딩이 작동하지 않음)
            def on_macos_key(event):
                """macOS Command 키 조합 감지 (state & 0x0008 = Command 키)"""
                is_command = bool(event.state & 0x0008)

                if is_command and event.char:
                    key_char = event.char.lower()
                    if key_char == 'c':
                        return do_copy(event)
                    elif key_char == 'x':
                        return do_cut(event)
                    elif key_char == 'v':
                        return do_paste(event)
                    elif key_char == 'a':
                        return do_select_all(event)
                return None

            widget.bind('<KeyPress>', on_macos_key, add='+')

        else:  # Windows, Linux
            # Windows/Linux는 Control 키 사용
            widget.bind('<Control-c>', do_copy, add='+')
            widget.bind('<Control-x>', do_cut, add='+')
            widget.bind('<Control-v>', do_paste, add='+')
            widget.bind('<Control-a>', do_select_all, add='+')

            # Windows용 대체 키 바인딩
            widget.bind('<Control-Insert>', do_copy, add='+')
            widget.bind('<Shift-Delete>', do_cut, add='+')
            widget.bind('<Shift-Insert>', do_paste, add='+')

        # 우클릭 컨텍스트 메뉴
        context_menu = tk.Menu(widget, tearoff=0)

        # OS에 따른 단축키 표시 텍스트
        key_modifier = "Cmd" if self.is_macos else "Ctrl"

        def show_context_menu(event):
            """우클릭 시 컨텍스트 메뉴 표시"""
            context_menu.delete(0, tk.END)  # 기존 메뉴 항목 제거

            # 메뉴 항목 추가 (OS에 맞는 단축키 표시)
            context_menu.add_command(label=f"복사 ({key_modifier}+C)", command=do_copy)
            context_menu.add_command(label=f"잘라내기 ({key_modifier}+X)", command=do_cut)
            context_menu.add_command(label=f"붙여넣기 ({key_modifier}+V)", command=do_paste)
            context_menu.add_separator()
            context_menu.add_command(label=f"전체 선택 ({key_modifier}+A)", command=do_select_all)

            # 메뉴 표시
            try:
                context_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                context_menu.grab_release()

        # 우클릭 이벤트 바인딩
        widget.bind('<Button-3>', show_context_menu, add='+')
        if self.is_macos:
            # macOS는 여러 방식의 우클릭 지원
            widget.bind('<Button-2>', show_context_menu, add='+')
            widget.bind('<Control-Button-1>', show_context_menu, add='+')

    def enable_file_compare_context_menu(self, widget, is_left):
        """파일 비교 텍스트 위젯에 차이점 복사 기능이 포함된 컨텍스트 메뉴 추가

        Args:
            widget: 텍스트 위젯 (file_text_left 또는 file_text_right)
            is_left: 왼쪽 위젯인지 여부
        """
        # 기본 클립보드 기능을 먼저 활성화 (키보드 바인딩 포함)
        self.enable_clipboard_operations(widget)

        # 차이점 복사 기능이 추가된 컨텍스트 메뉴
        context_menu = tk.Menu(widget, tearoff=0)
        key_modifier = "Cmd" if self.is_macos else "Ctrl"

        # 기본 클립보드 함수들 재정의
        def do_copy(event=None):
            try:
                widget.event_generate("<<Copy>>")
            except:
                if widget.tag_ranges('sel'):
                    widget.clipboard_clear()
                    text = widget.get('sel.first', 'sel.last')
                    widget.clipboard_append(text)
            return "break"

        def do_cut(event=None):
            try:
                widget.event_generate("<<Cut>>")
            except:
                if widget.tag_ranges('sel'):
                    widget.clipboard_clear()
                    text = widget.get('sel.first', 'sel.last')
                    widget.clipboard_append(text)
                    widget.delete('sel.first', 'sel.last')
            return "break"

        def do_paste(event=None):
            try:
                widget.event_generate("<<Paste>>")
            except:
                if widget.tag_ranges('sel'):
                    widget.delete('sel.first', 'sel.last')
                text = widget.clipboard_get()
                widget.insert('insert', text)
            return "break"

        def do_select_all(event=None):
            widget.tag_add('sel', "1.0", "end-1c")
            widget.mark_set('insert', "1.0")
            widget.see('insert')
            return 'break'

        def show_file_compare_context_menu(event):
            """파일 비교용 컨텍스트 메뉴 표시"""
            context_menu.delete(0, tk.END)

            # 기본 클립보드 작업
            context_menu.add_command(label=f"복사 ({key_modifier}+C)", command=do_copy)
            context_menu.add_command(label=f"잘라내기 ({key_modifier}+X)", command=do_cut)
            context_menu.add_command(label=f"붙여넣기 ({key_modifier}+V)", command=do_paste)
            context_menu.add_separator()
            context_menu.add_command(label=f"전체 선택 ({key_modifier}+A)", command=do_select_all)

            # 차이점이 있을 때만 복사 메뉴 추가
            if len(self.file_diff_blocks) > 0:
                context_menu.add_separator()
                if is_left:
                    context_menu.add_command(label="◀ 왼쪽으로 복사 (현재 블록)",
                                           command=self.copy_diff_to_left)
                    context_menu.add_command(label="오른쪽으로 복사 ▶ (현재 블록)",
                                           command=self.copy_diff_to_right)
                else:
                    context_menu.add_command(label="◀ 왼쪽으로 복사 (현재 블록)",
                                           command=self.copy_diff_to_left)
                    context_menu.add_command(label="오른쪽으로 복사 ▶ (현재 블록)",
                                           command=self.copy_diff_to_right)

            try:
                context_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                context_menu.grab_release()

        # 우클릭 이벤트 바인딩 (기존 바인딩 덮어쓰기)
        # enable_clipboard_operations에서 이미 바인딩했으므로, 이를 제거하고 새로 바인딩
        widget.unbind('<Button-3>')
        widget.bind('<Button-3>', show_file_compare_context_menu)
        if self.is_macos:
            widget.unbind('<Button-2>')
            widget.unbind('<Control-Button-1>')
            widget.bind('<Button-2>', show_file_compare_context_menu)
            widget.bind('<Control-Button-1>', show_file_compare_context_menu)

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
            raw_name = self._folder_tree_raw_names.get(current)
            if raw_name is None:
                raw_name = self._clean_folder_tree_text(self.folder_tree.item(current, 'text'))
            path_parts.insert(0, raw_name)
            current = self.folder_tree.parent(current)

        return os.path.join(*path_parts) if path_parts else ""

    def get_all_files_from_tree_item(self, item):
        """트리 아이템(폴더 포함)에서 모든 파일 아이템을 재귀적으로 가져오기"""
        file_items = []

        # 현재 아이템이 파일인지 폴더인지 확인
        item_values = self.folder_tree.item(item, 'values')

        if item_values and item_values[0]:  # 상태가 있으면 파일
            file_items.append(item)
        else:  # 폴더인 경우
            # 자식 아이템들을 재귀적으로 처리
            children = self.folder_tree.get_children(item)
            for child in children:
                file_items.extend(self.get_all_files_from_tree_item(child))

        return file_items

    def browse_folder(self, var, entry_widget=None):
        """폴더 선택 대화상자"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
            # Entry의 끝으로 스크롤하여 폴더명이 보이도록 함
            if entry_widget:
                entry_widget.xview_moveto(1.0)

    def browse_file(self, var, entry_widget=None):
        """파일 선택 대화상자"""
        file = filedialog.askopenfilename()
        if file:
            var.set(file)
            # Entry의 끝으로 스크롤하여 파일명이 보이도록 함
            if entry_widget:
                entry_widget.xview_moveto(1.0)

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

    def should_exclude(self, rel_path, patterns):
        """제외 패턴에 매칭되는지 확인"""
        if not patterns:
            return False

        # 경로를 정규화 (슬래시로 통일)
        normalized_path = rel_path.replace(os.sep, '/')

        for pattern in patterns:
            # 패턴도 슬래시로 통일
            normalized_pattern = pattern.replace(os.sep, '/')

            # 폴더 패턴 (끝에 /가 있는 경우)
            if normalized_pattern.endswith('/'):
                # 폴더 이름이나 경로가 매칭되는지 확인
                folder_pattern = normalized_pattern.rstrip('/')
                # 경로의 일부분이 폴더 패턴과 매칭되는지 확인
                path_parts = normalized_path.split('/')
                for part in path_parts[:-1]:  # 마지막 부분(파일명)을 제외한 모든 폴더
                    if fnmatch.fnmatch(part, folder_pattern):
                        return True
                # 전체 경로가 폴더 패턴으로 시작하는지 확인
                if normalized_path.startswith(folder_pattern + '/'):
                    return True
            else:
                # 파일 패턴
                # 전체 경로 매칭
                if fnmatch.fnmatch(normalized_path, normalized_pattern):
                    return True
                # 파일 이름만 매칭
                filename = os.path.basename(normalized_path)
                if fnmatch.fnmatch(filename, normalized_pattern):
                    return True
                # 경로의 일부분이 매칭되는지 확인
                path_parts = normalized_path.split('/')
                for part in path_parts:
                    if fnmatch.fnmatch(part, normalized_pattern):
                        return True

        return False

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
        self._folder_tree_raw_names.clear()

        compare_method = self.compare_method_var.get()

        # 제외 패턴 가져오기
        exclude_patterns = self.data_manager.get_exclude_patterns()

        # 파일 목록 수집
        left_files = {}
        right_files = {}
        excluded_files = set()  # 제외된 파일의 고유 경로 추적

        for root, dirs, files in os.walk(left_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, left_folder)

                # 제외 패턴 확인
                if self.should_exclude(rel_path, exclude_patterns):
                    excluded_files.add(rel_path)
                    continue

                left_files[rel_path] = full_path

        for root, dirs, files in os.walk(right_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, right_folder)

                # 제외 패턴 확인
                if self.should_exclude(rel_path, exclude_patterns):
                    excluded_files.add(rel_path)
                    continue

                right_files[rel_path] = full_path

        # 모든 파일 경로 합치기
        all_paths = set(left_files.keys()) | set(right_files.keys())

        # 트리 구조를 위한 딕셔너리 (폴더 경로 -> 트리 아이템 ID)
        folder_nodes = {}
        folder_stats = {}
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
                status_tag, status_icon = self._get_folder_status_visual(status)
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
                    count_key = self._get_folder_diff_count_key(status)

                    # 폴더 경로 생성 + 자손 stats 누적
                    for i, part in enumerate(path_parts[:-1]):
                        if cumulative_path:
                            cumulative_path = os.path.join(cumulative_path, part)
                        else:
                            cumulative_path = part

                        # 폴더 노드가 없으면 생성
                        if cumulative_path not in folder_nodes:
                            folder_nodes[cumulative_path] = self.folder_tree.insert(
                                parent_id, 'end', text=f"📁 {part}",
                                values=('', '', '', '', ''), open=True, tags=('folder',)
                            )
                            self._folder_tree_raw_names[folder_nodes[cumulative_path]] = part
                        parent_id = folder_nodes[cumulative_path]

                        if count_key:
                            bucket = folder_stats.setdefault(cumulative_path, {
                                'differ': 0, 'left_only': 0, 'right_only': 0, 'newer': 0
                            })
                            bucket[count_key] += 1

                    # 파일을 폴더 노드 아래에 추가
                    file_name = path_parts[-1]
                    file_item = self.folder_tree.insert(
                        parent_id, 'end', text=f"{status_icon}{file_name}",
                        values=(status, left_size, left_mtime, right_size, right_mtime),
                        tags=(status_tag,) if status_tag else ()
                    )
                    self._folder_tree_raw_names[file_item] = file_name
                else:
                    # 루트에 있는 파일
                    file_item = self.folder_tree.insert(
                        '', 'end', text=f"{status_icon}{rel_path}",
                        values=(status, left_size, left_mtime, right_size, right_mtime),
                        tags=(status_tag,) if status_tag else ()
                    )
                    self._folder_tree_raw_names[file_item] = rel_path

        # 폴더 노드에 자손 diff 카운트 배지 적용
        self._annotate_folder_diff_counts(folder_nodes, folder_stats)

        # 완료 메시지
        message = f"비교가 완료되었습니다.\n차이가 있는 파일: {diff_count}개"
        if len(excluded_files) > 0:
            message += f"\n제외된 파일: {len(excluded_files)}개"
        messagebox.showinfo("완료", message)

    def copy_file(self, direction):
        """파일 복사 (폴더 선택 시 하위 모든 파일 복사)"""
        selected = self.folder_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "복사할 파일 또는 폴더를 선택해주세요.")
            return

        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        copied_count = 0
        error_count = 0
        error_messages = []

        # 선택된 모든 항목에서 파일 수집 (폴더인 경우 하위 파일 모두 수집)
        all_file_items = []
        for item in selected:
            files = self.get_all_files_from_tree_item(item)
            all_file_items.extend(files)

        # 중복 제거
        all_file_items = list(set(all_file_items))

        if not all_file_items:
            messagebox.showwarning("경고", "복사할 파일이 없습니다.")
            return

        # 확인 메시지
        if len(all_file_items) > 1:
            direction_text = "왼쪽에서 오른쪽으로" if direction == 'left_to_right' else "오른쪽에서 왼쪽으로"
            if not messagebox.askyesno("확인", f"{len(all_file_items)}개의 파일을 {direction_text} 복사하시겠습니까?"):
                return

        # 파일 복사
        for item in all_file_items:
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
                error_messages.append(f"{rel_path}: {str(e)}")

        # 결과 메시지
        result_msg = f"{copied_count}개 파일이 복사되었습니다."
        if error_count > 0:
            result_msg += f"\n{error_count}개 파일 복사 실패."
            if len(error_messages) <= 5:
                result_msg += "\n\n실패한 파일:\n" + "\n".join(error_messages)
            else:
                result_msg += "\n\n실패한 파일:\n" + "\n".join(error_messages[:5]) + f"\n... 외 {len(error_messages)-5}개"

        if copied_count > 0:
            messagebox.showinfo("완료", result_msg)
            # 비교 다시 실행
            self.compare_folders()
        elif error_count > 0:
            messagebox.showerror("오류", result_msg)

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

    def show_folder_tree_context_menu(self, event):
        """폴더 트리 우클릭 시 컨텍스트 메뉴 표시"""
        # 우클릭한 위치의 아이템 식별
        item = self.folder_tree.identify_row(event.y)

        # 아이템이 있으면 선택하고 메뉴 표시
        if item:
            # 이미 선택된 항목이 아니면 선택
            if item not in self.folder_tree.selection():
                self.folder_tree.selection_set(item)

        # 선택된 항목이 있을 때만 메뉴 표시
        if self.folder_tree.selection():
            try:
                self.folder_tree_context_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.folder_tree_context_menu.grab_release()

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
        self._clear_diff_highlights(self.folder_preview_left)
        self._clear_diff_highlights(self.folder_preview_right)

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

    def _add_diff_line_background(self, text_widget, tag_name, start_line_index, end_line_index):
        """0-based line slice 범위에 hunk 단위 배경 태그를 추가."""
        for line_index in range(start_line_index, end_line_index):
            line_num = line_index + 1
            text_widget.tag_add(tag_name, f"{line_num}.0", f"{line_num + 1}.0")

    def _clear_diff_highlights(self, text_widget):
        """문자 diff와 hunk line-bg 태그를 함께 제거."""
        for tag_name in (
            'diff',
            'diff_line_left_only',
            'diff_line_right_only',
            'diff_line_replace',
        ):
            text_widget.tag_remove(tag_name, '1.0', 'end')

    def compare_text_detailed(self, left_widget, right_widget, left_lines, right_lines, store_blocks=False, blocks_list=None):
        """문자 단위로 상세 비교하여 하이라이트

        Args:
            left_widget: 왼쪽 텍스트 위젯
            right_widget: 오른쪽 텍스트 위젯
            left_lines: 왼쪽 텍스트 라인 리스트
            right_lines: 오른쪽 텍스트 라인 리스트
            store_blocks: 차이점 블록 정보를 저장할지 여부
            blocks_list: 블록 정보를 저장할 리스트
        """
        # 블록 정보 저장이 필요한 경우 초기화
        if store_blocks and blocks_list is not None:
            blocks_list.clear()

        # 라인 단위 비교
        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue

            # 블록 정보 저장
            if store_blocks and blocks_list is not None:
                block_info = {
                    'tag': tag,
                    'left_start': i1 + 1,  # 1-based line number
                    'left_end': i2,         # exclusive
                    'right_start': j1 + 1,  # 1-based line number
                    'right_end': j2,        # exclusive
                    'left_lines': left_lines[i1:i2],
                    'right_lines': right_lines[j1:j2]
                }
                blocks_list.append(block_info)

            if tag == 'delete':
                # 왼쪽에만 있는 라인들
                self._add_diff_line_background(left_widget, 'diff_line_left_only', i1, i2)
                for i in range(i1, i2):
                    self.highlight_text_diff(left_widget, left_lines[i], i+1, 0, len(left_lines[i]))
            elif tag == 'insert':
                # 오른쪽에만 있는 라인들
                self._add_diff_line_background(right_widget, 'diff_line_right_only', j1, j2)
                for j in range(j1, j2):
                    self.highlight_text_diff(right_widget, right_lines[j], j+1, 0, len(right_lines[j]))
            elif tag == 'replace':
                # 변경된 라인들 - 문자 단위로 상세 비교
                left_block = left_lines[i1:i2]
                right_block = right_lines[j1:j2]
                self._add_diff_line_background(left_widget, 'diff_line_replace', i1, i2)
                self._add_diff_line_background(right_widget, 'diff_line_replace', j1, j2)

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
        self._clear_diff_highlights(self.text_left)
        self._clear_diff_highlights(self.text_right)

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
        self._clear_diff_highlights(self.text_left)
        self._clear_diff_highlights(self.text_right)

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
        self._clear_diff_highlights(self.file_text_left)
        self._clear_diff_highlights(self.file_text_right)
        self.status_label_left.config(text="1:1")
        self.status_label_right.config(text="1:1")

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
            self._clear_diff_highlights(self.file_text_left)
            self._clear_diff_highlights(self.file_text_right)

            # 차이점 하이라이트 (문자 단위 상세 비교) 및 블록 정보 저장
            left_lines = left_content.splitlines()
            right_lines = right_content.splitlines()

            self.compare_text_detailed(self.file_text_left, self.file_text_right, left_lines, right_lines,
                                      store_blocks=True, blocks_list=self.file_diff_blocks)
            self._update_file_status(self.file_text_left, self.file_status_left)
            self._update_file_status(self.file_text_right, self.file_status_right)

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

    def _bind_file_status_events(self, widget, label, side):
        """파일 비교 텍스트 위젯의 라인:컬럼 status bar 이벤트 바인딩"""
        def update_status(event=None):
            self._update_file_status(widget, label)
            self._last_active_file_side = side
            return None

        widget.bind('<KeyRelease>', update_status, add='+')
        widget.bind('<ButtonRelease-1>', update_status, add='+')
        widget.bind('<<Selection>>', update_status, add='+')
        widget.bind('<FocusIn>', update_status, add='+')

    def _update_file_status(self, widget, label):
        """텍스트 위젯의 현재 커서 위치를 status label에 갱신"""
        try:
            idx = widget.index('insert')
            line, col = idx.split('.')
            col = int(col) + 1  # 1-based for display
            label.config(text=f"{line}:{col}")
        except Exception:
            pass

    def _active_file_widget(self):
        """파일 비교 탭에서 현재 활성 위젯/사이드 판별

        Returns:
            (widget, side) — side는 'left' 또는 'right'
        """
        focused = None
        try:
            focused = self.root.focus_get()
        except Exception:
            focused = None

        if focused is self.file_text_left:
            return self.file_text_left, 'left'
        if focused is self.file_text_right:
            return self.file_text_right, 'right'

        side = getattr(self, '_last_active_file_side', 'left')
        if side == 'right':
            return self.file_text_right, 'right'
        return self.file_text_left, 'left'

    def goto_prev_diff(self):
        """현재 활성 위젯에서 커서보다 위에 있는 diff 블록의 시작 라인으로 점프"""
        if not self.file_diff_blocks:
            return
        widget, side = self._active_file_widget()
        try:
            cur_idx = widget.index('insert')
            cur_line = int(cur_idx.split('.')[0])
        except Exception:
            cur_line = 1

        key = 'left_start' if side == 'left' else 'right_start'
        target = None
        for block in self.file_diff_blocks:
            start = block.get(key)
            if start is None:
                continue
            if start < cur_line:
                if target is None or start > target:
                    target = start
        if target is None:
            return
        self._jump_to_diff_line(widget, target)

    def goto_next_diff(self):
        """현재 활성 위젯에서 커서보다 아래에 있는 diff 블록의 시작 라인으로 점프"""
        if not self.file_diff_blocks:
            return
        widget, side = self._active_file_widget()
        try:
            cur_idx = widget.index('insert')
            cur_line = int(cur_idx.split('.')[0])
        except Exception:
            cur_line = 1

        key = 'left_start' if side == 'left' else 'right_start'
        target = None
        for block in self.file_diff_blocks:
            start = block.get(key)
            if start is None:
                continue
            if start > cur_line:
                if target is None or start < target:
                    target = start
        if target is None:
            return
        self._jump_to_diff_line(widget, target)

    def _jump_to_diff_line(self, widget, line):
        """텍스트 위젯의 특정 라인으로 커서 이동 및 view 스크롤"""
        try:
            pos = f"{int(line)}.0"
            widget.mark_set('insert', pos)
            widget.see(pos)
            widget.focus_set()
            if widget is self.file_text_left:
                self._update_file_status(widget, self.file_status_left)
                self._last_active_file_side = 'left'
            elif widget is self.file_text_right:
                self._update_file_status(widget, self.file_status_right)
                self._last_active_file_side = 'right'
        except Exception:
            pass

    def find_diff_block_at_cursor(self, widget, blocks_list):
        """커서 위치에서 차이점 블록 찾기

        Args:
            widget: 텍스트 위젯 (file_text_left 또는 file_text_right)
            blocks_list: 차이점 블록 리스트 (file_diff_blocks 또는 text_diff_blocks)

        Returns:
            찾은 블록 정보 딕셔너리, 없으면 None
        """
        # 현재 커서 위치 가져오기
        cursor_pos = widget.index('insert')
        line_num = int(cursor_pos.split('.')[0])

        # 왼쪽인지 오른쪽인지 확인
        is_left = (widget == self.file_text_left or widget == self.text_left)

        # 해당 라인이 포함된 블록 찾기
        for block in blocks_list:
            if is_left:
                if block['left_start'] <= line_num < block['left_start'] + len(block['left_lines']):
                    return block
            else:
                if block['right_start'] <= line_num < block['right_start'] + len(block['right_lines']):
                    return block

        return None

    def copy_diff_to_right(self):
        """현재 커서 위치의 차이점 블록을 왼쪽에서 오른쪽으로 복사"""
        block = self.find_diff_block_at_cursor(self.file_text_left, self.file_diff_blocks)

        if not block:
            messagebox.showwarning("알림", "커서가 차이점 블록 위에 있지 않습니다.")
            return

        # 오른쪽 텍스트에서 해당 블록 범위 삭제 후 왼쪽 내용 삽입
        left_content = '\n'.join(block['left_lines'])

        # 오른쪽에서 해당 라인 범위 찾기
        if block['tag'] == 'delete':
            # 왼쪽에만 있는 경우 - 오른쪽의 해당 위치에 삽입
            insert_pos = f"{block['right_start']}.0"
            self.file_text_right.insert(insert_pos, left_content + '\n')
        elif block['tag'] == 'insert':
            # 오른쪽에만 있는 경우 - 오른쪽 블록 삭제
            start_pos = f"{block['right_start']}.0"
            end_pos = f"{block['right_start'] + len(block['right_lines'])}.0"
            self.file_text_right.delete(start_pos, end_pos)
        else:  # replace
            # 양쪽 모두 있는 경우 - 오른쪽 내용을 왼쪽 내용으로 교체
            start_pos = f"{block['right_start']}.0"
            end_pos = f"{block['right_start'] + len(block['right_lines'])}.0"
            self.file_text_right.delete(start_pos, end_pos)
            self.file_text_right.insert(start_pos, left_content + '\n')

        # 비교 재실행 (하이라이트 업데이트)
        self.recompare_files()

    def copy_diff_to_left(self):
        """현재 커서 위치의 차이점 블록을 오른쪽에서 왼쪽으로 복사"""
        block = self.find_diff_block_at_cursor(self.file_text_right, self.file_diff_blocks)

        if not block:
            messagebox.showwarning("알림", "커서가 차이점 블록 위에 있지 않습니다.")
            return

        # 왼쪽 텍스트에서 해당 블록 범위 삭제 후 오른쪽 내용 삽입
        right_content = '\n'.join(block['right_lines'])

        # 왼쪽에서 해당 라인 범위 찾기
        if block['tag'] == 'insert':
            # 오른쪽에만 있는 경우 - 왼쪽의 해당 위치에 삽입
            insert_pos = f"{block['left_start']}.0"
            self.file_text_left.insert(insert_pos, right_content + '\n')
        elif block['tag'] == 'delete':
            # 왼쪽에만 있는 경우 - 왼쪽 블록 삭제
            start_pos = f"{block['left_start']}.0"
            end_pos = f"{block['left_start'] + len(block['left_lines'])}.0"
            self.file_text_left.delete(start_pos, end_pos)
        else:  # replace
            # 양쪽 모두 있는 경우 - 왼쪽 내용을 오른쪽 내용으로 교체
            start_pos = f"{block['left_start']}.0"
            end_pos = f"{block['left_start'] + len(block['left_lines'])}.0"
            self.file_text_left.delete(start_pos, end_pos)
            self.file_text_left.insert(start_pos, right_content + '\n')

        # 비교 재실행 (하이라이트 업데이트)
        self.recompare_files()

    def recompare_files(self):
        """파일 비교 재실행 (하이라이트 업데이트용)"""
        # 태그 제거
        self._clear_diff_highlights(self.file_text_left)
        self._clear_diff_highlights(self.file_text_right)

        # 현재 내용 가져오기
        left_content = self.file_text_left.get('1.0', 'end-1c')
        right_content = self.file_text_right.get('1.0', 'end-1c')

        # 차이점 하이라이트 및 블록 정보 업데이트
        left_lines = left_content.splitlines()
        right_lines = right_content.splitlines()

        self.compare_text_detailed(self.file_text_left, self.file_text_right, left_lines, right_lines,
                                  store_blocks=True, blocks_list=self.file_diff_blocks)
        self._update_file_status(self.file_text_left, self.file_status_left)
        self._update_file_status(self.file_text_right, self.file_status_right)

    def copy_all_to_right(self):
        """왼쪽 파일 전체 내용으로 오른쪽 파일 덮어쓰기"""
        # 확인 메시지
        result = messagebox.askyesno("확인",
                                     "오른쪽 파일 내용을 왼쪽 파일 내용으로 완전히 덮어쓰시겠습니까?\n"
                                     "이 작업은 저장 전까지 취소할 수 있습니다.")
        if not result:
            return

        # 왼쪽 전체 내용 가져오기
        left_content = self.file_text_left.get('1.0', 'end-1c')

        # 오른쪽 내용 덮어쓰기
        self.file_text_right.delete('1.0', 'end')
        self.file_text_right.insert('1.0', left_content)

        # 비교 재실행 (하이라이트 업데이트)
        self.recompare_files()

        messagebox.showinfo("완료", "왼쪽 파일 내용으로 오른쪽 파일을 덮어썼습니다.")

    def copy_all_to_left(self):
        """오른쪽 파일 전체 내용으로 왼쪽 파일 덮어쓰기"""
        # 확인 메시지
        result = messagebox.askyesno("확인",
                                     "왼쪽 파일 내용을 오른쪽 파일 내용으로 완전히 덮어쓰시겠습니까?\n"
                                     "이 작업은 저장 전까지 취소할 수 있습니다.")
        if not result:
            return

        # 오른쪽 전체 내용 가져오기
        right_content = self.file_text_right.get('1.0', 'end-1c')

        # 왼쪽 내용 덮어쓰기
        self.file_text_left.delete('1.0', 'end')
        self.file_text_left.insert('1.0', right_content)

        # 비교 재실행 (하이라이트 업데이트)
        self.recompare_files()

        messagebox.showinfo("완료", "오른쪽 파일 내용으로 왼쪽 파일을 덮어썼습니다.")

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

    def _resolve_history_items(self, category, data_type):
        """카테고리/타입에 해당하는 최신 데이터 가져오기"""
        if category == 'folder':
            return (self.data_manager.get_folder_history() if data_type == 'history'
                    else self.data_manager.get_folder_favorites())
        if category == 'file':
            return (self.data_manager.get_file_history() if data_type == 'history'
                    else self.data_manager.get_file_favorites())
        return (self.data_manager.get_text_history() if data_type == 'history'
                else self.data_manager.get_text_favorites())

    def _history_item_title(self, item, data_type):
        """항목의 #0 컬럼 표시 텍스트 (이름 또는 시각)"""
        icon = '⭐' if data_type == 'favorite' else '📅'
        primary = item.get('name') if data_type == 'favorite' else item.get('timestamp', '')
        return f"{icon}  {primary or ''}"

    def _history_item_values(self, item, category):
        """카테고리별 Treeview 컬럼 값"""
        if category == 'folder':
            return (item.get('left', ''), item.get('right', ''), item.get('method', ''))
        if category == 'file':
            return (item.get('left', ''), item.get('right', ''))
        left = (item.get('left_preview') or '').replace('\n', ' ')[:60]
        right = (item.get('right_preview') or '').replace('\n', ' ')[:60]
        return (left, right)

    def _history_columns_spec(self, category):
        """카테고리별 (columns tuple, headings dict, widths dict)"""
        if category == 'folder':
            return (('left', 'right', 'method'),
                    {'left': '왼쪽 폴더', 'right': '오른쪽 폴더', 'method': '비교 방법'},
                    {'left': 280, 'right': 280, 'method': 100})
        if category == 'file':
            return (('left', 'right'),
                    {'left': '왼쪽 파일', 'right': '오른쪽 파일'},
                    {'left': 340, 'right': 340})
        return (('left_preview', 'right_preview'),
                {'left_preview': '왼쪽 미리보기', 'right_preview': '오른쪽 미리보기'},
                {'left_preview': 340, 'right_preview': 340})

    def _build_history_tree(self, parent, category, data_type):
        """Treeview + 수직 스크롤바를 감싼 컨테이너 생성. (container, tree) 반환."""
        columns, headings, widths = self._history_columns_spec(category)

        container = ttk.Frame(parent)

        scrollbar = ttk.Scrollbar(container, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        tree = ttk.Treeview(container, columns=columns, show='tree headings',
                            height=14, selectmode='browse',
                            yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)

        head_text = '이름' if data_type == 'favorite' else '시각'
        tree.heading('#0', text=head_text, anchor='w')
        tree.column('#0', width=240, minwidth=140, anchor='w', stretch=False)
        for col in columns:
            tree.heading(col, text=headings[col], anchor='w')
            tree.column(col, width=widths[col], minwidth=120, anchor='w', stretch=True)

        tree.tag_configure('favorite', background=NOTION_COLORS['lavender'],
                           foreground=NOTION_COLORS['purple_ink'])
        tree.tag_configure('history', background=NOTION_COLORS['canvas'],
                           foreground=NOTION_COLORS['ink'])

        return container, tree

    def _populate_history_tree(self, tree, items, category, data_type, search_text=''):
        """현재 items를 Treeview에 채움. 검색 필터 적용. iid는 원본 index 문자열.
        반환: (total, visible)"""
        tree.delete(*tree.get_children())
        needle = (search_text or '').strip().lower()
        tag = 'favorite' if data_type == 'favorite' else 'history'

        visible = 0
        for idx, item in enumerate(items):
            title = self._history_item_title(item, data_type)
            values = self._history_item_values(item, category)
            haystack = ' '.join([title] + [str(v) for v in values]).lower()
            if needle and needle not in haystack:
                continue
            tree.insert('', 'end', iid=str(idx), text=title,
                        values=values, tags=(tag,))
            visible += 1

        return len(items), visible

    def _open_rename_dialog(self, parent_win, current_name):
        """이름 변경용 작은 자식 모달. 확정 시 새 이름 문자열, 취소 시 None 반환."""
        result = {'value': None}
        dialog = tk.Toplevel(parent_win)
        dialog.title("이름 변경")
        dialog.transient(parent_win)
        dialog.resizable(False, False)
        try:
            dialog.configure(bg=NOTION_COLORS['surface'])
        except tk.TclError:
            pass

        body = ttk.Frame(dialog, padding=(20, 18, 20, 16))
        body.pack(fill='both', expand=True)

        ui_font = resolve_ui_font(dialog)
        ttk.Label(body, text="새 이름을 입력하세요",
                  font=(ui_font, 13, 'bold'),
                  foreground=NOTION_COLORS['ink']).pack(anchor='w', pady=(0, 10))

        entry_var = tk.StringVar(value=current_name or '')
        entry = ttk.Entry(body, textvariable=entry_var, width=36)
        entry.pack(fill='x', pady=(0, 14))

        def on_ok(event=None):
            new_name = entry_var.get().strip()
            if not new_name:
                return "break"
            result['value'] = new_name
            dialog.destroy()
            return "break"

        def on_cancel(event=None):
            dialog.destroy()
            return "break"

        action_row = ttk.Frame(body)
        action_row.pack(fill='x')
        build_button_row(action_row, [
            {'label': '취소', 'command': on_cancel, 'role': 'ghost'},
            {'label': '확인', 'icon': '✓', 'command': on_ok, 'role': 'primary'},
        ], align='right', pady=(0, 0))

        entry.bind('<Return>', on_ok)
        entry.bind('<Escape>', on_cancel)
        dialog.bind('<Return>', on_ok)
        dialog.bind('<Escape>', on_cancel)
        dialog.protocol('WM_DELETE_WINDOW', on_cancel)

        dialog.update_idletasks()
        try:
            pw = max(parent_win.winfo_width(), 1)
            ph = max(parent_win.winfo_height(), 1)
            dw = dialog.winfo_width()
            dh = dialog.winfo_height()
            px = parent_win.winfo_rootx() + (pw - dw) // 2
            py = parent_win.winfo_rooty() + (ph - dh) // 2
            dialog.geometry(f"+{max(px, 20)}+{max(py, 20)}")
        except tk.TclError:
            pass

        dialog.grab_set()
        entry.focus_set()
        entry.select_range(0, 'end')
        parent_win.wait_window(dialog)

        # child grab 종료 후 parent grab 복원 (modal 유지)
        try:
            parent_win.grab_set()
        except tk.TclError:
            pass

        return result['value']

    def _build_history_listing_dialog(self, category, data_type, mode):
        """히스토리/즐겨찾기 다이얼로그 공통 구현.

        mode: 'select' (불러오기 다이얼로그) | 'manage' (관리 다이얼로그)
        """
        is_favorite = (data_type == 'favorite')
        category_label = {'folder': '폴더 비교',
                          'file': '파일 비교',
                          'text': '텍스트 비교'}[category]
        kind_icon = '⭐' if is_favorite else '📜'
        kind_label = '즐겨찾기' if is_favorite else '히스토리'

        win = tk.Toplevel(self.root)
        win.title(f"{kind_icon} {kind_label} — {category_label}")
        win.geometry("980x560")
        win.minsize(720, 420)
        win.resizable(True, True)
        try:
            win.configure(bg=NOTION_COLORS['surface'])
        except tk.TclError:
            pass
        win.transient(self.root)

        container = ttk.Frame(win, padding=(20, 18, 20, 16))
        container.pack(fill='both', expand=True)

        ui_font = resolve_ui_font(win)

        # 헤더
        header = ttk.Frame(container)
        header.pack(fill='x', pady=(0, 14))
        ttk.Label(header,
                  text=f"{kind_icon}  {kind_label} — {category_label}",
                  font=(ui_font, 19, 'bold'),
                  foreground=NOTION_COLORS['ink']).pack(anchor='w')

        count_var = tk.StringVar()
        ttk.Label(header, textvariable=count_var,
                  font=(ui_font, 13),
                  foreground=NOTION_COLORS['slate']).pack(anchor='w', pady=(4, 0))

        # 검색바 (placeholder 포함)
        search_var = tk.StringVar()
        search_row = ttk.Frame(container)
        search_row.pack(fill='x', pady=(0, 12))
        ttk.Label(search_row, text='🔍',
                  font=(ui_font, 14),
                  foreground=NOTION_COLORS['slate']).pack(side='left', padx=(0, 8))
        search_entry = ttk.Entry(search_row, textvariable=search_var,
                                 foreground=NOTION_COLORS['ink'])
        search_entry.pack(side='left', fill='x', expand=True)

        placeholder = '검색...'
        placeholder_state = {'shown': False}

        def show_placeholder():
            if not search_var.get():
                placeholder_state['shown'] = True
                search_entry.configure(foreground=NOTION_COLORS['slate'])
                search_entry.insert(0, placeholder)

        def hide_placeholder():
            if placeholder_state['shown']:
                placeholder_state['shown'] = False
                search_entry.delete(0, 'end')
                search_entry.configure(foreground=NOTION_COLORS['ink'])

        def on_search_focus_in(event=None):
            hide_placeholder()

        def on_search_focus_out(event=None):
            if not search_var.get().strip():
                show_placeholder()

        search_entry.bind('<FocusIn>', on_search_focus_in)
        search_entry.bind('<FocusOut>', on_search_focus_out)

        # 본문 (Treeview 또는 빈 상태)
        body = ttk.Frame(container)
        body.pack(fill='both', expand=True)

        empty_label = ttk.Label(body, text='',
                                font=(ui_font, 14),
                                foreground=NOTION_COLORS['slate'],
                                anchor='center', justify='center')

        tree_container, tree = self._build_history_tree(body, category, data_type)
        tree_container.pack(fill='both', expand=True)

        # 하단 hairline + 액션 영역
        divider = tk.Frame(container, height=1,
                           bg=NOTION_COLORS['hairline'],
                           highlightthickness=0, bd=0)
        divider.pack(fill='x', pady=(14, 12))

        action_frame = ttk.Frame(container)
        action_frame.pack(fill='x')

        # 데이터 채우기 및 빈 상태 처리
        state = {'items': []}

        def refresh():
            current_items = self._resolve_history_items(category, data_type)
            state['items'] = current_items
            effective_search = '' if placeholder_state['shown'] else search_var.get()
            total, visible = self._populate_history_tree(
                tree, current_items, category, data_type, effective_search
            )
            searching = bool(effective_search.strip())
            if searching:
                count_var.set(f"총 {total}개 · 검색 결과 {visible}개")
            else:
                count_var.set(f"총 {total}개")

            tree_container.pack_forget()
            empty_label.pack_forget()
            if total == 0:
                empty_label.config(text="아직 항목이 없습니다.\n비교를 실행하거나 즐겨찾기를 추가해 보세요.")
                empty_label.pack(fill='both', expand=True, pady=40)
            elif visible == 0:
                empty_label.config(text="검색 결과가 없습니다.\n다른 키워드로 시도해 보세요.")
                empty_label.pack(fill='both', expand=True, pady=40)
            else:
                tree_container.pack(fill='both', expand=True)

        def get_selected_index():
            selection = tree.selection()
            if not selection:
                return None
            try:
                return int(selection[0])
            except (TypeError, ValueError):
                return None

        def do_load(event=None):
            idx = get_selected_index()
            if idx is None:
                messagebox.showwarning("경고", "항목을 선택해주세요.", parent=win)
                return "break"
            items = state['items']
            if idx < 0 or idx >= len(items):
                refresh()
                return "break"
            item = items[idx]
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
                self.text_left.insert('1.0', item.get('left_text', ''))
                self.text_right.insert('1.0', item.get('right_text', ''))

            win.destroy()
            messagebox.showinfo("완료", "불러오기 완료!")
            return "break"

        def do_delete(event=None):
            idx = get_selected_index()
            if idx is None:
                messagebox.showwarning("경고", "삭제할 항목을 선택해주세요.", parent=win)
                return "break"
            items = state['items']
            if idx < 0 or idx >= len(items):
                refresh()
                return "break"
            if not messagebox.askyesno("확인", "선택한 항목을 삭제하시겠습니까?", parent=win):
                return "break"
            if data_type == 'history':
                self.data_manager.delete_history(category, idx)
            else:
                self.data_manager.delete_favorite(category, idx)
            refresh()
            return "break"

        def do_rename(event=None):
            if data_type != 'favorite':
                messagebox.showinfo("알림", "히스토리는 이름을 변경할 수 없습니다.", parent=win)
                return "break"
            idx = get_selected_index()
            if idx is None:
                messagebox.showwarning("경고", "이름을 변경할 항목을 선택해주세요.", parent=win)
                return "break"
            items = state['items']
            if idx < 0 or idx >= len(items):
                refresh()
                return "break"
            current_name = items[idx].get('name', '')
            new_name = self._open_rename_dialog(win, current_name)
            if new_name:
                self.data_manager.rename_favorite(category, idx, new_name)
                refresh()
            return "break"

        def on_escape(event=None):
            win.destroy()
            return "break"

        # 검색 실시간 필터
        search_var.trace_add('write', lambda *_: refresh())

        # 키 바인딩
        def on_tree_return(event=None):
            if mode == 'select':
                return do_load()
            if is_favorite:
                return do_rename()
            return "break"

        def on_tree_double(event=None):
            if mode == 'select':
                return do_load()
            if is_favorite:
                return do_rename()
            return "break"

        tree.bind('<Double-1>', on_tree_double)
        tree.bind('<Return>', on_tree_return)
        tree.bind('<Delete>', do_delete)
        win.bind('<Escape>', on_escape)
        search_entry.bind('<Return>', on_tree_return)
        search_entry.bind('<Escape>', on_escape)
        search_entry.bind('<Down>', lambda e: (tree.focus_set(),
                                                tree.selection_set(tree.get_children()[:1] or ()),
                                                "break")[-1])

        context_menu = tk.Menu(tree, tearoff=0)

        def show_history_context_menu(event):
            item_id = tree.identify_row(event.y)
            if not item_id:
                return "break"

            tree.selection_set(item_id)
            tree.focus(item_id)
            context_menu.delete(0, tk.END)

            if mode == 'select':
                context_menu.add_command(label='불러오기', command=do_load)
                context_menu.add_separator()
            elif is_favorite:
                context_menu.add_command(label='이름 변경', command=do_rename)
                context_menu.add_separator()

            context_menu.add_command(label='선택 항목 삭제', command=do_delete)
            try:
                context_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                context_menu.grab_release()
            return "break"

        tree.bind('<Button-3>', show_history_context_menu)
        tree.bind('<Button-2>', show_history_context_menu)
        tree.bind('<Control-Button-1>', show_history_context_menu)

        # 액션 버튼 구성
        delete_specs = [
            {'label': '선택 항목 삭제', 'icon': '🗑️',
             'command': do_delete, 'role': 'destructive'},
        ]
        if mode == 'select':
            right_specs = [
                {'label': '취소', 'command': win.destroy, 'role': 'ghost'},
                {'label': '불러오기', 'icon': '▶', 'command': do_load, 'role': 'primary'},
            ]
        else:  # manage
            right_specs = []
            if is_favorite:
                right_specs.append({'label': '이름 변경', 'icon': '✏️',
                                    'command': do_rename, 'role': 'secondary'})
            right_specs.append({'label': '닫기', 'command': win.destroy, 'role': 'ghost'})

        build_toolbar(action_frame, left_specs=delete_specs, right_specs=right_specs, pady=(0, 0))

        # placeholder 초기 표시 (focus_set 전에 — 첫 focus_set이 hide_placeholder 트리거)
        show_placeholder()

        refresh()

        # 부모 윈도우 기준 중앙 배치
        win.update_idletasks()
        try:
            pw = max(self.root.winfo_width(), 1)
            ph = max(self.root.winfo_height(), 1)
            ww = win.winfo_width()
            wh = win.winfo_height()
            px = self.root.winfo_rootx() + (pw - ww) // 2
            py = self.root.winfo_rooty() + (ph - wh) // 2
            win.geometry(f"+{max(px, 20)}+{max(py, 20)}")
        except tk.TclError:
            pass

        win.grab_set()
        # 첫 포커스는 Treeview의 첫 행으로 — 검색 placeholder가 사라지지 않음
        first_children = tree.get_children()
        if first_children:
            tree.focus_set()
            tree.selection_set(first_children[0])
            tree.focus(first_children[0])
        else:
            search_entry.focus_set()

    def show_selection_window(self, category, data_type, items):
        """히스토리/즐겨찾기 선택 다이얼로그 (불러오기용)."""
        self._build_history_listing_dialog(category, data_type, mode='select')

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
        """히스토리/즐겨찾기 관리 다이얼로그 (이름변경/삭제)."""
        self._build_history_listing_dialog(category, data_type, mode='manage')

    def show_font_settings(self):
        """폰트 설정 대화상자"""
        win = tk.Toplevel(self.root)
        win.title("폰트 설정")
        win.geometry("500x380")
        win.resizable(True, True)

        # 중앙에 배치
        win.transient(self.root)
        win.grab_set()

        # 메인 프레임
        main_frame = ttk.Frame(win, padding=20)
        main_frame.pack(fill='both', expand=True)

        # 설명
        ttk.Label(
            main_frame,
            text="폴더 목록 및 비교 창의 폰트를 설정합니다.",
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE)
        ).pack(pady=(0, 20))

        # 폰트 패밀리 선택
        font_family_frame = ttk.Frame(main_frame)
        font_family_frame.pack(fill='x', pady=10)

        ttk.Label(font_family_frame, text="폰트:", width=15).pack(side='left')
        font_family_var = tk.StringVar(value=self.font_family)

        # 일반적으로 사용 가능한 폰트 목록
        common_fonts = [
            'Pretendard Std', 'Pretendard', 'Inter',
            'Consolas', 'Courier New', 'Monaco', 'Menlo',
            'DejaVu Sans Mono', 'Liberation Mono', 'Source Code Pro',
            'Arial', 'Helvetica', 'Verdana', 'Tahoma', 'Segoe UI',
            'Malgun Gothic', 'Gulim', 'Dotum', 'Batang'
        ]

        font_combo = ttk.Combobox(font_family_frame, textvariable=font_family_var,
                                 values=common_fonts, width=20, state='readonly')
        font_combo.pack(side='left', padx=5)

        # 폰트 크기 선택
        font_size_frame = ttk.Frame(main_frame)
        font_size_frame.pack(fill='x', pady=10)

        ttk.Label(font_size_frame, text="크기:", width=15).pack(side='left')
        font_size_var = tk.IntVar(value=self.font_size)

        size_spinbox = ttk.Spinbox(font_size_frame, from_=8, to=20,
                                   textvariable=font_size_var, width=20)
        size_spinbox.pack(side='left', padx=5)

        # 미리보기
        preview_frame = ttk.Labelframe(main_frame, text="미리보기", padding=10)
        preview_frame.pack(fill='x', expand=False, pady=10)

        preview_text = tk.Text(preview_frame, height=3, wrap='none')
        preview_text.pack(fill='both', expand=False)
        configure_notion_text_widget(preview_text, (font_family_var.get(), font_size_var.get()))
        preview_text.insert('1.0', "The quick brown fox jumps over the lazy dog\n빠른 갈색 여우가 게으른 개를 뛰어넘습니다\n0123456789")

        def update_preview(*args):
            try:
                preview_text.config(font=(font_family_var.get(), font_size_var.get()))
            except:
                pass

        font_family_var.trace('w', update_preview)
        font_size_var.trace('w', update_preview)
        update_preview()

        # 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))

        def apply_settings():
            self.font_family = font_family_var.get()
            self.font_size = font_size_var.get()
            self.data_manager.set_font_settings(self.font_family, self.font_size)
            self.apply_fonts()
            messagebox.showinfo("완료", "폰트 설정이 적용되었습니다.")
            win.destroy()

        build_button_row(
            button_frame,
            [
                {'label': '취소', 'command': win.destroy, 'role': 'ghost'},
                {'label': '적용', 'icon': '✓', 'command': apply_settings, 'role': 'primary'},
            ],
            align='right',
            pady=(0, 0),
        )

    def apply_fonts(self):
        """모든 위젯에 폰트 적용"""
        # 폰트 튜플 생성
        normal_font = (self.font_family, self.font_size)
        bold_font = (self.font_family, self.font_size, 'bold')

        # 폴더 비교 탭의 미리보기 텍스트 위젯
        if hasattr(self, 'folder_preview_left'):
            self.folder_preview_left.config(font=normal_font)
            self.folder_preview_left.tag_config('diff', font=bold_font)

        if hasattr(self, 'folder_preview_right'):
            self.folder_preview_right.config(font=normal_font)
            self.folder_preview_right.tag_config('diff', font=bold_font)

        # 텍스트 비교 탭의 텍스트 위젯
        if hasattr(self, 'text_left'):
            self.text_left.config(font=normal_font)
            self.text_left.tag_config('diff', font=bold_font)

        if hasattr(self, 'text_right'):
            self.text_right.config(font=normal_font)
            self.text_right.tag_config('diff', font=bold_font)

        # 파일 비교 탭의 텍스트 위젯
        if hasattr(self, 'file_text_left'):
            self.file_text_left.config(font=normal_font)
            self.file_text_left.tag_config('diff', font=bold_font)

        if hasattr(self, 'file_text_right'):
            self.file_text_right.config(font=normal_font)
            self.file_text_right.tag_config('diff', font=bold_font)

    def open_exclude_patterns_dialog(self):
        """제외 패턴 설정 다이얼로그 열기"""
        dialog = tk.Toplevel(self.root)
        dialog.title("폴더 비교 제외 패턴 설정")
        dialog.geometry("800x650")

        # 상단 설명
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill='x', padx=10, pady=10)

        info_text = """제외할 파일이나 폴더 패턴을 입력하세요 (.gitignore 형식)
• 한 줄에 하나의 패턴을 입력합니다
• # 으로 시작하는 줄은 주석으로 처리됩니다
• 예시: node_modules/, *.pyc, __pycache__/, .git/, *.log"""

        ttk.Label(
            info_frame,
            text=info_text,
            font=(self.font_family, DEFAULT_TEXT_FONT_SIZE - 2),
            justify='left'
        ).pack(anchor='w')

        # 텍스트 영역
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(text_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        text_widget = tk.Text(text_frame, wrap='none', yscrollcommand=scrollbar.set,
                              font=(self.font_family, self.font_size))
        text_widget.pack(fill='both', expand=True)
        configure_notion_text_widget(text_widget, (self.font_family, self.font_size))
        scrollbar.config(command=text_widget.yview)

        # 기존 패턴 로드
        patterns = self.data_manager.get_exclude_patterns()
        if patterns:
            text_widget.insert('1.0', '\n'.join(patterns))
        else:
            # 기본 패턴 예시
            default_patterns = [
                "# 일반적으로 제외되는 폴더/파일 예시",
                "# node_modules/",
                "# .git/",
                "# __pycache__/",
                "# *.pyc",
                "# .DS_Store",
                "# Thumbs.db"
            ]
            text_widget.insert('1.0', '\n'.join(default_patterns))

        # 버튼 영역
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)

        def save_patterns():
            """패턴 저장"""
            content = text_widget.get('1.0', 'end-1c')
            lines = content.split('\n')

            # 빈 줄과 주석 제거, 앞뒤 공백 제거
            patterns = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)

            self.data_manager.set_exclude_patterns(patterns)
            messagebox.showinfo("성공", f"{len(patterns)}개의 제외 패턴이 저장되었습니다.")
            dialog.destroy()

        def clear_patterns():
            """패턴 초기화"""
            if messagebox.askyesno("확인", "모든 제외 패턴을 삭제하시겠습니까?"):
                text_widget.delete('1.0', 'end')

        build_button_row(
            button_frame,
            [
                {'label': '취소', 'command': dialog.destroy, 'role': 'ghost'},
                {'label': '초기화', 'icon': '↻', 'command': clear_patterns, 'role': 'secondary'},
                {'label': '저장', 'icon': '💾', 'command': save_patterns, 'role': 'primary'},
            ],
            align='right',
            pady=(0, 0),
        )

        # 다이얼로그를 모달로 만들기
        dialog.transient(self.root)
        dialog.grab_set()


def main():
    # ttkbootstrap Window with minty base and Notion visual overrides
    root = ttk.Window(themename="minty")
    register_pretendard_fonts(root)
    setup_notion_styles(root)
    app = CompareToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
