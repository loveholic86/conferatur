#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""4단계: 우클릭 메뉴 테스트"""

import tkinter as tk

print("=== 4단계: 우클릭 메뉴 테스트 ===")
print("창 안에서 우클릭하세요")
print()

root = tk.Tk()
root.title("4단계: 우클릭 메뉴 테스트")
root.geometry("500x300")

status = tk.Label(root, text="창 안에서 우클릭 하세요",
                 bg='lightyellow', pady=20, font=('Arial', 12, 'bold'))
status.pack(fill='both', expand=True)

# 우클릭 메뉴 생성
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="메뉴 항목 1", command=lambda: status.config(text="메뉴 항목 1 클릭됨!"))
menu.add_command(label="메뉴 항목 2", command=lambda: status.config(text="메뉴 항목 2 클릭됨!"))
menu.add_separator()
menu.add_command(label="메뉴 항목 3", command=lambda: status.config(text="메뉴 항목 3 클릭됨!"))

def show_menu(event):
    """우클릭 시 메뉴 표시"""
    print(f"우클릭 감지: x={event.x}, y={event.y}, x_root={event.x_root}, y_root={event.y_root}")
    status.config(text=f"우클릭 감지! 위치: ({event.x}, {event.y})")
    try:
        menu.tk_popup(event.x_root, event.y_root, 0)
        print("메뉴 표시됨")
    except Exception as e:
        print(f"메뉴 표시 실패: {e}")
        status.config(text=f"메뉴 표시 실패: {e}")
    finally:
        menu.grab_release()

print("우클릭 이벤트 바인딩 중...")
root.bind('<Button-3>', show_menu)
status.bind('<Button-3>', show_menu)
print("바인딩 완료!")
print()

root.mainloop()
