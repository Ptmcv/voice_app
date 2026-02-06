# ui/main_window.py
"""Главное окно приложения"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
from core.config import Config
from core.api_client import VoiceAPIClient
from core.settings_manager import SettingsManager
from ui.theme import DarkTheme
from ui.widgets import (
    APIPanel, TextPanel, SettingsPanel, 
    VideoPanel, ToolsPanel, MontagePanel, ProjectPanel  
)
from utils.audio_processor import AudioProcessor
from utils.helpers import open_file_in_system

class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(Config.APP_NAME)
        self.root.state('zoomed')
        
        # Состояние
        self.is_running = False
        self.preview_text = Config.DEFAULT_PREVIEW_TEXT
        self.adjust_speed_var = tk.BooleanVar(value=False)  # ← ДОБАВЛЕНО!
        
        # Менеджер настроек
        self.settings_manager = SettingsManager()
        
        # Применяем тему
        self.colors = DarkTheme.apply_to_root(root)
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем настройки
        self.load_settings()
        
        # Автозагрузка шаблонов
        self.root.after(Config.AUTO_LOAD_DELAY, self.auto_load_templates_on_start)
        
        # Автосохранение при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    
    def on_closing(self):
        """Обработка закрытия окна"""
        self.auto_save_settings()
        self.root.destroy()

    def auto_save_settings(self):
        """Автоматическое сохранение настроек"""
        settings = {
            "projects_folder": self.project_panel.project_manager.base_folder,
            "output_folder": self.settings_panel.output_folder_var.get(),
            "video_input_folder": self.video_panel.video_input_folder_var.get(),
            "video_output_folder": self.video_panel.video_output_folder_var.get(),
            "chunk_size": self.settings_panel.chunk_size_var.get(),
            "disable_chunks": self.settings_panel.disable_chunks_var.get(),
            "mode": self.settings_panel.mode_var.get(),
            "end_pause": self.settings_panel.end_pause_var.get(),
            "adjust_speed": self.adjust_speed_var.get(),
            "target_duration": self.target_duration_var.get(),
            "keep_original_audio": self.video_panel.keep_original_audio_var.get(),
            "original_volume": self.video_panel.original_volume_var.get(),
            "video_fit_mode": self.video_panel.video_fit_mode_var.get(),
            "preview_text": self.preview_text,
            "use_transitions": self.montage_panel.use_transitions_var.get(),
            "transition_duration": self.montage_panel.transition_duration_var.get(),
            "transition_type": getattr(self.montage_panel, 'transition_type_var', tk.StringVar(value="crossfade")).get()
        }
        
        self.settings_manager.save_settings(settings)

        

    def create_widgets(self):
        """Создать виджеты"""
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 3 колонки с ТОЧНЫМИ пропорциями 45%/35%/20%
        main_container.columnconfigure(0, weight=40)  # Левая 45%
        main_container.columnconfigure(1, weight=40)  # Средняя 35%
        main_container.columnconfigure(2, weight=20)  # Правая 20%
        
        # Левая колонка (45%)
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Средняя колонка (35%)
        middle_column = ttk.Frame(main_container)
        middle_column.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Правая колонка (20%)
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        # === ЛЕВАЯ КОЛОНКА (45%) ===
        self.project_panel = ProjectPanel(left_column, self)
        self.project_panel.pack(fill="x", pady=5)
        
        self.text_panel = TextPanel(left_column, self)
        self.text_panel.pack(fill="both", expand=True, pady=5)
        
        self.settings_panel = SettingsPanel(left_column, self)
        self.settings_panel.pack(fill="x", pady=5)
        
        # Настройка скорости
        speed_frame = ttk.LabelFrame(left_column, text="Настройка длительности аудио", padding=10)
        speed_frame.pack(fill="x", pady=5)
        
        speed_inner = ttk.Frame(speed_frame)
        speed_inner.pack(fill="x")
        
        ttk.Checkbutton(speed_inner, text="Изменить длительность:", 
                    variable=self.adjust_speed_var,
                    command=self.toggle_speed_adjustment).pack(side="left", padx=5)
        
        ttk.Label(speed_inner, text="Целевая длительность (сек):").pack(side="left", padx=5)
        
        self.target_duration_var = tk.DoubleVar(value=8.0)
        self.duration_spinbox = ttk.Spinbox(speed_inner, from_=1.0, to=60.0, increment=0.5,
                                            textvariable=self.target_duration_var, width=10,
                                            state="disabled")
        self.duration_spinbox.pack(side="left", padx=5)
        
        # Кнопки действий
        action_frame = ttk.Frame(left_column, padding=10)
        action_frame.pack(fill="x", pady=5)
        
        self.start_button = ttk.Button(action_frame, text="🎤 Начать озвучивание",
                                    command=self.start_synthesis,
                                    style='Accent.TButton')
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(action_frame, text="⏹ Остановить",
                                    command=self.stop_synthesis, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="⚙️ Настройки",
                command=self.open_settings).pack(side="right", padx=5)
        
        # === СРЕДНЯЯ КОЛОНКА (35%) ===
        self.video_panel = VideoPanel(middle_column, self)
        self.video_panel.pack(fill="both", expand=True, pady=5)
        
        self.tools_panel = ToolsPanel(middle_column, self)
        self.tools_panel.pack(fill="x", pady=5)
        
        # === ПРАВАЯ КОЛОНКА (20%) ===
        self.montage_panel = MontagePanel(right_column, self)
        self.montage_panel.pack(fill="both", expand=True, pady=5)
        
        # === СТАТУС-БАР (ВНИЗУ ЭКРАНА) ===
        status_container = ttk.Frame(self.root)
        status_container.pack(fill="x", side="bottom", padx=10, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(status_container, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.status_label = ttk.Label(status_container, text="✓ Готов к работе",
                                    foreground=self.colors['success'])
        self.status_label.pack(fill="x")

    
    def toggle_speed_adjustment(self):
        """Переключение регулировки скорости"""
        if self.adjust_speed_var.get():
            self.duration_spinbox.config(state="normal")
        else:
            self.duration_spinbox.config(state="disabled")

    def open_settings(self):
        """Открыть окно настроек"""
        from ui.settings_window import SettingsWindow
        SettingsWindow(self.root, self)

    
    def auto_load_templates_on_start(self):
        """Автозагрузка шаблонов при запуске"""
        api_key = self.api_panel.get_api_key()
        if api_key and len(api_key) > 10:
            try:
                self.api_panel.check_balance(show_message=False)
                self.api_panel.load_templates(show_message=False)
            except:
                pass


    
    def set_status(self, text, success=False, error=False):
        """Установить статус"""
        if success:
            self.status_label.config(text=text, foreground=self.colors['success'])
        elif error:
            self.status_label.config(text=text, foreground=self.colors['error'])
        else:
            self.status_label.config(text=text, foreground=self.colors['fg'])
        self.root.update()
    
    def set_templates(self, templates):
        """Установить шаблоны"""
        self.templates = templates
        self.settings_panel.set_templates(templates)
    
    def start_synthesis(self):
        """Начать озвучивание"""
        text = self.text_panel.get_text()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для озвучивания")
            return
        
        api_key = self.get_api_key()
        if not api_key:
            messagebox.showwarning("Предупреждение", "Введите API Key")
            return
        
        settings = self.settings_panel.get_settings()
        template = settings['template']
        
        if not template:
            messagebox.showwarning("Предупреждение", "Выберите шаблон голоса")
            return
        
        output_folder = settings['output_folder']
        os.makedirs(output_folder, exist_ok=True)
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        mode = settings['mode']
        if mode == "full":
            self.synthesize_full(text, template, api_key, output_folder, settings)
        else:
            self.synthesize_line_by_line(text, template, api_key, output_folder, settings)
    
    def synthesize_full(self, text, template, api_key, output_folder, settings):
        """Озвучить весь текст"""
        try:
            api = VoiceAPIClient(api_key)
            template_uuid = template.get('uuid')
            
            self.set_status("⚙ Создание задачи...")
            
            success, result = api.create_task(text, template_uuid, settings['chunk_size'])
            
            if not success:
                messagebox.showerror("Ошибка", f"Ошибка API: {result}")
                self.set_status("✗ Ошибка", error=True)
                return
            
            task_id = result.get("task_id")
            self.set_status(f"⚙ Задача #{task_id} создана")
            
            # Ждем завершения
            def status_callback(status, status_data, attempt):
                if not self.is_running:
                    return
                status_label = status_data.get("status_label", status)
                self.set_status(f"⚙ {status_label} ({attempt}с)")
            
            success, result = api.wait_for_task(task_id, callback=status_callback)
            
            if not self.is_running:
                self.set_status("⏹ Остановлено", error=True)
                return
            
            if success:
                # Получаем результат
                success, content = api.get_task_result(task_id)
                
                if success:
                    # Сохраняем
                    ext = ".zip" if b'PK' in content[:10] else ".mp3"
                    output_file = os.path.join(output_folder, f"output{ext}")
                    
                    if os.path.exists(output_file):
                        timestamp = int(time.time())
                        output_file = os.path.join(output_folder, f"output_{timestamp}{ext}")
                    
                    with open(output_file, 'wb') as f:
                        f.write(content)
                    
                    # Добавляем паузу
                    if settings['end_pause'] > 0 and ext == ".mp3":
                        AudioProcessor.add_end_pause(output_file, settings['end_pause'])
                    
                    # Изменяем скорость
                    if self.adjust_speed_var.get() and ext == ".mp3":
                        AudioProcessor.adjust_duration(output_file, self.target_duration_var.get())
                    
                    self.set_status(f"✓ Готово! {os.path.basename(output_file)}", success=True)
                    open_file_in_system(output_file)
                else:
                    messagebox.showerror("Ошибка", "Не удалось получить результат")
                    self.set_status("✗ Ошибка", error=True)
            else:
                messagebox.showerror("Ошибка", f"Ошибка: {result}")
                self.set_status("✗ Ошибка", error=True)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
            self.set_status("✗ Ошибка", error=True)
        
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def synthesize_line_by_line(self, text, template, api_key, output_folder, settings):
        """Озвучить построчно"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            messagebox.showwarning("Предупреждение", "Нет строк для озвучивания")
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            return
        
        self.progress_bar["maximum"] = len(lines)
        self.progress_bar["value"] = 0
        
        api = VoiceAPIClient(api_key)
        template_uuid = template.get('uuid')
        
        completed = 0
        errors = []
        
        for i, line in enumerate(lines, 1):
            if not self.is_running:
                self.set_status("⏹ Остановлено", error=True)
                break
            
            self.set_status(f"⚙ Озвучивание строки {i}/{len(lines)}")
            self.progress_bar["value"] = i
            self.root.update()
            
            try:
                # Создаём задачу
                success, result = api.create_task(line, template_uuid, settings['chunk_size'])
                
                if not success:
                    errors.append(f"Строка {i}: {result}")
                    continue
                
                task_id = result.get("task_id")
                
                # Ждём выполнения
                success, task_result = api.wait_for_task(task_id, max_attempts=120)
                
                if not self.is_running:
                    break
                
                if success:
                    # Получаем результат
                    success, content = api.get_task_result(task_id)
                    
                    if success and content:
                        # Сохраняем с номером строки
                        output_file = os.path.join(output_folder, f"{i}.mp3")
                        
                        with open(output_file, 'wb') as f:
                            f.write(content)
                        
                        # Добавляем паузу если нужно
                        if settings['end_pause'] > 0:
                            AudioProcessor.add_end_pause(output_file, settings['end_pause'])
                        
                        # Изменяем скорость если нужно
                        if self.adjust_speed_var.get():
                            AudioProcessor.adjust_duration(output_file, self.target_duration_var.get())
                        
                        completed += 1
                    else:
                        errors.append(f"Строка {i}: не удалось получить аудио")
                else:
                    errors.append(f"Строка {i}: таймаут или ошибка")
            
            except Exception as e:
                errors.append(f"Строка {i}: {str(e)}")
                print(f"Ошибка озвучивания строки {i}: {e}")
        
        # Итоги
        if errors:
            error_text = "\n".join(errors[:10])  # Показываем первые 10 ошибок
            if len(errors) > 10:
                error_text += f"\n... и ещё {len(errors) - 10} ошибок"
            messagebox.showwarning("Предупреждение", 
                                f"Озвучено: {completed}/{len(lines)}\n\nОшибки:\n{error_text}")
        
        self.set_status(f"✓ Готово! Озвучено: {completed}/{len(lines)}", success=True)
        
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    
    def stop_synthesis(self):
        """Остановить озвучивание"""
        self.is_running = False
        self.set_status("⏹ Остановка...", error=True)
    
    def save_settings(self):
        """Сохранить настройки"""
        settings = {
            "api_key": self.api_panel.get_api_key(),
            "output_folder": self.settings_panel.output_folder_var.get(),
            "video_input_folder": self.video_panel.video_input_folder_var.get(),
            "video_output_folder": self.video_panel.video_output_folder_var.get(),
            "chunk_size": self.settings_panel.chunk_size_var.get(),
            "disable_chunks": self.settings_panel.disable_chunks_var.get(),
            "mode": self.settings_panel.mode_var.get(),
            "end_pause": self.settings_panel.end_pause_var.get(),
            "adjust_speed": self.adjust_speed_var.get(),
            "target_duration": self.target_duration_var.get(),
            "keep_original_audio": self.video_panel.keep_original_audio_var.get(),
            "original_volume": self.video_panel.original_volume_var.get(),
            "video_fit_mode": self.video_panel.video_fit_mode_var.get(),
            "preview_text": self.preview_text
        }
        
        success, msg = self.settings_manager.save_settings(settings)
        if success:
            messagebox.showinfo("Сохранено", "Настройки сохранены")
        else:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {msg}")
    
    def load_settings(self):
        """Загрузить настройки"""
        settings = self.settings_manager.load_settings()
        
        # API ключ сохраняется в настройках, но панель удалена
        
        # Папка проектов
        projects_folder = settings.get("projects_folder", Config.DEFAULT_PROJECTS_FOLDER)
        if projects_folder and os.path.exists(projects_folder):
            self.project_panel.project_manager.base_folder = projects_folder
        
        self.settings_panel.output_folder_var.set(settings.get("output_folder", Config.DEFAULT_OUTPUT_AUDIO))
        self.video_panel.video_input_folder_var.set(settings.get("video_input_folder", ""))
        self.video_panel.video_output_folder_var.set(settings.get("video_output_folder", Config.DEFAULT_OUTPUT_VIDEO))
        self.settings_panel.chunk_size_var.set(settings.get("chunk_size", Config.DEFAULT_CHUNK_SIZE))
        self.settings_panel.disable_chunks_var.set(settings.get("disable_chunks", True))
        self.settings_panel.mode_var.set(settings.get("mode", "full"))
        self.settings_panel.end_pause_var.set(settings.get("end_pause", 0.0))
        self.adjust_speed_var.set(settings.get("adjust_speed", False))
        self.target_duration_var.set(settings.get("target_duration", 8.0))
        self.video_panel.keep_original_audio_var.set(settings.get("keep_original_audio", False))
        self.video_panel.original_volume_var.set(settings.get("original_volume", 30))
        self.video_panel.video_fit_mode_var.set(settings.get("video_fit_mode", "fit"))
        self.preview_text = settings.get("preview_text", Config.DEFAULT_PREVIEW_TEXT)
        
        # Настройки монтажа
        self.montage_panel.use_transitions_var.set(settings.get("use_transitions", False))
        self.montage_panel.transition_duration_var.set(settings.get("transition_duration", 0.5))
        if hasattr(self.montage_panel, 'transition_type_var'):
            self.montage_panel.transition_type_var.set(settings.get("transition_type", "crossfade"))
        
        self.settings_panel.toggle_chunk_size()
        self.toggle_speed_adjustment()
        self.video_panel.toggle_audio_mixing()
        self.montage_panel.toggle_transitions()
