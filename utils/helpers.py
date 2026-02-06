# utils/helpers.py
"""Вспомогательные функции"""

import os
import re
import platform
import subprocess

def open_file_in_system(filepath):
    """Открыть файл в системном приложении"""
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])
        return True
    except Exception as e:
        return False

def natural_sort_key(text):
    """Ключ для естественной сортировки (1, 2, 10 вместо 1, 10, 2)"""
    parts = re.split(r'(\d+)', text)
    return [int(part) if part.isdigit() else part.lower() for part in parts]

def safe_filename(name):
    """Безопасное имя файла (удаляет недопустимые символы)"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.')).strip()
