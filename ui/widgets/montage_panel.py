# ui/widgets/montage_panel.py
"""Панель монтажа видео"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core.config import Config
from utils.video_processor import VideoProcessor

class MontagePanel(ttk.LabelFrame):
    """Панель монтажа видео"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="🎬 Монтаж видео", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Входная папка
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", pady=5)
        
        ttk.Label(input_frame, text="Папка с видео:").pack(side="left", padx=5)
        
        self.montage_input_var = tk.StringVar(value="")
        ttk.Entry(input_frame, textvariable=self.montage_input_var, width=20).pack(
            side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(input_frame, text="📁", width=3,
                  command=self.select_input).pack(side="left", padx=2)
        
        # Выходной файл
        output_frame = ttk.Frame(self)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Label(output_frame, text="Итоговое видео:").pack(side="left", padx=5)
        
        self.montage_output_var = tk.StringVar(value=os.path.join(os.getcwd(), "final_video.mp4"))
        ttk.Entry(output_frame, textvariable=self.montage_output_var, width=20).pack(
            side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(output_frame, text="📁", width=3,
                  command=self.select_output).pack(side="left", padx=2)
        
        # Переходы
        transition_frame = ttk.LabelFrame(self, text="Переходы между клипами", padding=10)
        transition_frame.pack(fill="x", pady=10)
        
        self.use_transitions_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(transition_frame, text="✓ Использовать переходы",
                       variable=self.use_transitions_var,
                       command=self.toggle_transitions).pack(anchor="w", pady=5)
        
        # Тип перехода
        type_frame = ttk.Frame(transition_frame)
        type_frame.pack(fill="x", pady=5)
        
        ttk.Label(type_frame, text="Тип перехода:").pack(side="left", padx=5)
        
        self.transition_type_var = tk.StringVar(value="crossfade")
        self.transition_combo = ttk.Combobox(type_frame, 
                                            textvariable=self.transition_type_var,
                                            state="disabled",
                                            width=18)
        self.transition_combo['values'] = [
            "crossfade",      # Плавное затухание
            "fade",           # Затухание через чёрный
            "slide_left",     # Слайд влево
            "slide_right",    # Слайд вправо
            "slide_up",       # Слайд вверх
            "slide_down",     # Слайд вниз
            "wipe",           # Вытеснение
            "dissolve"        # Растворение
        ]
        self.transition_combo.pack(side="left", padx=5)
        
        # Длительность перехода
        duration_frame = ttk.Frame(transition_frame)
        duration_frame.pack(fill="x", pady=5)
        
        ttk.Label(duration_frame, text="Длительность (сек):").pack(side="left", padx=5)
        
        self.transition_duration_var = tk.DoubleVar(value=0.5)
        self.transition_spinbox = ttk.Spinbox(
            duration_frame,
            from_=0.1, to=3.0, increment=0.1,
            textvariable=self.transition_duration_var,
            width=10,
            state="disabled"
        )
        self.transition_spinbox.pack(side="left", padx=5)
        
        # Описания переходов
        desc_frame = ttk.Frame(transition_frame)
        desc_frame.pack(fill="x", pady=5)
        
        self.transition_desc_label = ttk.Label(desc_frame, 
                                              text="ℹ️ Плавное затухание: один клип плавно переходит в другой",
                                              foreground=Config.COLORS['fg_dim'],
                                              font=('Segoe UI', 8),
                                              wraplength=350)
        self.transition_desc_label.pack(anchor="w", padx=5)
        
        # Обновление описания при выборе
        self.transition_combo.bind('<<ComboboxSelected>>', self.update_transition_description)
        
        # Кнопка монтажа
        ttk.Button(self, text="🎬 Смонтировать видео",
                  command=self.montage_video,
                  style='Accent.TButton').pack(fill="x", pady=15, padx=5)
    
    def toggle_transitions(self):
        """Переключение переходов"""
        if self.use_transitions_var.get():
            self.transition_spinbox.config(state="normal")
            self.transition_combo.config(state="readonly")
        else:
            self.transition_spinbox.config(state="disabled")
            self.transition_combo.config(state="disabled")
    
    def update_transition_description(self, event=None):
        """Обновить описание перехода"""
        descriptions = {
            "crossfade": "ℹ️ Плавное затухание: один клип плавно переходит в другой",
            "fade": "ℹ️ Затухание: переход через чёрный экран",
            "slide_left": "ℹ️ Слайд влево: новый клип выезжает слева",
            "slide_right": "ℹ️ Слайд вправо: новый клип выезжает справа",
            "slide_up": "ℹ️ Слайд вверх: новый клип выезжает снизу вверх",
            "slide_down": "ℹ️ Слайд вниз: новый клип выезжает сверху вниз",
            "wipe": "ℹ️ Вытеснение: новый клип вытесняет старый",
            "dissolve": "ℹ️ Растворение: клипы растворяются друг в друге"
        }
        
        trans_type = self.transition_type_var.get()
        desc = descriptions.get(trans_type, "")
        self.transition_desc_label.config(text=desc)
    
    def select_input(self):
        """Выбрать входную папку"""
        folder = filedialog.askdirectory(title="Выберите папку с видео для монтажа")
        if folder:
            self.montage_input_var.set(folder)
    
    def select_output(self):
        """Выбрать выходной файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить итоговое видео",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if filename:
            self.montage_output_var.set(filename)
    
    def montage_video(self):
        """Смонтировать видео"""
        input_folder = self.montage_input_var.get()
        output_file = self.montage_output_var.get()
        
        if not input_folder or not os.path.exists(input_folder):
            messagebox.showwarning("Предупреждение", "Выберите папку с видео")
            return
        
        if not output_file:
            messagebox.showwarning("Предупреждение", "Укажите выходной файл")
            return
        
        self.app.set_status("⚙ Монтаж видео...")
        
        try:
            success, msg = VideoProcessor.montage_videos(
                input_folder,
                output_file,
                use_transitions=self.use_transitions_var.get(),
                transition_type=self.transition_type_var.get(),
                transition_duration=self.transition_duration_var.get()
            )
            
            if success:
                self.app.set_status("✓ Монтаж завершён!", success=True)
                messagebox.showinfo("Готово", msg)
            else:
                self.app.set_status("✗ Ошибка монтажа", error=True)
                messagebox.showerror("Ошибка", msg)
        
        except Exception as e:
            self.app.set_status("✗ Ошибка", error=True)
            messagebox.showerror("Ошибка", f"Не удалось смонтировать: {e}")
