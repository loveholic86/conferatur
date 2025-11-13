#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2단계: Text 위젯의 기본 동작 테스트"""

import tkinter as tk

print("=== 2단계: Text 위젯 기본 동작 테스트 ===")
print("Text 위젯에 텍스트를 입력하고, Ctrl+C, Ctrl+V를 눌러보세요")
print()

root = tk.Tk()
root.title("2단계: Text 위젯 테스트")
root.geometry("600x400")

# 상태 표시
status = tk.Label(root, text="Text 위젯에 텍스트를 입력하고 Ctrl+C, Ctrl+V 시도",
                 bg='lightyellow', pady=10, font=('Arial', 10))
status.pack(fill='x')

# 일반 Text 위젯 (아무 커스텀 없음)
text = tk.Text(root, wrap='word', width=60, height=15, font=('Consolas', 11))
text.pack(fill='both', expand=True, padx=10, pady=10)

# 초기 텍스트
text.insert('1.0', '이 텍스트를 선택하고 Ctrl+C로 복사한 후\n다른 곳에 Ctrl+V로 붙여넣기 해보세요.\n\n')
text.insert('end', '아무것도 커스터마이징하지 않은 순수한 tkinter Text 위젯입니다.\n')

# 이벤트 로깅
def log_event(event):
    event_name = event.type
    keysym = getattr(event, 'keysym', 'N/A')
    print(f"이벤트 감지: type={event_name}, keysym={keysym}")

# 모든 키 이벤트 로깅
text.bind('<KeyPress>', log_event, add='+')

print("Text 위젯 생성 완료")
print("기본 tkinter Text 위젯은 자동으로 Ctrl+C, Ctrl+V를 지원해야 합니다.")
print()

root.mainloop()
