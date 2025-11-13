#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1단계: 가장 기본적인 tkinter 테스트"""

import tkinter as tk

print("=== 1단계: 기본 tkinter 테스트 ===")
print("이 창에서 아무 키나 누르고, 마우스를 클릭하세요.")
print()

root = tk.Tk()
root.title("1단계: 기본 이벤트 테스트")
root.geometry("500x300")

status_text = tk.StringVar()
status_text.set("아무 키나 누르거나 마우스를 클릭하세요")

label = tk.Label(root, textvariable=status_text,
                bg='lightyellow', pady=20, font=('Arial', 12))
label.pack(fill='both', expand=True)

def on_key(event):
    msg = f"키 입력: {event.char} (keysym: {event.keysym})"
    print(msg)
    status_text.set(msg)

def on_left_click(event):
    msg = f"왼쪽 클릭: x={event.x}, y={event.y}"
    print(msg)
    status_text.set(msg)

def on_right_click(event):
    msg = f"오른쪽 클릭: x={event.x}, y={event.y}"
    print(msg)
    status_text.set(msg)

print("이벤트 바인딩 중...")
root.bind('<Key>', on_key)
root.bind('<Button-1>', on_left_click)
root.bind('<Button-3>', on_right_click)
print("바인딩 완료!")
print()

root.mainloop()
