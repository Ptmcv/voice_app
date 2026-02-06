# ui/widgets/audio_mix_panel.py
"""Панель микширования аудио"""

import tkinter as tk
from tkinter import ttk
from core.config import Config


class AudioMixPanel(ttk.LabelFrame):
    """Панель микширования аудио"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="🔊 Микширование аудио", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        self.keep_original_audio_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            self, 
            text="✓ Оставить оригинальное аудио видео",
            variable=self.keep_original_audio_var,
            command=self.toggle_audio_mixing
        ).pack(anchor="w", pady=5)
        
        volume_frame = ttk.Frame(self)
        volume_frame.pack(fill="x", pady=5)
        
        ttk.Label(volume_frame, text="Громкость оригинала (%):").pack(side="left", padx=5)
        
        self.original_volume_var = tk.IntVar(value=25)
        self.volume_spinbox = ttk.Spinbox(
            volume_frame,
            from_=0, to=100,
            textvariable=self.original_volume_var,
            width=10,
            state='disabled'
        )
        self.volume_spinbox.pack(side="left", padx=5)
        
        ttk.Label(volume_frame, text="← Рекомендуется 25%",
                 foreground=Config.COLORS['fg_dim'],
                 font=('Segoe UI', 8)).pack(side="left", padx=5)
    
    def toggle_audio_mixing(self):
        """Переключение микширования"""
        if self.keep_original_audio_var.get():
            self.volume_spinbox.config(state="normal")
        else:
            self.volume_spinbox.config(state="disabled")
