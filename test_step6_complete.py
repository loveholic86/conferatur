#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""6단계: 완전한 복사/붙여넣기 + 우클릭 테스트"""

import tkinter as tk

print("=== 6단계: 완전한 복사/붙여넣기 + 우클릭 테스트 ===")
print()

root = tk.Tk()
root.title("6단계: 완전한 테스트")
root.geometry("700x500")

status = tk.Label(root, text="Ctrl+C/V 또는 우클릭 메뉴 사용",
                 bg='lightyellow', pady=10, font=('Arial', 10, 'bold'))
status.pack(fill='x')

# 로그
log_text = tk.Text(root, height=5, font=('Consolas', 8), bg='#f0f0f0')
log_text.pack(fill='x', padx=10, pady=5)

def log(msg):
    print(msg)
    log_text.insert('end', msg + '\n')
    log_text.see('end')

# 메인 텍스트
text = tk.Text(root, wrap='word', font=('Consolas', 11))
text.pack(fill='both', expand=True, padx=10, pady=10)
text.insert('1.0', '이 텍스트를 복사/붙여넣기 해보세요.\n\n')

# 복사/붙여넣기 함수
def do_copy(event=None):
    log("do_copy() 호출")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            status.config(text=f"복사: {selected[:30]}...", bg='lightgreen')
            log(f"  복사 성공: {len(selected)} 문자")
        else:
            status.config(text="선택 없음", bg='orange')
            log("  선택된 텍스트 없음")
    except Exception as e:
        status.config(text=f"복사 실패: {e}", bg='lightcoral')
        log(f"  에러: {e}")
    return 'break'

def do_paste(event=None):
    log("do_paste() 호출")
    try:
        content = root.clipboard_get()
        if text.tag_ranges('sel'):
            text.delete('sel.first', 'sel.last')
        text.insert('insert', content)
        status.config(text=f"붙여넣기: {content[:30]}...", bg='lightgreen')
        log(f"  붙여넣기 성공: {len(content)} 문자")
    except Exception as e:
        status.config(text=f"붙여넣기 실패: {e}", bg='lightcoral')
        log(f"  에러: {e}")
    return 'break'

def do_cut(event=None):
    log("do_cut() 호출")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            text.delete('sel.first', 'sel.last')
            status.config(text=f"잘라내기: {selected[:30]}...", bg='lightgreen')
            log(f"  잘라내기 성공: {len(selected)} 문자")
        else:
            status.config(text="선택 없음", bg='orange')
            log("  선택된 텍스트 없음")
    except Exception as e:
        status.config(text=f"잘라내기 실패: {e}", bg='lightcoral')
        log(f"  에러: {e}")
    return 'break'

def do_select_all(event=None):
    log("do_select_all() 호출")
    text.tag_add('sel', '1.0', 'end-1c')
    text.mark_set('insert', '1.0')
    text.see('insert')
    status.config(text="전체 선택", bg='lightblue')
    return 'break'

# 키 바인딩
log("키 바인딩: Ctrl+C, Ctrl+X, Ctrl+V, Ctrl+A")
text.bind('<Control-c>', do_copy)
text.bind('<Control-x>', do_cut)
text.bind('<Control-v>', do_paste)
text.bind('<Control-a>', do_select_all)

# 우클릭 메뉴
context_menu = tk.Menu(root, tearoff=0)

def show_menu(event):
    log(f"우클릭: ({event.x}, {event.y})")
    status.config(text="우클릭 메뉴 표시", bg='lightyellow')

    # 메뉴 재생성
    context_menu.delete(0, tk.END)
    context_menu.add_command(label="복사 (Ctrl+C)", command=do_copy)
    context_menu.add_command(label="잘라내기 (Ctrl+X)", command=do_cut)
    context_menu.add_command(label="붙여넣기 (Ctrl+V)", command=do_paste)
    context_menu.add_separator()
    context_menu.add_command(label="전체 선택 (Ctrl+A)", command=do_select_all)

    try:
        context_menu.tk_popup(event.x_root, event.y_root, 0)
        log("  메뉴 표시됨")
    except Exception as e:
        log(f"  메뉴 표시 실패: {e}")
    finally:
        context_menu.grab_release()

text.bind('<Button-3>', show_menu)
log("우클릭 바인딩 완료")
log("")

root.mainloop()
