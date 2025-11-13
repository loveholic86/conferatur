#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""macOS용 복사/붙여넣기 테스트"""

import tkinter as tk
import platform

print("=== macOS Command 키 테스트 ===")
print(f"현재 OS: {platform.system()}")
print()

root = tk.Tk()
root.title("macOS Command 키 테스트")
root.geometry("700x500")

status = tk.Label(root, text="Cmd+C, Cmd+V 또는 우클릭 사용",
                 bg='lightyellow', pady=10, font=('Arial', 11, 'bold'))
status.pack(fill='x')

# 로그
log_text = tk.Text(root, height=6, font=('Consolas', 9), bg='#f0f0f0')
log_text.pack(fill='x', padx=10, pady=5)

def log(msg):
    print(msg)
    log_text.insert('end', msg + '\n')
    log_text.see('end')

# 메인 텍스트
text = tk.Text(root, wrap='word', font=('Consolas', 12))
text.pack(fill='both', expand=True, padx=10, pady=10)
text.insert('1.0', '이 텍스트를 선택하고 Cmd+C로 복사한 후\n')
text.insert('end', '아래에 Cmd+V로 붙여넣기 해보세요.\n\n')

# 클립보드 함수들
def do_copy(event=None):
    log(">>> do_copy() 호출됨")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            status.config(text=f"복사 성공: {selected[:30]}...", bg='lightgreen')
            log(f"  복사 완료: {len(selected)} 문자")
        else:
            status.config(text="선택된 텍스트 없음", bg='orange')
            log("  선택 없음")
    except Exception as e:
        status.config(text=f"복사 실패: {e}", bg='lightcoral')
        log(f"  에러: {e}")
    return 'break'

def do_paste(event=None):
    log(">>> do_paste() 호출됨")
    try:
        content = root.clipboard_get()
        if text.tag_ranges('sel'):
            text.delete('sel.first', 'sel.last')
        text.insert('insert', content)
        status.config(text=f"붙여넣기 성공: {content[:30]}...", bg='lightgreen')
        log(f"  붙여넣기 완료: {len(content)} 문자")
    except Exception as e:
        status.config(text=f"붙여넣기 실패: {e}", bg='lightcoral')
        log(f"  에러: {e}")
    return 'break'

def do_cut(event=None):
    log(">>> do_cut() 호출됨")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            text.delete('sel.first', 'sel.last')
            status.config(text=f"잘라내기 성공: {selected[:30]}...", bg='lightgreen')
            log(f"  잘라내기 완료: {len(selected)} 문자")
    except Exception as e:
        status.config(text=f"잘라내기 실패: {e}", bg='lightcoral')
        log(f"  에러: {e}")
    return 'break'

def do_select_all(event=None):
    log(">>> do_select_all() 호출됨")
    text.tag_add('sel', '1.0', 'end-1c')
    text.mark_set('insert', '1.0')
    status.config(text="전체 선택 완료", bg='lightblue')
    return 'break'

# macOS Command 키 바인딩
log("macOS Command 키 바인딩 설정 중...")
text.bind('<Command-c>', do_copy)
text.bind('<Command-x>', do_cut)
text.bind('<Command-v>', do_paste)
text.bind('<Command-a>', do_select_all)
log("바인딩 완료: Cmd+C, Cmd+X, Cmd+V, Cmd+A")
log("")

# 우클릭 메뉴
context_menu = tk.Menu(root, tearoff=0)

def show_menu(event):
    log("우클릭 메뉴 표시")
    context_menu.delete(0, tk.END)
    context_menu.add_command(label="복사 (Cmd+C)", command=do_copy)
    context_menu.add_command(label="잘라내기 (Cmd+X)", command=do_cut)
    context_menu.add_command(label="붙여넣기 (Cmd+V)", command=do_paste)
    context_menu.add_separator()
    context_menu.add_command(label="전체 선택 (Cmd+A)", command=do_select_all)

    try:
        context_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        context_menu.grab_release()

text.bind('<Button-2>', show_menu)  # macOS는 Button-2가 우클릭
text.bind('<Button-3>', show_menu)  # 일부 설정에서는 Button-3
text.bind('<Control-Button-1>', show_menu)  # Ctrl+클릭도 우클릭
log("우클릭 바인딩 완료 (Button-2, Button-3, Ctrl+Button-1)")
log("")
log("=== 테스트 시작 ===")
log("1. 텍스트 선택 후 Cmd+C (복사)")
log("2. 다른 위치에서 Cmd+V (붙여넣기)")
log("3. 우클릭으로 메뉴 열기")
log("")

root.mainloop()
