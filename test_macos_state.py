#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""macOS Command 키 state 기반 감지 테스트"""

import tkinter as tk
import platform

print("=== macOS Command 키 state 기반 감지 ===")
print(f"OS: {platform.system()}")
print()

root = tk.Tk()
root.title("Command 키 state 감지 테스트")
root.geometry("700x500")

status = tk.Label(root, text="텍스트 영역에서 Cmd+C, Cmd+V 시도",
                 bg='lightyellow', pady=10, font=('Arial', 11, 'bold'))
status.pack(fill='x')

# 로그
log_text = tk.Text(root, height=8, font=('Consolas', 9), bg='#f0f0f0')
log_text.pack(fill='x', padx=10, pady=5)

def log(msg):
    print(msg)
    log_text.insert('end', msg + '\n')
    log_text.see('end')

# 메인 텍스트
text = tk.Text(root, wrap='word', font=('Consolas', 12))
text.pack(fill='both', expand=True, padx=10, pady=10)
text.insert('1.0', '이 텍스트를 선택하고 Cmd+C를 눌러보세요.\n\n')

# 클립보드 함수
def do_copy():
    log(">>> do_copy() 실행")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            status.config(text=f"복사 성공!", bg='lightgreen')
            log(f"  복사 완료: '{selected[:40]}...'")
        else:
            status.config(text="선택 없음", bg='orange')
    except Exception as e:
        log(f"  에러: {e}")
    return 'break'

def do_paste():
    log(">>> do_paste() 실행")
    try:
        content = root.clipboard_get()
        if text.tag_ranges('sel'):
            text.delete('sel.first', 'sel.last')
        text.insert('insert', content)
        status.config(text=f"붙여넣기 성공!", bg='lightgreen')
        log(f"  붙여넣기 완료: '{content[:40]}...'")
    except Exception as e:
        log(f"  에러: {e}")
    return 'break'

def do_cut():
    log(">>> do_cut() 실행")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            text.delete('sel.first', 'sel.last')
            status.config(text=f"잘라내기 성공!", bg='lightgreen')
            log(f"  잘라내기 완료")
    except Exception as e:
        log(f"  에러: {e}")
    return 'break'

# state 기반 키 감지
def on_key_press(event):
    """모든 키를 감지하고 Command 키 조합 체크"""
    # macOS에서 Command 키는 state의 비트 8 (0x0008)에 설정됨
    # 하지만 실제로는 다를 수 있으므로 여러 비트를 체크

    is_command = False

    # 여러 방법으로 Command 키 감지 시도
    if event.state & 0x0008:  # Alt/Option (일반적으로)
        is_command = True
    if event.state & 0x0010:  # Command (일부 경우)
        is_command = True
    if hasattr(event, 'keysym') and 'Meta' in event.keysym:
        is_command = True

    log(f"키 입력: keysym='{event.keysym}', char='{event.char}', state={hex(event.state)}, is_command={is_command}")

    # Command 키가 눌린 상태에서 특정 키 조합 감지
    # keysym 대신 char를 사용 (macOS에서 keysym이 '??'로 나옴)
    if is_command and event.char:
        key_char = event.char.lower()
        if key_char == 'c':
            log("  >>> Cmd+C 감지!")
            status.config(text="Cmd+C 감지!", bg='yellow')
            return do_copy()
        elif key_char == 'v':
            log("  >>> Cmd+V 감지!")
            status.config(text="Cmd+V 감지!", bg='yellow')
            return do_paste()
        elif key_char == 'x':
            log("  >>> Cmd+X 감지!")
            status.config(text="Cmd+X 감지!", bg='yellow')
            return do_cut()
        elif key_char == 'a':
            log("  >>> Cmd+A 감지!")
            status.config(text="Cmd+A 감지!", bg='yellow')
            text.tag_add('sel', '1.0', 'end-1c')
            return 'break'

# KeyPress 이벤트로 모든 키 감지
log("KeyPress 이벤트 바인딩...")
text.bind('<KeyPress>', on_key_press)
log("바인딩 완료!")
log("")
log("=== 테스트 시작 ===")
log("텍스트를 선택하고 Cmd+C를 눌러보세요")
log("")

# 우클릭 메뉴
menu = tk.Menu(root, tearoff=0)

def show_menu(event):
    log("우클릭 메뉴")
    menu.delete(0, tk.END)
    menu.add_command(label="복사 (Cmd+C)", command=do_copy)
    menu.add_command(label="잘라내기 (Cmd+X)", command=do_cut)
    menu.add_command(label="붙여넣기 (Cmd+V)", command=do_paste)
    try:
        menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        menu.grab_release()

text.bind('<Button-2>', show_menu)
text.bind('<Button-3>', show_menu)
text.bind('<Control-Button-1>', show_menu)

root.mainloop()
