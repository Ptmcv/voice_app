# ui/widgets/voice_preview.py
"""Виджет превью голосов с кнопками Play"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import requests
import time
from core.config import Config
from utils.helpers import open_file_in_system

class VoicePreviewCombobox(ttk.Frame):
    """Combobox с кнопками Play для прослушивания голосов"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent)
        self.app = app
        self.templates = []
        self.current_index = 0
        
        # Combobox
        self.combo = ttk.Combobox(self, state="readonly", width=40, font=('Segoe UI', 10))
        self.combo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.combo.bind("<<ComboboxSelected>>", self.on_select)
        
        # Кнопка Play/Generate
        self.play_btn = ttk.Button(self, text="▶", width=3, command=self.play_preview, state="disabled")
        self.play_btn.pack(side="left", padx=2)
        
        # Кнопка Regenerate
        self.regen_btn = ttk.Button(self, text="🔄", width=3, command=self.regenerate_preview, state="disabled")
        self.regen_btn.pack(side="left", padx=2)
    
    def set_templates(self, templates):
        """Установить список шаблонов"""
        self.templates = templates
        template_names = [f"{t.get('name', 'Без названия')}" for t in templates]
        self.combo['values'] = template_names
        if template_names:
            self.combo.current(0)
            self.current_index = 0
            self.update_buttons()
    
    def on_select(self, event=None):
        """Обработка выбора шаблона"""
        self.current_index = self.combo.current()
        self.update_buttons()
    
    def get_current_template(self):
        """Получить текущий выбранный шаблон"""
        if 0 <= self.current_index < len(self.templates):
            return self.templates[self.current_index]
        return None
    
    def update_buttons(self):
        """Обновить состояние кнопок"""
        template = self.get_current_template()
        if not template:
            self.play_btn.config(state="disabled")
            self.regen_btn.config(state="disabled")
            return
        
        # Проверяем наличие примера
        preview_path = self.get_preview_path(template)
        if os.path.exists(preview_path):
            self.play_btn.config(text="▶", state="normal")
            self.regen_btn.config(state="normal")
        else:
            self.play_btn.config(text="+", state="normal")
            self.regen_btn.config(state="disabled")
    
    def get_preview_path(self, template):
        """Получить путь к файлу примера"""
        template_id = template.get('uuid', 'unknown')
        preview_folder = os.path.join(os.getcwd(), "voice_previews")
        os.makedirs(preview_folder, exist_ok=True)
        return os.path.join(preview_folder, f"{template_id}.mp3")
    
    def play_preview(self):
        """Воспроизвести или создать пример"""
        template = self.get_current_template()
        if not template:
            return
        
        preview_path = self.get_preview_path(template)
        if os.path.exists(preview_path):
            open_file_in_system(preview_path)
        else:
            self.generate_preview()
    
    def generate_preview(self):
        """Создать пример голоса"""
        template = self.get_current_template()
        if not template:
            return
        
        # Получаем тестовый текст
        test_text = getattr(self.app, 'preview_text', Config.DEFAULT_PREVIEW_TEXT)
        if not test_text:
            messagebox.showwarning("Предупреждение", "Введите тестовый текст для примера голоса")
            return
        
        api_key = self.app.get_api_key()
        if not api_key:
            messagebox.showwarning("Предупреждение", "Введите API Key")
            return
        
        # Генерируем озвучку через API
        self.app.set_status("⚙ Генерация примера голоса...")
        
        try:
            from core.api_client import VoiceAPIClient
            
            api = VoiceAPIClient(api_key)
            template_uuid = template.get('uuid')
            
            # Создаём задачу на синтез
            success, result = api.create_task(test_text, template_uuid)
            
            if not success:
                messagebox.showerror("Ошибка", f"Ошибка API: {result}")
                self.app.set_status("✗ Ошибка", error=True)
                return
            
            task_id = result.get("task_id")
            
            # Ожидаем завершения задачи
            self.app.set_status("⚙ Ожидание результата...")
            
            def status_callback(status, status_data, attempt):
                self.app.set_status(f"⚙ {status_data.get('status_label', status)} ({attempt}с)")
            
            success, result = api.wait_for_task(task_id, callback=status_callback)
            
            if success:
                # Получаем результат
                success, content = api.get_task_result(task_id)
                
                if success:
                    preview_path = self.get_preview_path(template)
                    with open(preview_path, 'wb') as f:
                        f.write(content)
                    
                    self.app.set_status("✓ Пример создан!", success=True)
                    self.update_buttons()
                    open_file_in_system(preview_path)
                else:
                    messagebox.showerror("Ошибка", "Не удалось получить результат")
                    self.app.set_status("✗ Ошибка", error=True)
            else:
                messagebox.showerror("Ошибка", f"Ошибка: {result}")
                self.app.set_status("✗ Ошибка", error=True)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать пример: {e}")
            self.app.set_status("✗ Ошибка", error=True)
    
    def regenerate_preview(self):
        """Пересоздать пример голоса"""
        template = self.get_current_template()
        if not template:
            return
        
        # Удаляем старый пример
        preview_path = self.get_preview_path(template)
        if os.path.exists(preview_path):
            os.remove(preview_path)
        
        # Создаём новый
        self.generate_preview()
