# ui/settings_window.py
"""Окно настроек приложения (полная версия)"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core.config import Config
from core.api_client import VoiceAPIClient

class SettingsWindow:
    """Окно настроек"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Настройки")
        self.window.geometry("800x600")
        self.window.configure(bg=Config.COLORS['bg'])
        self.window.transient(parent)
        
        # Центрируем
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Notebook (вкладки)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка 1: API
        api_tab = ttk.Frame(notebook, padding=20)
        notebook.add(api_tab, text="🔑 API")
        self.create_api_tab(api_tab)
        
        # Вкладка 2: Проекты
        projects_tab = ttk.Frame(notebook, padding=20)
        notebook.add(projects_tab, text="📁 Проекты")
        self.create_projects_tab(projects_tab)
        
        # Вкладка 3: Озвучка
        voice_tab = ttk.Frame(notebook, padding=20)
        notebook.add(voice_tab, text="🎤 Озвучка")
        self.create_voice_tab(voice_tab)
        
        # Вкладка 4: Видео
        video_tab = ttk.Frame(notebook, padding=20)
        notebook.add(video_tab, text="🎥 Видео")
        self.create_video_tab(video_tab)
        
        # Кнопка закрытия
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="✓ Применить и закрыть", command=self.close,
                  style='Accent.TButton').pack(side="right", padx=5)
    
    def create_api_tab(self, parent):
        """Вкладка API"""
        ttk.Label(parent, text="Настройки API", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=10)
        
        # API Key
        api_frame = ttk.LabelFrame(parent, text="API Ключ", padding=10)
        api_frame.pack(fill="x", pady=10)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        settings = self.app.settings_manager.load_settings()
        self.api_key_var = tk.StringVar(value=settings.get("api_key", ""))
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        show_var = tk.BooleanVar(value=False)
        def toggle_show():
            api_entry.config(show="" if show_var.get() else "*")
        
        ttk.Checkbutton(api_frame, text="Показать", variable=show_var,
                       command=toggle_show).grid(row=0, column=2, padx=5)
        
        # Кнопка загрузки шаблонов
        ttk.Button(api_frame, text="🔄 Загрузить шаблоны",
                  command=self.load_templates,
                  style='Accent.TButton').grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        
        self.templates_status_label = ttk.Label(api_frame, text="", 
                                               foreground=Config.COLORS['fg_dim'])
        self.templates_status_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        api_frame.columnconfigure(1, weight=1)
        
        # Текст для примеров
        preview_frame = ttk.LabelFrame(parent, text="Текст для примеров голосов", padding=10)
        preview_frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(preview_frame, text="Этот текст будет озвучиваться при создании примеров:").pack(
            anchor="w", pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=5, width=60,
                                    bg=Config.COLORS['input_bg'],
                                    fg=Config.COLORS['fg'],
                                    font=('Segoe UI', 10))
        self.preview_text.pack(fill="both", expand=True, pady=5)
        self.preview_text.insert("1.0", self.app.preview_text)
    
    def create_projects_tab(self, parent):
        """Вкладка проектов"""
        ttk.Label(parent, text="Настройки проектов", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=10)
        
        # Папка проектов
        folder_frame = ttk.LabelFrame(parent, text="Расположение проектов", padding=10)
        folder_frame.pack(fill="x", pady=10)
        
        ttk.Label(folder_frame, text="Папка для проектов:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.projects_folder_var = tk.StringVar(
            value=self.app.project_panel.project_manager.base_folder)
        
        ttk.Entry(folder_frame, textvariable=self.projects_folder_var, width=50).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(folder_frame, text="Обзор", 
                  command=self.select_projects_folder).grid(row=0, column=2, padx=5)
        
        folder_frame.columnconfigure(1, weight=1)
        
        # Структура проекта
        structure_frame = ttk.LabelFrame(parent, text="Структура проекта", padding=10)
        structure_frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(structure_frame, text="Папки, которые создаются в новом проекте:",
                 font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=5)
        
        folders_info = [
            ("✓ картинки", "Папка для сохранения изображений"),
            ("✓ видео", "Папка для исходных видео"),
            ("✓ озвучка", "Папка для озвученных аудио файлов"),
            ("✓ видео_с_озвучкой", "Папка для видео с добавленной озвучкой")
        ]
        
        for folder_name, description in folders_info:
            ttk.Label(structure_frame, text=folder_name,
                     font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=2)
            
            ttk.Label(structure_frame, text=f"   {description}",
                     foreground=Config.COLORS['fg_dim'],
                     font=('Segoe UI', 8)).pack(anchor="w", padx=20)
    
    def create_voice_tab(self, parent):
        """Вкладка озвучки"""
        ttk.Label(parent, text="Настройки озвучивания", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=10)
        
        # Режим по умолчанию
        mode_frame = ttk.LabelFrame(parent, text="Режим озвучивания по умолчанию", padding=10)
        mode_frame.pack(fill="x", pady=10)
        
        self.default_mode_var = tk.StringVar(value=self.app.settings_panel.mode_var.get())
        
        ttk.Radiobutton(mode_frame, text="Полностью (весь текст одним файлом)",
                       variable=self.default_mode_var, value="full").pack(anchor="w", pady=5)
        ttk.Radiobutton(mode_frame, text="Построчно (каждая строка - отдельный файл)",
                       variable=self.default_mode_var, value="line_by_line").pack(anchor="w", pady=5)
        
        # Чанки
        chunk_frame = ttk.LabelFrame(parent, text="Размер чанка", padding=10)
        chunk_frame.pack(fill="x", pady=10)
        
        self.disable_chunks_var = tk.BooleanVar(
            value=self.app.settings_panel.disable_chunks_var.get())
        
        ttk.Checkbutton(chunk_frame, text="Без чанков (весь текст целиком)",
                       variable=self.disable_chunks_var).pack(anchor="w", pady=5)
        
        chunk_size_frame = ttk.Frame(chunk_frame)
        chunk_size_frame.pack(fill="x", pady=5)
        
        ttk.Label(chunk_size_frame, text="Размер чанка (символов):").pack(side="left", padx=5)
        
        self.chunk_size_var = tk.IntVar(value=self.app.settings_panel.chunk_size_var.get())
        ttk.Spinbox(chunk_size_frame, from_=500, to=5000, increment=100,
                   textvariable=self.chunk_size_var, width=10).pack(side="left", padx=5)
        
        # Пауза
        pause_frame = ttk.LabelFrame(parent, text="Пауза в конце", padding=10)
        pause_frame.pack(fill="x", pady=10)
        
        pause_inner = ttk.Frame(pause_frame)
        pause_inner.pack(fill="x")
        
        ttk.Label(pause_inner, text="Пауза в конце (секунд):").pack(side="left", padx=5)
        
        self.end_pause_var = tk.DoubleVar(value=self.app.settings_panel.end_pause_var.get())
        ttk.Spinbox(pause_inner, from_=0.0, to=5.0, increment=0.1,
                   textvariable=self.end_pause_var, width=10).pack(side="left", padx=5)
    
    def create_video_tab(self, parent):
        """Вкладка видео"""
        ttk.Label(parent, text="Настройки обработки видео", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=10)
        
        # Подгонка длины
        fit_frame = ttk.LabelFrame(parent, text="Подгонка длины видео", padding=10)
        fit_frame.pack(fill="x", pady=10)
        
        self.video_fit_mode_var = tk.StringVar(
            value=self.app.video_panel.video_fit_mode_var.get())
        
        ttk.Radiobutton(fit_frame, text="Только обрезка (видео обрезается под аудио)",
                       variable=self.video_fit_mode_var, value="trim").pack(anchor="w", pady=5)
        ttk.Radiobutton(fit_frame, text="Растяжение/обрезка (видео подгоняется под аудио)",
                       variable=self.video_fit_mode_var, value="fit").pack(anchor="w", pady=5)
        ttk.Radiobutton(fit_frame, text="Без изменений (видео остается как есть)",
                       variable=self.video_fit_mode_var, value="none").pack(anchor="w", pady=5)
        
        # Микширование
        mix_frame = ttk.LabelFrame(parent, text="Микширование аудио", padding=10)
        mix_frame.pack(fill="x", pady=10)
        
        self.keep_original_var = tk.BooleanVar(
            value=self.app.video_panel.keep_original_audio_var.get())
        
        ttk.Checkbutton(mix_frame, text="Оставлять оригинальное аудио видео",
                       variable=self.keep_original_var).pack(anchor="w", pady=5)
        
        vol_frame = ttk.Frame(mix_frame)
        vol_frame.pack(fill="x", pady=5)
        
        ttk.Label(vol_frame, text="Громкость оригинала (%):").pack(side="left", padx=5)
        
        self.original_volume_var = tk.IntVar(
            value=self.app.video_panel.original_volume_var.get())
        ttk.Spinbox(vol_frame, from_=0, to=100,
                   textvariable=self.original_volume_var, width=10).pack(side="left", padx=5)
    
    def select_projects_folder(self):
        """Выбрать папку для проектов"""
        folder = filedialog.askdirectory(title="Выберите папку для проектов")
        if folder:
            self.projects_folder_var.set(folder)
    
    def load_templates(self):
        """Загрузить шаблоны"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Предупреждение", "Введите API Key")
            return
        
        try:
            self.templates_status_label.config(text="⚙ Загрузка шаблонов...", 
                                              foreground=Config.COLORS['fg'])
            self.window.update()
            
            api = VoiceAPIClient(api_key)
            success, templates = api.get_templates()
            
            if success:
                self.app.set_templates(templates)
                self.templates_status_label.config(
                    text=f"✓ Загружено шаблонов: {len(templates)}",
                    foreground=Config.COLORS['success'])
                messagebox.showinfo("Успех", f"Загружено шаблонов: {len(templates)}")
            else:
                self.templates_status_label.config(
                    text="✗ Ошибка загрузки",
                    foreground=Config.COLORS['error'])
                messagebox.showerror("Ошибка", "Не удалось загрузить шаблоны")
        
        except Exception as e:
            self.templates_status_label.config(
                text="✗ Ошибка",
                foreground=Config.COLORS['error'])
            messagebox.showerror("Ошибка", f"Не удалось загрузить шаблоны: {e}")
    
    def close(self):
        """Закрыть окно и сохранить настройки"""
        # Сохраняем API ключ
        api_key = self.api_key_var.get().strip()
        
        # Применяем настройки
        self.app.preview_text = self.preview_text.get("1.0", "end-1c").strip()
        
        # Обновляем папку проектов
        new_folder = self.projects_folder_var.get()
        if new_folder and os.path.exists(new_folder):
            self.app.project_panel.project_manager.base_folder = new_folder
        
        # Применяем настройки озвучки
        self.app.settings_panel.mode_var.set(self.default_mode_var.get())
        self.app.settings_panel.disable_chunks_var.set(self.disable_chunks_var.get())
        self.app.settings_panel.chunk_size_var.set(self.chunk_size_var.get())
        self.app.settings_panel.end_pause_var.set(self.end_pause_var.get())
        self.app.settings_panel.toggle_chunk_size()
        
        # Применяем настройки видео
        self.app.video_panel.video_fit_mode_var.set(self.video_fit_mode_var.get())
        self.app.video_panel.keep_original_audio_var.set(self.keep_original_var.get())
        self.app.video_panel.original_volume_var.set(self.original_volume_var.get())
        self.app.video_panel.toggle_audio_mixing()
        
        # Сохраняем всё включая API key
        settings = self.app.settings_manager.load_settings()
        settings["api_key"] = api_key
        settings["projects_folder"] = new_folder if new_folder else settings.get("projects_folder", "")
        settings["mode"] = self.default_mode_var.get()
        settings["disable_chunks"] = self.disable_chunks_var.get()
        settings["chunk_size"] = self.chunk_size_var.get()
        settings["end_pause"] = self.end_pause_var.get()
        settings["video_fit_mode"] = self.video_fit_mode_var.get()
        settings["keep_original_audio"] = self.keep_original_var.get()
        settings["original_volume"] = self.original_volume_var.get()
        settings["preview_text"] = self.app.preview_text
        
        self.app.settings_manager.save_settings(settings)
        
        self.window.destroy()
