# ui/widgets/text_panel.py
"""Панель ввода текста"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
from core.config import Config

class TextPanel(ttk.LabelFrame):
    """Панель для ввода текста"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="📝 Текст для озвучивания", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопки
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Button(btn_frame, text="Загрузить из файла", 
                  command=self.load_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить", 
                  command=self.clear_text).pack(side="left", padx=5)
        
        # Текстовое поле
        self.text_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            height=12,
            bg=Config.COLORS['input_bg'],
            fg=Config.COLORS['fg'],
            insertbackground=Config.COLORS['fg'],
            selectbackground=Config.COLORS['accent'],
            selectforeground=Config.COLORS['fg'],
            font=('Segoe UI', 10)
        )
        self.text_area.pack(fill="both", expand=True)
    
    def get_text(self):
        """Получить текст"""
        return self.text_area.get("1.0", "end-1c").strip()
    
    def set_text(self, text):
        """Установить текст"""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
    
    def load_file(self):
        """Загрузить текст из файла"""
        filename = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.set_text(content)
                self.app.set_status(f"✓ Загружен: {os.path.basename(filename)}", success=True)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def clear_text(self):
        """Очистить текст"""
        self.text_area.delete("1.0", tk.END)
        self.app.set_status("✓ Текст очищен", success=True)
