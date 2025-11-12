#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 및 폴더 비교 도구
세 가지 모드를 지원:
1. 폴더 비교 (MD5/날짜)
2. 텍스트 직접 비교
3. 파일 내용 비교
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import hashlib
import difflib
import shutil
from datetime import datetime
from pathlib import Path


class CompareToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("파일/폴더 비교 도구")
        self.root.geometry("1200x800")

        # 탭 생성
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 세 가지 모드 탭 생성
        self.folder_compare_tab = ttk.Frame(self.notebook)
        self.text_compare_tab = ttk.Frame(self.notebook)
        self.file_compare_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.folder_compare_tab, text="폴더 비교")
        self.notebook.add(self.text_compare_tab, text="텍스트 비교")
        self.notebook.add(self.file_compare_tab, text="파일 비교")

        # 각 탭 초기화
        self.setup_folder_compare_tab()
        self.setup_text_compare_tab()
        self.setup_file_compare_tab()

    def setup_folder_compare_tab(self):
        """첫 번째 모드: 폴더 비교"""
        frame = self.folder_compare_tab

        # 상단 컨트롤 영역
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 왼쪽 폴더 선택
        ttk.Label(control_frame, text="왼쪽 폴더:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.left_folder_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.left_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_folder(self.left_folder_var)).grid(row=0, column=2, padx=5, pady=5)

        # 오른쪽 폴더 선택
        ttk.Label(control_frame, text="오른쪽 폴더:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.right_folder_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.right_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_folder(self.right_folder_var)).grid(row=1, column=2, padx=5, pady=5)

        # 비교 옵션
        option_frame = ttk.Frame(control_frame)
        option_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.compare_method_var = tk.StringVar(value="md5")
        ttk.Radiobutton(option_frame, text="MD5 비교", variable=self.compare_method_var, value="md5").pack(side='left', padx=10)
        ttk.Radiobutton(option_frame, text="날짜 비교", variable=self.compare_method_var, value="date").pack(side='left', padx=10)
        ttk.Radiobutton(option_frame, text="MD5 + 날짜", variable=self.compare_method_var, value="both").pack(side='left', padx=10)

        ttk.Button(option_frame, text="비교 시작", command=self.compare_folders).pack(side='left', padx=20)

        # 결과 영역
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 트리뷰 생성
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill='both', expand=True)

        # 스크롤바
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')

        # 트리뷰
        self.folder_tree = ttk.Treeview(tree_frame,
                                        columns=('상태', '왼쪽_크기', '왼쪽_수정일', '오른쪽_크기', '오른쪽_수정일'),
                                        yscrollcommand=tree_scroll_y.set,
                                        xscrollcommand=tree_scroll_x.set)
        self.folder_tree.pack(fill='both', expand=True)

        tree_scroll_y.config(command=self.folder_tree.yview)
        tree_scroll_x.config(command=self.folder_tree.xview)

        # 트리뷰 열 설정
        self.folder_tree.heading('#0', text='파일 경로')
        self.folder_tree.heading('상태', text='상태')
        self.folder_tree.heading('왼쪽_크기', text='왼쪽 크기')
        self.folder_tree.heading('왼쪽_수정일', text='왼쪽 수정일')
        self.folder_tree.heading('오른쪽_크기', text='오른쪽 크기')
        self.folder_tree.heading('오른쪽_수정일', text='오른쪽 수정일')

        self.folder_tree.column('#0', width=300)
        self.folder_tree.column('상태', width=100)
        self.folder_tree.column('왼쪽_크기', width=100)
        self.folder_tree.column('왼쪽_수정일', width=150)
        self.folder_tree.column('오른쪽_크기', width=100)
        self.folder_tree.column('오른쪽_수정일', width=150)

        # 버튼 영역
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="왼쪽 → 오른쪽 복사", command=lambda: self.copy_file('left_to_right')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="오른쪽 → 왼쪽 복사", command=lambda: self.copy_file('right_to_left')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="선택 항목 삭제", command=self.delete_selected).pack(side='left', padx=5)

    def setup_text_compare_tab(self):
        """두 번째 모드: 텍스트 직접 비교"""
        frame = self.text_compare_tab

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(control_frame, text="비교하기", command=self.compare_text).pack(side='left', padx=5)
        ttk.Button(control_frame, text="왼쪽으로 적용", command=lambda: self.apply_text('to_left')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="오른쪽으로 적용", command=lambda: self.apply_text('to_right')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="초기화", command=self.clear_text_comparison).pack(side='left', padx=5)

        # 텍스트 입력 영역
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 왼쪽 텍스트
        left_frame = ttk.Frame(text_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(left_frame, text="왼쪽 텍스트", font=('', 12, 'bold')).pack()
        self.text_left = scrolledtext.ScrolledText(left_frame, wrap='word', width=40, height=30)
        self.text_left.pack(fill='both', expand=True)

        # 오른쪽 텍스트
        right_frame = ttk.Frame(text_frame)
        right_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(right_frame, text="오른쪽 텍스트", font=('', 12, 'bold')).pack()
        self.text_right = scrolledtext.ScrolledText(right_frame, wrap='word', width=40, height=30)
        self.text_right.pack(fill='both', expand=True)

        # 차이점 표시를 위한 태그 설정
        self.text_left.tag_config('diff', background='#ffcccc')
        self.text_right.tag_config('diff', background='#ffcccc')

    def setup_file_compare_tab(self):
        """세 번째 모드: 파일 내용 비교"""
        frame = self.file_compare_tab

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        # 왼쪽 파일 선택
        ttk.Label(control_frame, text="왼쪽 파일:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.file_left_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_left_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_file(self.file_left_var)).grid(row=0, column=2, padx=5, pady=5)

        # 오른쪽 파일 선택
        ttk.Label(control_frame, text="오른쪽 파일:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.file_right_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_right_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="찾아보기", command=lambda: self.browse_file(self.file_right_var)).grid(row=1, column=2, padx=5, pady=5)

        # 버튼
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="비교하기", command=self.compare_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="왼쪽 파일 저장", command=lambda: self.save_file('left')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="오른쪽 파일 저장", command=lambda: self.save_file('right')).pack(side='left', padx=5)

        # 파일 내용 표시 영역
        file_text_frame = ttk.Frame(frame)
        file_text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 왼쪽 파일 내용
        left_file_frame = ttk.Frame(file_text_frame)
        left_file_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(left_file_frame, text="왼쪽 파일 내용", font=('', 12, 'bold')).pack()
        self.file_text_left = scrolledtext.ScrolledText(left_file_frame, wrap='word', width=40, height=30)
        self.file_text_left.pack(fill='both', expand=True)

        # 오른쪽 파일 내용
        right_file_frame = ttk.Frame(file_text_frame)
        right_file_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(right_file_frame, text="오른쪽 파일 내용", font=('', 12, 'bold')).pack()
        self.file_text_right = scrolledtext.ScrolledText(right_file_frame, wrap='word', width=40, height=30)
        self.file_text_right.pack(fill='both', expand=True)

        # 차이점 표시를 위한 태그 설정
        self.file_text_left.tag_config('diff', background='#ffcccc')
        self.file_text_right.tag_config('diff', background='#ffcccc')

    # 유틸리티 메서드
    def browse_folder(self, var):
        """폴더 선택 대화상자"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    def browse_file(self, var):
        """파일 선택 대화상자"""
        file = filedialog.askopenfilename()
        if file:
            var.set(file)

    def calculate_md5(self, filepath):
        """파일의 MD5 해시 계산"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return None

    def get_file_info(self, filepath):
        """파일 정보 가져오기"""
        try:
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'mtime_raw': stat.st_mtime
            }
        except Exception as e:
            return None

    def compare_folders(self):
        """폴더 비교 실행"""
        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        if not left_folder or not right_folder:
            messagebox.showwarning("경고", "두 폴더를 모두 선택해주세요.")
            return

        if not os.path.exists(left_folder) or not os.path.exists(right_folder):
            messagebox.showerror("오류", "선택한 폴더가 존재하지 않습니다.")
            return

        # 트리뷰 초기화
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        compare_method = self.compare_method_var.get()

        # 파일 목록 수집
        left_files = {}
        right_files = {}

        for root, dirs, files in os.walk(left_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, left_folder)
                left_files[rel_path] = full_path

        for root, dirs, files in os.walk(right_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, right_folder)
                right_files[rel_path] = full_path

        # 모든 파일 경로 합치기
        all_paths = set(left_files.keys()) | set(right_files.keys())

        differences = []

        for rel_path in sorted(all_paths):
            left_path = left_files.get(rel_path)
            right_path = right_files.get(rel_path)

            status = ""
            left_info = self.get_file_info(left_path) if left_path else None
            right_info = self.get_file_info(right_path) if right_path else None

            if not left_path:
                status = "오른쪽만 존재"
            elif not right_path:
                status = "왼쪽만 존재"
            else:
                # 비교 수행
                different = False

                if compare_method == "md5":
                    left_md5 = self.calculate_md5(left_path)
                    right_md5 = self.calculate_md5(right_path)
                    if left_md5 != right_md5:
                        different = True
                        status = "내용 다름 (MD5)"

                elif compare_method == "date":
                    if left_info and right_info:
                        if left_info['mtime_raw'] != right_info['mtime_raw']:
                            different = True
                            if left_info['mtime_raw'] > right_info['mtime_raw']:
                                status = "왼쪽이 최신"
                            else:
                                status = "오른쪽이 최신"

                elif compare_method == "both":
                    left_md5 = self.calculate_md5(left_path)
                    right_md5 = self.calculate_md5(right_path)
                    if left_md5 != right_md5:
                        different = True
                        status = "내용 다름 (MD5)"
                    elif left_info and right_info and left_info['mtime_raw'] != right_info['mtime_raw']:
                        different = True
                        if left_info['mtime_raw'] > right_info['mtime_raw']:
                            status = "내용 같음, 왼쪽이 최신"
                        else:
                            status = "내용 같음, 오른쪽이 최신"

                if not different and status == "":
                    status = "동일"

            # 차이가 있는 파일만 표시
            if status != "동일":
                left_size = left_info['size'] if left_info else ""
                left_mtime = left_info['mtime'] if left_info else ""
                right_size = right_info['size'] if right_info else ""
                right_mtime = right_info['mtime'] if right_info else ""

                item_id = self.folder_tree.insert('', 'end', text=rel_path,
                                                   values=(status, left_size, left_mtime, right_size, right_mtime))
                # 아이템에 경로 정보 저장
                self.folder_tree.set(item_id, '#0', rel_path)

        messagebox.showinfo("완료", f"비교가 완료되었습니다.\n차이가 있는 파일: {len(self.folder_tree.get_children())}개")

    def copy_file(self, direction):
        """파일 복사"""
        selected = self.folder_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "복사할 파일을 선택해주세요.")
            return

        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        copied_count = 0
        error_count = 0

        for item in selected:
            rel_path = self.folder_tree.item(item, 'text')
            left_path = os.path.join(left_folder, rel_path)
            right_path = os.path.join(right_folder, rel_path)

            try:
                if direction == 'left_to_right':
                    if os.path.exists(left_path):
                        os.makedirs(os.path.dirname(right_path), exist_ok=True)
                        shutil.copy2(left_path, right_path)
                        copied_count += 1
                elif direction == 'right_to_left':
                    if os.path.exists(right_path):
                        os.makedirs(os.path.dirname(left_path), exist_ok=True)
                        shutil.copy2(right_path, left_path)
                        copied_count += 1
            except Exception as e:
                error_count += 1
                messagebox.showerror("오류", f"파일 복사 실패: {rel_path}\n{str(e)}")

        if copied_count > 0:
            messagebox.showinfo("완료", f"{copied_count}개 파일이 복사되었습니다.")
            # 비교 다시 실행
            self.compare_folders()

    def delete_selected(self):
        """선택한 항목 삭제"""
        selected = self.folder_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 파일을 선택해주세요.")
            return

        if not messagebox.askyesno("확인", f"{len(selected)}개 파일을 삭제하시겠습니까?"):
            return

        left_folder = self.left_folder_var.get()
        right_folder = self.right_folder_var.get()

        deleted_count = 0

        for item in selected:
            rel_path = self.folder_tree.item(item, 'text')
            left_path = os.path.join(left_folder, rel_path)
            right_path = os.path.join(right_folder, rel_path)

            try:
                if os.path.exists(left_path):
                    os.remove(left_path)
                    deleted_count += 1
                if os.path.exists(right_path):
                    os.remove(right_path)
                    deleted_count += 1
            except Exception as e:
                messagebox.showerror("오류", f"파일 삭제 실패: {rel_path}\n{str(e)}")

        if deleted_count > 0:
            messagebox.showinfo("완료", f"{deleted_count}개 파일이 삭제되었습니다.")
            self.compare_folders()

    def compare_text(self):
        """텍스트 비교"""
        # 태그 제거
        self.text_left.tag_remove('diff', '1.0', 'end')
        self.text_right.tag_remove('diff', '1.0', 'end')

        left_text = self.text_left.get('1.0', 'end-1c')
        right_text = self.text_right.get('1.0', 'end-1c')

        left_lines = left_text.splitlines()
        right_lines = right_text.splitlines()

        # difflib로 차이점 찾기
        diff = difflib.unified_diff(left_lines, right_lines, lineterm='')

        # 차이점 하이라이트
        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace' or tag == 'delete':
                # 왼쪽에서 차이나는 부분
                for i in range(i1, i2):
                    start = f"{i+1}.0"
                    end = f"{i+1}.end"
                    self.text_left.tag_add('diff', start, end)

            if tag == 'replace' or tag == 'insert':
                # 오른쪽에서 차이나는 부분
                for j in range(j1, j2):
                    start = f"{j+1}.0"
                    end = f"{j+1}.end"
                    self.text_right.tag_add('diff', start, end)

        messagebox.showinfo("완료", "텍스트 비교가 완료되었습니다.\n차이나는 부분이 연한 붉은색으로 표시됩니다.")

    def apply_text(self, direction):
        """텍스트 적용"""
        if direction == 'to_left':
            right_text = self.text_right.get('1.0', 'end-1c')
            self.text_left.delete('1.0', 'end')
            self.text_left.insert('1.0', right_text)
        elif direction == 'to_right':
            left_text = self.text_left.get('1.0', 'end-1c')
            self.text_right.delete('1.0', 'end')
            self.text_right.insert('1.0', left_text)

        messagebox.showinfo("완료", "텍스트가 적용되었습니다.")

    def clear_text_comparison(self):
        """텍스트 비교 초기화"""
        self.text_left.delete('1.0', 'end')
        self.text_right.delete('1.0', 'end')
        self.text_left.tag_remove('diff', '1.0', 'end')
        self.text_right.tag_remove('diff', '1.0', 'end')

    def compare_files(self):
        """파일 내용 비교"""
        left_file = self.file_left_var.get()
        right_file = self.file_right_var.get()

        if not left_file or not right_file:
            messagebox.showwarning("경고", "두 파일을 모두 선택해주세요.")
            return

        if not os.path.exists(left_file) or not os.path.exists(right_file):
            messagebox.showerror("오류", "선택한 파일이 존재하지 않습니다.")
            return

        try:
            # 파일 읽기
            with open(left_file, 'r', encoding='utf-8') as f:
                left_content = f.read()

            with open(right_file, 'r', encoding='utf-8') as f:
                right_content = f.read()

            # 텍스트 위젯에 표시
            self.file_text_left.delete('1.0', 'end')
            self.file_text_right.delete('1.0', 'end')
            self.file_text_left.insert('1.0', left_content)
            self.file_text_right.insert('1.0', right_content)

            # 태그 제거
            self.file_text_left.tag_remove('diff', '1.0', 'end')
            self.file_text_right.tag_remove('diff', '1.0', 'end')

            # 차이점 하이라이트
            left_lines = left_content.splitlines()
            right_lines = right_content.splitlines()

            matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'replace' or tag == 'delete':
                    for i in range(i1, i2):
                        start = f"{i+1}.0"
                        end = f"{i+1}.end"
                        self.file_text_left.tag_add('diff', start, end)

                if tag == 'replace' or tag == 'insert':
                    for j in range(j1, j2):
                        start = f"{j+1}.0"
                        end = f"{j+1}.end"
                        self.file_text_right.tag_add('diff', start, end)

            messagebox.showinfo("완료", "파일 비교가 완료되었습니다.\n차이나는 부분이 연한 붉은색으로 표시됩니다.")

        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다:\n{str(e)}")

    def save_file(self, side):
        """파일 저장"""
        if side == 'left':
            filepath = self.file_left_var.get()
            content = self.file_text_left.get('1.0', 'end-1c')
        else:
            filepath = self.file_right_var.get()
            content = self.file_text_right.get('1.0', 'end-1c')

        if not filepath:
            messagebox.showwarning("경고", "저장할 파일을 선택해주세요.")
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("완료", "파일이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 실패:\n{str(e)}")


def main():
    root = tk.Tk()
    app = CompareToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
