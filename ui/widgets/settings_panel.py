# ui/widgets/settings_panel.py
"""Панель настроек озвучивания"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from core.config import Config

class SettingsPanel(ttk.LabelFrame):
    """Панель настроек озвучивания"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="⚙️ Настройки озвучивания", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Row 0: Шаблон голоса
        ttk.Label(self, text="Шаблон голоса:", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky="w", padx=5, pady=8)
        
        from ui.widgets import VoicePreviewCombobox
        self.voice_preview = VoicePreviewCombobox(self, self.app)
        self.voice_preview.grid(row=0, column=1, padx=5, pady=8, sticky="ew", columnspan=4)
        
        # Row 1: Размер чанка и Режим
        ttk.Label(self, text="Размер чанка:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        chunk_frame = ttk.Frame(self)
        chunk_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        self.chunk_size_var = tk.IntVar(value=Config.DEFAULT_CHUNK_SIZE)
        self.chunk_spinbox = ttk.Spinbox(chunk_frame, from_=500, to=5000, increment=100,
                                         textvariable=self.chunk_size_var, width=10, state="disabled")
        self.chunk_spinbox.pack(side="left", padx=(0, 5))
        
        self.disable_chunks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chunk_frame, text="Без чанков (весь текст целиком)",
                       variable=self.disable_chunks_var,
                       command=self.toggle_chunk_size).pack(side="left")
        
        ttk.Label(self, text="Режим:").grid(row=1, column=2, sticky="w", padx=15, pady=5)
        
        self.mode_var = tk.StringVar(value="full")
        ttk.Radiobutton(self, text="Полностью", variable=self.mode_var,
                       value="full").grid(row=1, column=3, sticky="w", padx=5)
        ttk.Radiobutton(self, text="Построчно", variable=self.mode_var,
                       value="line_by_line").grid(row=1, column=4, sticky="w", padx=5)
        
        # Row 2: Пауза
        ttk.Label(self, text="Пауза в конце (сек):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.end_pause_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(self, from_=0.0, to=5.0, increment=0.1,
                   textvariable=self.end_pause_var, width=10).grid(
                       row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Row 3: Папка для аудио
        ttk.Label(self, text="Папка для аудио:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        self.output_folder_var = tk.StringVar(value=Config.DEFAULT_OUTPUT_AUDIO)
        ttk.Entry(self, textvariable=self.output_folder_var, width=30).grid(
            row=3, column=1, padx=5, pady=5, columnspan=3, sticky="ew")
        
        ttk.Button(self, text="Обзор", command=self.select_output_folder).grid(
            row=3, column=4, padx=5)
        
        self.columnconfigure(1, weight=1)
    
    def toggle_chunk_size(self):
        """Переключение размера чанка"""
        if self.disable_chunks_var.get():
            self.chunk_spinbox.config(state="disabled")
        else:
            self.chunk_spinbox.config(state="normal")
    
    def select_output_folder(self):
        """Выбрать папку для аудио"""
        folder = filedialog.askdirectory(title="Выберите папку для аудио")
        if folder:
            self.output_folder_var.set(folder)
    
    def get_settings(self):
        """Получить настройки"""
        return {
            'template': self.voice_preview.get_current_template(),
            'chunk_size': None if self.disable_chunks_var.get() else self.chunk_size_var.get(),
            'mode': self.mode_var.get(),
            'end_pause': self.end_pause_var.get(),
            'output_folder': self.output_folder_var.get()
        }
    
    def set_templates(self, templates):
        """Установить шаблоны"""
        self.voice_preview.set_templates(templates)
