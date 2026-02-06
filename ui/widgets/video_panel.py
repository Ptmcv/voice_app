# ui/widgets/video_panel.py
"""Панель обработки видео"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core.config import Config
from utils.video_processor import VideoProcessor

class VideoPanel(ttk.LabelFrame):
    """Панель обработки видео"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="🎥 Обработка видео", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Используем ТОЛЬКО pack для всех элементов
        
        # Микширование аудио
        audio_mix_frame = ttk.LabelFrame(self, text="Микширование аудио", padding=10)
        audio_mix_frame.pack(fill="x", pady=5)
        
        self.keep_original_audio_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(audio_mix_frame, text="✓ Оставить оригинальное аудио видео",
                       variable=self.keep_original_audio_var,
                       command=self.toggle_audio_mixing).pack(anchor="w", padx=5, pady=5)
        
        volume_frame = ttk.Frame(audio_mix_frame)
        volume_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(volume_frame, text="Громкость оригинала (%):").pack(side="left", padx=5)
        
        self.original_volume_var = tk.IntVar(value=30)
        self.volume_spinbox = ttk.Spinbox(
            volume_frame,
            from_=0, to=100,
            textvariable=self.original_volume_var,
            width=10,
            state='disabled',
            command=self.update_volume_label
        )
        self.volume_spinbox.pack(side="left", padx=5)
        
        self.volume_label = ttk.Label(volume_frame, text="30%", 
                                      foreground=Config.COLORS['accent'])
        self.volume_label.pack(side="left", padx=5)
        
        # Папка с видео
        video_input_frame = ttk.Frame(self)
        video_input_frame.pack(fill="x", pady=5)
        
        ttk.Label(video_input_frame, text="Папка с видео:").pack(side="left", padx=5)
        
        self.video_input_folder_var = tk.StringVar(value="")
        ttk.Entry(video_input_frame, textvariable=self.video_input_folder_var, width=25).pack(
            side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(video_input_frame, text="Обзор", 
                  command=self.select_video_input_folder).pack(side="left", padx=5)
        
        # Папка для видео
        video_output_frame = ttk.Frame(self)
        video_output_frame.pack(fill="x", pady=5)
        
        ttk.Label(video_output_frame, text="Папка для видео:").pack(side="left", padx=5)
        
        self.video_output_folder_var = tk.StringVar(value=Config.DEFAULT_OUTPUT_VIDEO)
        ttk.Entry(video_output_frame, textvariable=self.video_output_folder_var, width=25).pack(
            side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(video_output_frame, text="Обзор", 
                  command=self.select_video_output_folder).pack(side="left", padx=5)
        
        # Подгонка длины
        fit_frame = ttk.Frame(self)
        fit_frame.pack(fill="x", pady=5)
        
        ttk.Label(fit_frame, text="Подгонка длины:").pack(side="left", padx=5)
        
        self.video_fit_mode_var = tk.StringVar(value="fit")
        
        radio_frame = ttk.Frame(fit_frame)
        radio_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Radiobutton(radio_frame, text="Только обрезка",
                       variable=self.video_fit_mode_var,
                       value="trim").pack(anchor="w", pady=2)
        ttk.Radiobutton(radio_frame, text="✓ Растяжение/обрезка",
                       variable=self.video_fit_mode_var,
                       value="fit").pack(anchor="w", pady=2)
        ttk.Radiobutton(radio_frame, text="Без изменений",
                       variable=self.video_fit_mode_var,
                       value="none").pack(anchor="w", pady=2)
        
        # Кнопка обработки
        ttk.Button(self, text="🎬 Заменить звук в видео",
                  command=self.process_videos,
                  style='Accent.TButton').pack(fill="x", pady=10, padx=5)
    
    def toggle_audio_mixing(self):
        """Переключение микширования"""
        if self.keep_original_audio_var.get():
            self.volume_spinbox.config(state="normal")
        else:
            self.volume_spinbox.config(state="disabled")
    
    def update_volume_label(self, event=None):
        """Обновить метку громкости"""
        try:
            vol = self.original_volume_var.get()
            self.volume_label.config(text=f"{vol}%")
        except:
            pass
    
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
        """Обработать видео"""
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
        
        # Находим пары
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
                    keep_original=self.keep_original_audio_var.get(),
                    original_volume=self.original_volume_var.get()
                )
                
                if success:
                    success_count += 1
            except Exception as e:
                print(f"Ошибка обработки {pair['number']}: {e}")
        
        self.app.set_status(f"✓ Готово! Обработано: {success_count}/{len(pairs)}", success=True)
        messagebox.showinfo("Готово", f"Обработано видео: {success_count}/{len(pairs)}")
