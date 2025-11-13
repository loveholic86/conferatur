#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""가장 단순한 붙여넣기 테스트"""

import tkinter as tk
from tkinter import scrolledtext

root = tk.Tk()
root.title("단순 붙여넣기 테스트")
root.geometry("500x300")

# 안내 메시지
label = tk.Label(root, text="아래 텍스트 영역에 Ctrl+V 또는 우클릭으로 붙여넣기 시도",
                bg='yellow', pady=10)
label.pack(fill='x')

# ScrolledText 위젯
text_widget = scrolledtext.ScrolledText(root, wrap='word', width=50, height=10)
text_widget.pack(fill='both', expand=True, padx=10, pady=10)

# 초기 텍스트
text_widget.insert('1.0', '여기에 붙여넣기를 시도하세요.\n\n')

# 상태 표시용 레이블
status = tk.Label(root, text="대기 중...", bg='lightgray', pady=5)
status.pack(fill='x')

# 가장 단순한 붙여넣기 구현
def simple_paste(event=None):
    """가장 단순한 붙여넣기"""
    status.config(text="붙여넣기 함수 호출됨!", bg='lightgreen')
    try:
        # 클립보드에서 텍스트 가져오기
        content = root.clipboard_get()
        status.config(text=f"클립보드 내용: {content[:30]}...", bg='lightgreen')

        # 현재 위치에 삽입
        text_widget.insert(tk.INSERT, content)
        status.config(text="붙여넣기 성공!", bg='lightgreen')
    except Exception as e:
        status.config(text=f"에러: {str(e)}", bg='lightcoral')
    return 'break'

def simple_copy(event=None):
    """가장 단순한 복사"""
    status.config(text="복사 함수 호출됨!", bg='lightblue')
    try:
        # 선택된 텍스트 가져오기
        if text_widget.tag_ranges('sel'):
            selected = text_widget.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            status.config(text=f"복사 성공: {selected[:30]}...", bg='lightblue')
        else:
            status.config(text="선택된 텍스트가 없습니다", bg='orange')
    except Exception as e:
        status.config(text=f"에러: {str(e)}", bg='lightcoral')
    return 'break'

# 바인딩
print("바인딩 시작...")
text_widget.bind('<Control-v>', simple_paste)
text_widget.bind('<Control-c>', simple_copy)
print("바인딩 완료")

# 우클릭 메뉴
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="복사", command=simple_copy)
menu.add_command(label="붙여넣기", command=simple_paste)

def show_menu(event):
    """우클릭 메뉴 표시"""
    status.config(text="우클릭 메뉴 열림", bg='lightyellow')
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

text_widget.bind('<Button-3>', show_menu)
print("우클릭 바인딩 완료")

root.mainloop()
