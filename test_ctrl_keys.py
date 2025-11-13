#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ctrl 키 감지 상세 테스트"""

import tkinter as tk

print("=== Ctrl 키 감지 테스트 ===")
print("다양한 키를 눌러보세요:")
print("- 일반 키: a, b, c")
print("- Ctrl+C, Ctrl+V, Ctrl+A")
print("- Shift+A")
print()

root = tk.Tk()
root.title("Ctrl 키 감지 테스트")
root.geometry("700x500")

# 안내
info = tk.Label(root, text="아래 텍스트 영역에 포커스를 두고 다양한 키를 눌러보세요\n(Ctrl+C, Ctrl+V, Shift+A 등)",
                bg='lightyellow', pady=10, font=('Arial', 10, 'bold'))
info.pack(fill='x')

# 이벤트 로그
log_frame = tk.Frame(root)
log_frame.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(log_frame, text="이벤트 로그:", font=('Arial', 9, 'bold')).pack(anchor='w')
log_text = tk.Text(log_frame, wrap='word', font=('Consolas', 9), bg='#f5f5f5')
log_text.pack(fill='both', expand=True)

# 테스트용 텍스트 위젯
tk.Label(root, text="테스트 텍스트 영역 (여기에 포커스):", font=('Arial', 9, 'bold')).pack(anchor='w', padx=10)
text = tk.Text(root, wrap='word', height=5, font=('Consolas', 11))
text.pack(fill='x', padx=10, pady=5)
text.insert('1.0', '이 영역에 포커스를 두고 Ctrl+C, Ctrl+V 등을 눌러보세요\n')

def log(msg):
    """로그 추가"""
    print(msg)
    log_text.insert('end', msg + '\n')
    log_text.see('end')

def on_key_press(event):
    """모든 키 입력 감지"""
    info_parts = []

    # 기본 정보
    info_parts.append(f"char='{event.char}'")
    info_parts.append(f"keysym='{event.keysym}'")
    info_parts.append(f"keycode={event.keycode}")

    # 수정자 키 상태
    modifiers = []
    if event.state & 0x0004:  # Control
        modifiers.append("Ctrl")
    if event.state & 0x0001:  # Shift
        modifiers.append("Shift")
    if event.state & 0x0008:  # Alt
        modifiers.append("Alt")

    if modifiers:
        info_parts.append(f"modifiers={'+'.join(modifiers)}")

    info_parts.append(f"state={hex(event.state)}")

    msg = "KeyPress: " + ", ".join(info_parts)
    log(msg)

def on_ctrl_c(event):
    """Ctrl+C 전용 핸들러"""
    log(">>> <Control-c> 이벤트 감지! <<<")
    return 'break'

def on_ctrl_v(event):
    """Ctrl+V 전용 핸들러"""
    log(">>> <Control-v> 이벤트 감지! <<<")
    return 'break'

def on_ctrl_a(event):
    """Ctrl+A 전용 핸들러"""
    log(">>> <Control-a> 이벤트 감지! <<<")
    return 'break'

def on_ctrl_key(event):
    """일반 Ctrl 키 조합"""
    log(f">>> <Control-Key> 이벤트: {event.keysym} <<<")

# 모든 키 입력 감지
log("바인딩 설정 중...")
text.bind('<KeyPress>', on_key_press, add='+')

# 명시적인 Ctrl 조합 바인딩
text.bind('<Control-c>', on_ctrl_c, add='+')
text.bind('<Control-v>', on_ctrl_v, add='+')
text.bind('<Control-a>', on_ctrl_a, add='+')
text.bind('<Control-Key>', on_ctrl_key, add='+')

log("바인딩 완료!")
log("")
log("=== 테스트 시작 ===")
log("다음을 순서대로 눌러보세요:")
log("1. 'a' 키")
log("2. 'Ctrl+C'")
log("3. 'Ctrl+V'")
log("4. 'Ctrl+A'")
log("5. 'Shift+A'")
log("")

root.mainloop()
