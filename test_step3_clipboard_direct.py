#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3단계: 클립보드 직접 접근 테스트"""

import tkinter as tk

print("=== 3단계: 클립보드 직접 접근 테스트 ===")
print()

root = tk.Tk()
root.title("3단계: 클립보드 테스트")
root.geometry("600x400")

# 상태 표시
status = tk.Label(root, text="클립보드 읽기/쓰기 테스트",
                 bg='lightyellow', pady=10, font=('Arial', 10, 'bold'))
status.pack(fill='x')

# 버튼 프레임
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# 결과 표시
result_text = tk.Text(root, wrap='word', height=15, font=('Consolas', 10))
result_text.pack(fill='both', expand=True, padx=10, pady=10)

def test_clipboard_write():
    """클립보드에 쓰기 테스트"""
    try:
        test_string = "테스트 문자열 - " + str(tk.IntVar().get())
        root.clipboard_clear()
        root.clipboard_append(test_string)
        root.update()  # 클립보드 업데이트

        result = f"✓ 클립보드에 쓰기 성공: '{test_string}'\n"
        print(result)
        result_text.insert('end', result)
        status.config(text="클립보드 쓰기 성공!", bg='lightgreen')
    except Exception as e:
        result = f"✗ 클립보드 쓰기 실패: {e}\n"
        print(result)
        result_text.insert('end', result)
        status.config(text=f"쓰기 실패: {e}", bg='lightcoral')

def test_clipboard_read():
    """클립보드에서 읽기 테스트"""
    try:
        content = root.clipboard_get()
        result = f"✓ 클립보드에서 읽기 성공: '{content}'\n"
        print(result)
        result_text.insert('end', result)
        status.config(text="클립보드 읽기 성공!", bg='lightgreen')
    except Exception as e:
        result = f"✗ 클립보드 읽기 실패: {e}\n"
        print(result)
        result_text.insert('end', result)
        status.config(text=f"읽기 실패: {e}", bg='lightcoral')

def test_external_clipboard():
    """외부 프로그램에서 복사한 내용 읽기"""
    result_text.insert('end', "\n=== 외부 클립보드 테스트 ===\n")
    result_text.insert('end', "다른 프로그램에서 텍스트를 복사한 후 '외부 클립보드 읽기' 버튼을 누르세요.\n\n")
    status.config(text="다른 프로그램에서 복사 후 테스트하세요", bg='lightyellow')

# 버튼들
btn1 = tk.Button(button_frame, text="클립보드에 쓰기",
                command=test_clipboard_write,
                bg='lightblue', padx=10, pady=5)
btn1.pack(side='left', padx=5)

btn2 = tk.Button(button_frame, text="클립보드 읽기",
                command=test_clipboard_read,
                bg='lightgreen', padx=10, pady=5)
btn2.pack(side='left', padx=5)

btn3 = tk.Button(button_frame, text="외부 클립보드 읽기",
                command=test_clipboard_read,
                bg='lightyellow', padx=10, pady=5)
btn3.pack(side='left', padx=5)

# 초기 안내
result_text.insert('1.0', "클립보드 테스트 순서:\n")
result_text.insert('end', "1. '클립보드에 쓰기' 버튼 클릭\n")
result_text.insert('end', "2. '클립보드 읽기' 버튼 클릭 (방금 쓴 내용이 보여야 함)\n")
result_text.insert('end', "3. 외부 프로그램(메모장 등)에서 텍스트 복사\n")
result_text.insert('end', "4. '외부 클립보드 읽기' 버튼 클릭\n\n")

print("버튼을 클릭하여 클립보드 기능을 테스트하세요.")
print()

root.mainloop()
