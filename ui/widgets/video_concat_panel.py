# ui/widgets/video_concat_panel.py
"""Панель склейки видео"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core.config import Config
from utils.video_processor import VideoProcessor


class VideoConcatPanel(ttk.LabelFrame):
    """Панель склейки видео"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="🎬 Монтаж видео", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Заголовок
        ttk.Label(self, text="Переходы между клипами:", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Тип перехода
        ttk.Label(self, text="Тип:").pack(anchor="w", padx=5, pady=2)
        
        self.transition_var = tk.StringVar(value="Без перехода")
        
        self.transitions_list = [
            ("Без перехода", "none"),
            ("Затухание", "fade"),
            ("Растворение", "dissolve"),
            ("Вытеснение ←", "wipeleft"),
            ("Вытеснение →", "wiperight"),
            ("Вытеснение ↑", "wipeup"),
            ("Вытеснение ↓", "wipedown"),
            ("Круговое открытие", "circleopen"),
            ("Увеличение", "zoomin")
        ]
        
        self.transition_mapping = {name: code for name, code in self.transitions_list}
        
        transition_combo = ttk.Combobox(
            self, 
            textvariable=self.transition_var,
            values=[t[0] for t in self.transitions_list],
            state="readonly"
        )
        transition_combo.pack(fill="x", padx=5, pady=5)
        transition_combo.current(0)
        
        # Длительность
        duration_frame = ttk.Frame(self)
        duration_frame.pack(fill="x", pady=5)
        
        ttk.Label(duration_frame, text="Длительность (сек):").pack(side="left", padx=5)
        
        self.transition_duration_var = tk.DoubleVar(value=0.5)
        ttk.Spinbox(
            duration_frame, 
            from_=0.1, to=3.0, increment=0.1,
            textvariable=self.transition_duration_var, 
            width=8
        ).pack(side="left", padx=5)
        
        # Описание
        ttk.Label(self, 
                 text="💡 Переходы применяются\nмежду всеми видео",
                 foreground=Config.COLORS['fg_dim'],
                 font=('Segoe UI', 8),
                 justify="left").pack(anchor="w", padx=5, pady=5)
        
        # Разделитель
        ttk.Separator(self, orient='horizontal').pack(fill="x", pady=10)
        
        # Папка с видео
        ttk.Label(self, text="Папка с видео:").pack(anchor="w", padx=5, pady=(0, 2))
        
        folder_frame = ttk.Frame(self)
        folder_frame.pack(fill="x", pady=(0, 10))
        
        self.video_folder_var = tk.StringVar(value="")
        ttk.Entry(
            folder_frame, 
            textvariable=self.video_folder_var
        ).pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(
            folder_frame, 
            text="📁", 
            command=self.select_folder,
            width=3
        ).pack(side="left")
        
        # Кнопка склейки
        ttk.Button(
            self, 
            text="🔗 Склеить все видео",
            command=self.concatenate_videos,
            style='Accent.TButton'
        ).pack(fill="x", pady=10)
        
        self.auto_detect_folder()
    
    def auto_detect_folder(self):
        """Автоопределение папки"""
        if hasattr(self.app, 'project_panel') and self.app.project_panel.current_project:
            project_name = self.app.project_panel.current_project
            project_base = self.app.project_panel.project_manager.base_folder
            output_folder = os.path.join(project_base, project_name, "видео_с_озвучкой")
            
            if os.path.exists(output_folder):
                self.video_folder_var.set(output_folder)
    
    def select_folder(self):
        """Выбрать папку"""
        folder = filedialog.askdirectory(title="Выберите папку с видео")
        if folder:
            self.video_folder_var.set(folder)
    
    def concatenate_videos(self):
        """Склеить видео"""
        output_folder = self.video_folder_var.get()
        
        if not output_folder or not os.path.exists(output_folder):
            messagebox.showwarning("Предупреждение", "Выберите папку с видео")
            return
        
        video_files = []
        for filename in sorted(os.listdir(output_folder)):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                if filename != "FINAL_VIDEO.mp4":
                    video_files.append(os.path.join(output_folder, filename))
        
        if len(video_files) < 2:
            messagebox.showinfo("Информация", "Нужно минимум 2 видео для склейки")
            return
        
        final_output = os.path.join(output_folder, "FINAL_VIDEO.mp4")
        
        transition_name = self.transition_var.get()
        transition_code = self.transition_mapping.get(transition_name, "none")
        transition_duration = self.transition_duration_var.get()
        
        self.app.set_status(f"⚙ Склейка {len(video_files)} видео...")
        
        try:
            success, result = VideoProcessor.concatenate_videos_with_transitions(
                video_files=video_files,
                output_file=final_output,
                transition_type=transition_code,
                duration=transition_duration
            )
            
            if success:
                self.app.set_status(f"✓ Видео склеено!", success=True)
                messagebox.showinfo("Успех", f"✅ Видео успешно склеено!\n\n📁 {final_output}")
            else:
                self.app.set_status(f"✗ Ошибка склейки", success=False)
                messagebox.showerror("Ошибка", f"Не удалось склеить видео:\n{result}")
        
        except Exception as e:
            self.app.set_status(f"✗ Ошибка: {e}", success=False)
            messagebox.showerror("Ошибка", f"Ошибка склейки видео:\n{e}")
