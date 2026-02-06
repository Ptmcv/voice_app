# ui/widgets/video_replace_panel.py
"""Панель замены звука в видео"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core.config import Config
from utils.video_processor import VideoProcessor


class VideoReplacePanel(ttk.LabelFrame):
    """Панель замены звука в видео"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="🎬 Замена звука в видео", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Папка с видео
        ttk.Label(self, text="Папка с видео:").pack(anchor="w", padx=5, pady=(0, 2))
        
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", pady=(0, 5))
        
        self.video_input_folder_var = tk.StringVar(value="")
        ttk.Entry(
            input_frame, 
            textvariable=self.video_input_folder_var
        ).pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(
            input_frame, 
            text="📁", 
            command=self.select_video_input_folder,
            width=3
        ).pack(side="left")
        
        # Папка для результата
        ttk.Label(self, text="Папка для видео:").pack(anchor="w", padx=5, pady=(5, 2))
        
        output_frame = ttk.Frame(self)
        output_frame.pack(fill="x", pady=(0, 5))
        
        self.video_output_folder_var = tk.StringVar(value=Config.DEFAULT_OUTPUT_VIDEO)
        ttk.Entry(
            output_frame, 
            textvariable=self.video_output_folder_var
        ).pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(
            output_frame, 
            text="📁", 
            command=self.select_video_output_folder,
            width=3
        ).pack(side="left")
        
        # Подгонка длины видео
        fit_frame = ttk.LabelFrame(self, text="⚙️ Подгонка длины:", padding=5)
        fit_frame.pack(fill="x", pady=5)
        
        self.video_fit_mode_var = tk.StringVar(value="fit")
        
        ttk.Radiobutton(
            fit_frame, 
            text="Обрезка (trim)",
            variable=self.video_fit_mode_var,
            value="trim"
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            fit_frame, 
            text="✓ Растяжение/обрезка (fit)",
            variable=self.video_fit_mode_var,
            value="fit"
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            fit_frame, 
            text="Без изменений (none)",
            variable=self.video_fit_mode_var,
            value="none"
        ).pack(anchor="w", pady=2)
        
        # Кнопка обработки
        ttk.Button(
            self, 
            text="🎬 Заменить звук в видео",
            command=self.process_videos,
            style='Accent.TButton'
        ).pack(fill="x", pady=10)
        
        self.auto_detect_folders()
    
    def auto_detect_folders(self):
        """Автоопределение папок"""
        if hasattr(self.app, 'project_panel') and self.app.project_panel.current_project:
            project_name = self.app.project_panel.current_project
            project_base = self.app.project_panel.project_manager.base_folder
            
            video_folder = os.path.join(project_base, project_name, "видео")
            output_folder = os.path.join(project_base, project_name, "видео_с_озвучкой")
            
            if os.path.exists(video_folder):
                self.video_input_folder_var.set(video_folder)
            
            if os.path.exists(output_folder):
                self.video_output_folder_var.set(output_folder)
    
    def select_video_input_folder(self):
        """Выбрать папку с видео"""
        folder = filedialog.askdirectory(title="Выберите папку с видео")
        if folder:
            self.video_input_folder_var.set(folder)
    
    def select_video_output_folder(self):
        """Выбрать папку для видео"""
        folder = filedialog.askdirectory(title="Выберите папку для видео")
        if folder:
            self.video_output_folder_var.set(folder)
    
    def process_videos(self):
        """Обработать видео (заменить звук)"""
        video_folder = self.video_input_folder_var.get()
        audio_folder = self.app.settings_panel.output_folder_var.get()
        output_folder = self.video_output_folder_var.get()
        
        if not video_folder or not os.path.exists(video_folder):
            messagebox.showwarning("Предупреждение", "Выберите папку с видео")
            return
        
        if not audio_folder or not os.path.exists(audio_folder):
            messagebox.showwarning("Предупреждение", "Папка с аудио не найдена")
            return
        
        os.makedirs(output_folder, exist_ok=True)
        
        pairs = VideoProcessor.find_video_audio_pairs(video_folder, audio_folder)
        
        if not pairs:
            messagebox.showinfo("Информация", "Не найдено пар видео-аудио")
            return
        
        self.app.set_status(f"⚙ Обработка {len(pairs)} видео...")
        
        success_count = 0
        for i, pair in enumerate(pairs, 1):
            try:
                output_file = os.path.join(output_folder, f"{pair['number']}.mp4")
                
                self.app.set_status(f"⚙ Обработка {i}/{len(pairs)}: {pair['number']}")
                
                success, msg = VideoProcessor.process_single_video(
                    pair['video'],
                    pair['audio'],
                    output_file,
                    fit_mode=self.video_fit_mode_var.get(),
                    keep_original=self.app.audio_mix_panel.keep_original_audio_var.get(),
                    original_volume=self.app.audio_mix_panel.original_volume_var.get()
                )
                
                if success:
                    success_count += 1
            except Exception as e:
                print(f"Ошибка обработки {pair['number']}: {e}")
        
        self.app.set_status(f"✓ Готово! Обработано: {success_count}/{len(pairs)}", success=True)
        messagebox.showinfo("Готово", f"Обработано видео: {success_count}/{len(pairs)}")
