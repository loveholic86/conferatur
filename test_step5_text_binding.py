#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5단계: Text 위젯 바인딩 테스트"""

import tkinter as tk

print("=== 5단계: Text 위젯 키 바인딩 테스트 ===")
print()

root = tk.Tk()
root.title("5단계: Text 위젯 바인딩")
root.geometry("700x500")

status = tk.Label(root, text="Text 위젯에서 Ctrl+C, Ctrl+V 시도",
                 bg='lightyellow', pady=10, font=('Arial', 10, 'bold'))
status.pack(fill='x')

# 로그 표시
log_frame = tk.Frame(root)
log_frame.pack(fill='x', padx=10, pady=5)
tk.Label(log_frame, text="이벤트 로그:", font=('Arial', 9, 'bold')).pack(anchor='w')

log_text = tk.Text(log_frame, height=5, font=('Consolas', 9), bg='#f0f0f0')
log_text.pack(fill='x')

# 메인 텍스트 위젯
tk.Label(root, text="메인 텍스트 영역:", font=('Arial', 9, 'bold')).pack(anchor='w', padx=10)
text = tk.Text(root, wrap='word', width=60, height=10, font=('Consolas', 11))
text.pack(fill='both', expand=True, padx=10, pady=10)

text.insert('1.0', '이 텍스트를 선택하고 Ctrl+C를 누르세요.\n\n')

def log(msg):
    """로그 추가"""
    print(msg)
    log_text.insert('end', msg + '\n')
    log_text.see('end')

def my_copy(event=None):
    """복사 함수"""
    log(">>> my_copy() 호출됨")
    try:
        if text.tag_ranges('sel'):
            selected = text.get('sel.first', 'sel.last')
            log(f"  선택된 텍스트: '{selected[:50]}...'")
            root.clipboard_clear()
            root.clipboard_append(selected)
            root.update()
            log("  클립보드에 복사 완료")
            status.config(text="복사 성공!", bg='lightgreen')
        else:
            log("  선택된 텍스트 없음")
            status.config(text="선택된 텍스트 없음", bg='orange')
    except Exception as e:
        log(f"  에러: {e}")
        status.config(text=f"복사 실패: {e}", bg='lightcoral')
    return 'break'

def my_paste(event=None):
    """붙여넣기 함수"""
    log(">>> my_paste() 호출됨")
    try:
        clipboard_content = root.clipboard_get()
        log(f"  클립보드 내용: '{clipboard_content[:50]}...'")

        # 선택된 텍스트 있으면 삭제
        if text.tag_ranges('sel'):
            text.delete('sel.first', 'sel.last')
            log("  선택 영역 삭제")

        # 삽입
        text.insert('insert', clipboard_content)
        log("  붙여넣기 완료")
        status.config(text="붙여넣기 성공!", bg='lightgreen')
    except Exception as e:
        log(f"  에러: {e}")
        status.config(text=f"붙여넣기 실패: {e}", bg='lightcoral')
    return 'break'

def my_select_all(event=None):
    """전체 선택"""
    log(">>> my_select_all() 호출됨")
    text.tag_add('sel', '1.0', 'end-1c')
    text.mark_set('insert', '1.0')
    text.see('insert')
    status.config(text="전체 선택 완료", bg='lightblue')
    return 'break'

# 바인딩
log("키 바인딩 중...")
text.bind('<Control-c>', my_copy)
text.bind('<Control-v>', my_paste)
text.bind('<Control-a>', my_select_all)
log("바인딩 완료: Ctrl+C, Ctrl+V, Ctrl+A")
log("")

root.mainloop()
