#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""클립보드 기능 테스트"""

import tkinter as tk
from tkinter import scrolledtext

def test_basic_clipboard():
    """기본 클립보드 테스트"""
    root = tk.Tk()
    root.title("클립보드 테스트")
    root.geometry("600x400")

    text = scrolledtext.ScrolledText(root, wrap='word', width=40, height=10)
    text.pack(fill='both', expand=True, padx=10, pady=10)

    # 초기 텍스트
    text.insert('1.0', '이 텍스트를 복사/붙여넣기 해보세요.\n\n')

    def copy(event=None):
        print("Copy 함수 호출됨")
        try:
            selected_text = text.get('sel.first', 'sel.last')
            print(f"선택된 텍스트: {selected_text}")
            text.clipboard_clear()
            text.clipboard_append(selected_text)
            print("클립보드에 복사 완료")
        except tk.TclError as e:
            print(f"복사 실패: {e}")
        return 'break'

    def paste(event=None):
        print("Paste 함수 호출됨")
        try:
            clipboard_text = text.clipboard_get()
            print(f"클립보드 내용: {clipboard_text}")
            # 선택된 텍스트가 있으면 삭제
            try:
                text.delete('sel.first', 'sel.last')
            except tk.TclError:
                pass
            # 현재 커서 위치에 붙여넣기
            text.insert('insert', clipboard_text)
            print("붙여넣기 완료")
        except tk.TclError as e:
            print(f"붙여넣기 실패: {e}")
        return 'break'

    def show_context_menu(event):
        print(f"우클릭 이벤트: x={event.x_root}, y={event.y_root}")
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    # 바인딩
    print("바인딩 설정 중...")
    text.bind('<Control-c>', copy)
    text.bind('<Control-v>', paste)
    text.bind('<Button-3>', show_context_menu)
    print("바인딩 완료")

    # 컨텍스트 메뉴
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="복사 (Ctrl+C)", command=copy)
    context_menu.add_command(label="붙여넣기 (Ctrl+V)", command=paste)

    # 상태 표시
    status = tk.Label(root, text="Ctrl+C로 복사, Ctrl+V로 붙여넣기, 우클릭으로 메뉴 열기",
                     bg='lightyellow', fg='black', pady=5)
    status.pack(fill='x', side='bottom')

    print("테스트 창 실행 중...")
    print("콘솔에서 이벤트를 확인하세요.")
    root.mainloop()

if __name__ == '__main__':
    test_basic_clipboard()
