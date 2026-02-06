# ui/widgets/tools_panel.py
"""Инструменты для файлов с бекапами"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import shutil
import time
from core.config import Config
from utils.helpers import natural_sort_key

class ToolsPanel(ttk.LabelFrame):
    """Инструменты для файлов"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="🛠️ Инструменты файлов", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
        
        # Автоопределение папки видео
        self.auto_detect_video_folder()
    
    def create_widgets(self):
        # Папка (автоматически определяется)
        folder_frame = ttk.Frame(self)
        folder_frame.pack(fill="x", pady=5)
        
        ttk.Label(folder_frame, text="Папка видео:", 
                 font=('Segoe UI', 9, 'bold')).pack(side="left", padx=5)
        
        self.tools_folder_var = tk.StringVar(value="")
        folder_entry = ttk.Entry(folder_frame, textvariable=self.tools_folder_var, 
                                width=25, state="readonly")
        folder_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(folder_frame, text="📁", 
                  command=self.select_folder,
                  width=3).pack(side="left", padx=5)
        
        # Разделитель
        ttk.Separator(self, orient='horizontal').pack(fill="x", pady=10)
        
        # Кнопка 1: Нормализация имён файлов
        ttk.Button(self, text="✨ Нормализовать имена файлов",
                  command=self.normalize_filenames).pack(fill="x", pady=5, padx=5)
        
        ttk.Label(self, 
                 text="175. 177_Name → 177. Name (исправляет несоответствия)",
                 foreground=Config.COLORS['fg_dim'], 
                 font=('Segoe UI', 8)).pack(anchor="w", padx=20, pady=2)
        
        # Кнопка 2: Перенумерация
        ttk.Button(self, text="🔢 Перенумерация 1., 2., 3., ...",
                  command=self.renumber_sequential).pack(fill="x", pady=5, padx=5)
        
        ttk.Label(self, text="Переименовывает все файлы по порядку",
                 foreground=Config.COLORS['fg_dim'], 
                 font=('Segoe UI', 8)).pack(anchor="w", padx=20, pady=2)
        
        # Разделитель
        ttk.Separator(self, orient='horizontal').pack(fill="x", pady=10)
        
        # Кнопка 3: Исправить пропуски видео (с нормализацией)
        ttk.Button(self, text="🔍 Исправить пропуски видео",
                  command=self.fix_missing_videos,
                  style='Accent.TButton').pack(fill="x", pady=5, padx=5)
        
        ttk.Label(self, 
                 text="Нормализует имена, находит пропуски, копирует в 'ошибки/'",
                 foreground=Config.COLORS['fg_dim'], 
                 font=('Segoe UI', 8)).pack(anchor="w", padx=20, pady=2)
        
        # Статус бекапа
        self.backup_status = ttk.Label(self, text="", 
                                       foreground=Config.COLORS['success'],
                                       font=('Segoe UI', 8))
        self.backup_status.pack(pady=5)
    
    def auto_detect_video_folder(self):
        """Автоопределение папки видео"""
        if hasattr(self.app, 'project_panel') and self.app.project_panel.current_project:
            project_name = self.app.project_panel.current_project
            project_base = self.app.project_panel.project_manager.base_folder
            video_folder = os.path.join(project_base, project_name, "видео")
            
            if os.path.exists(video_folder):
                self.tools_folder_var.set(video_folder)
    
    def select_folder(self):
        """Выбрать папку вручную"""
        folder = filedialog.askdirectory(title="Выберите папку видео")
        if folder:
            self.tools_folder_var.set(folder)
    
    def create_backup(self, folder):
        """Создать бекап перед изменениями"""
        backup_folder = os.path.join(folder, "_backup_" + time.strftime('%Y%m%d_%H%M%S'))
        
        try:
            os.makedirs(backup_folder, exist_ok=True)
            
            # Копируем все файлы
            copied = 0
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath) and not filename.startswith('_backup_'):
                    shutil.copy2(filepath, os.path.join(backup_folder, filename))
                    copied += 1
            
            self.backup_status.config(
                text=f"✓ Бекап создан: {copied} файлов → {os.path.basename(backup_folder)}",
                foreground=Config.COLORS['success'])
            
            return True, backup_folder
        
        except Exception as e:
            messagebox.showerror("Ошибка бекапа", f"Не удалось создать бекап:\n{e}")
            return False, None
    
    def normalize_filenames(self):
        """
        Нормализация имён файлов:
        175. 177_Name → 177. Name
        """
        folder = self.tools_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("Предупреждение", "Выберите папку видео")
            return
        
        # Создаём бекап
        success, backup_folder = self.create_backup(folder)
        if not success:
            return
        
        processed = 0
        
        for filename in os.listdir(folder):
            if filename.startswith('_backup_'):
                continue
            
            filepath = os.path.join(folder, filename)
            if not os.path.isfile(filepath):
                continue
            
            name, ext = os.path.splitext(filename)
            
            # Ищем паттерн: ЧИСЛО1. ЧИСЛО2_остальное
            # Примеры: "175. 177_Name", "24. 24_Name"
            match = re.match(r'^(\d+)\.\s*(\d+)[_\.\s]+(.+)$', name)
            
            if match:
                prefix_num = match.group(1)   # 175
                real_num = match.group(2)     # 177
                rest = match.group(3)         # Name
                
                # Если числа разные - берём второе (реальное)
                if prefix_num != real_num:
                    # Используем реальное число
                    new_name = f"{real_num}. {rest}{ext}"
                else:
                    # Числа одинаковые - просто убираем дубль
                    new_name = f"{real_num}. {rest}{ext}"
                
                new_path = os.path.join(folder, new_name)
                
                if new_name != filename:
                    try:
                        os.rename(filepath, new_path)
                        processed += 1
                        print(f"✓ {filename} → {new_name}")
                    except Exception as e:
                        print(f"✗ Ошибка {filename}: {e}")
        
        messagebox.showinfo("Готово", 
                          f"✅ Нормализовано файлов: {processed}\n\n"
                          f"📁 Бекап: {os.path.basename(backup_folder)}")
        
        self.app.set_status(f"✓ Нормализовано: {processed} файлов", success=True)
    
    def renumber_sequential(self):
        """Перенумерация файлов 1., 2., 3., ..."""
        folder = self.tools_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("Предупреждение", "Выберите папку видео")
            return
        
        # Создаём бекап
        success, backup_folder = self.create_backup(folder)
        if not success:
            return
        
        # Собираем файлы
        files = []
        for filename in os.listdir(folder):
            if filename.startswith('_backup_'):
                continue
            
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                files.append({"path": filepath, "name": filename})
        
        if not files:
            messagebox.showinfo("Информация", "Нет файлов в папке")
            return
        
        # Сортируем
        files.sort(key=lambda f: natural_sort_key(f['name']))
        
        # Временные имена
        temp_files = []
        for i, file_info in enumerate(files, 1):
            old_path = file_info['path']
            name, ext = os.path.splitext(file_info['name'])
            
            # Убираем старый номер если есть
            clean_name = re.sub(r'^\d+[\.\s]+', '', name)
            
            temp_name = f"temp_{i}_{int(time.time() * 1000000)}_{clean_name}{ext}"
            temp_path = os.path.join(folder, temp_name)
            
            os.rename(old_path, temp_path)
            temp_files.append({
                "temp_path": temp_path, 
                "new_number": i, 
                "clean_name": clean_name,
                "ext": ext
            })
        
        # Финальные имена
        processed = 0
        for item in temp_files:
            final_name = f"{item['new_number']}. {item['clean_name']}{item['ext']}"
            final_path = os.path.join(folder, final_name)
            
            try:
                os.rename(item['temp_path'], final_path)
                processed += 1
                print(f"✓ → {final_name}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
        
        messagebox.showinfo("Готово", 
                          f"✅ Перенумеровано: {processed} файлов\n\n"
                          f"📁 Бекап: {os.path.basename(backup_folder)}")
        
        self.app.set_status(f"✓ Перенумеровано: {processed} файлов", success=True)
    
    def fix_missing_videos(self):
        """Исправить пропуски видео (с нормализацией имён)"""
        # Проверяем проект
        if not hasattr(self.app, 'project_panel') or not self.app.project_panel.current_project:
            messagebox.showwarning("Предупреждение", "Сначала откройте проект!")
            return
        
        project_name = self.app.project_panel.current_project
        project_base = self.app.project_panel.project_manager.base_folder
        project_path = os.path.join(project_base, project_name)
        
        # Папки
        video_folder = os.path.join(project_path, "видео")
        images_folder = os.path.join(project_path, "картинки")
        
        if not os.path.exists(video_folder):
            messagebox.showwarning("Предупреждение", f"Папка видео не найдена!\n{video_folder}")
            return
        
        if not os.path.exists(images_folder):
            messagebox.showwarning("Предупреждение", f"Папка картинок не найдена!\n{images_folder}")
            return
        
        # ШАГ 1: Нормализация имён в папке видео
        print("\n=== ШАГ 1: Нормализация имён видео ===")
        
        # Создаём бекап видео
        success, backup_folder = self.create_backup(video_folder)
        if not success:
            return
        
        normalized = 0
        for filename in os.listdir(video_folder):
            if filename.startswith('_backup_') or filename.endswith('.txt'):
                continue
            
            filepath = os.path.join(video_folder, filename)
            if not os.path.isfile(filepath):
                continue
            
            name, ext = os.path.splitext(filename)
            
            # Нормализуем: 175. 177_Name → 177. Name
            match = re.match(r'^(\d+)\.\s*(\d+)[_\.\s]+(.+)$', name)
            
            if match:
                prefix_num = match.group(1)
                real_num = match.group(2)
                rest = match.group(3)
                
                new_name = f"{real_num}. {rest}{ext}"
                new_path = os.path.join(video_folder, new_name)
                
                if new_name != filename:
                    try:
                        os.rename(filepath, new_path)
                        normalized += 1
                        print(f"✓ {filename} → {new_name}")
                    except Exception as e:
                        print(f"✗ {filename}: {e}")
        
        print(f"\n✓ Нормализовано видео: {normalized}")
        
        # ШАГ 2: Нормализация имён в папке картинок
        print("\n=== ШАГ 2: Нормализация имён картинок ===")
        
        # Создаём бекап картинок
        success, backup_images = self.create_backup(images_folder)
        
        normalized_images = 0
        for filename in os.listdir(images_folder):
            if filename.startswith('_backup_'):
                continue
            
            filepath = os.path.join(images_folder, filename)
            if not os.path.isfile(filepath):
                continue
            
            name, ext = os.path.splitext(filename)
            
            match = re.match(r'^(\d+)\.\s*(\d+)[_\.\s]+(.+)$', name)
            
            if match:
                real_num = match.group(2)
                rest = match.group(3)
                new_name = f"{real_num}. {rest}{ext}"
                new_path = os.path.join(images_folder, new_name)
                
                if new_name != filename:
                    try:
                        os.rename(filepath, new_path)
                        normalized_images += 1
                        print(f"✓ {filename} → {new_name}")
                    except Exception as e:
                        print(f"✗ {filename}: {e}")
        
        print(f"\n✓ Нормализовано картинок: {normalized_images}")
        
        # ШАГ 3: Поиск пропусков
        print("\n=== ШАГ 3: Поиск пропусков ===")
        
        # Получаем номера видео
        video_numbers = set()
        for file in os.listdir(video_folder):
            if file.startswith('_backup_') or file.endswith('.txt'):
                continue
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                match = re.match(r'^(\d+)', file)
                if match:
                    video_numbers.add(int(match.group(1)))
        
        # Получаем номера картинок
        image_numbers = set()
        image_files = {}
        for file in os.listdir(images_folder):
            if file.startswith('_backup_'):
                continue
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                match = re.match(r'^(\d+)', file)
                if match:
                    num = int(match.group(1))
                    image_numbers.add(num)
                    image_files[num] = file
        
        # Находим пропуски
        missing_numbers = sorted(image_numbers - video_numbers)
        
        if not missing_numbers:
            messagebox.showinfo("Готово", 
                              f"✅ Нормализовано:\n"
                              f"   • Видео: {normalized}\n"
                              f"   • Картинки: {normalized_images}\n\n"
                              f"✅ Пропусков не найдено!\n\n"
                              f"📁 Бекапы созданы")
            return
        
        # ШАГ 4: Копирование в папку ошибок
        print(f"\n=== ШАГ 4: Копирование {len(missing_numbers)} пропусков ===")
        
        errors_folder = os.path.join(project_path, "ошибки")
        os.makedirs(errors_folder, exist_ok=True)
        
        prompts_file = os.path.join(errors_folder, "failed_video_prompts.txt")
        
        # Читаем промпты
        video_prompts_file = os.path.join(video_folder, "prompts_video.txt")
        prompts_dict = {}
        
        if os.path.exists(video_prompts_file):
            with open(video_prompts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        match = re.match(r'^(\d+)\.\s*(.+)', line)
                        if match:
                            num = int(match.group(1))
                            prompts_dict[num] = line
        
        # Копируем файлы
        copied = 0
        with open(prompts_file, 'w', encoding='utf-8') as f:
            f.write(f"# Пропущенные видео для проекта '{project_name}'\n")
            f.write(f"# Создано: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Всего пропусков: {len(missing_numbers)}\n\n")
            
            for num in missing_numbers:
                # Копируем картинку
                if num in image_files:
                    src_img = os.path.join(images_folder, image_files[num])
                    dst_img = os.path.join(errors_folder, image_files[num])
                    
                    try:
                        shutil.copy2(src_img, dst_img)
                        copied += 1
                        print(f"✓ Скопирована: {image_files[num]}")
                    except Exception as e:
                        print(f"✗ {image_files[num]}: {e}")
                
                # Записываем промпт
                if num in prompts_dict:
                    f.write(prompts_dict[num] + '\n')
                else:
                    f.write(f"{num}. [промпт не найден]\n")
        
        # Отчёт
        total_expected = len(image_numbers)
        success_rate = ((total_expected - len(missing_numbers)) / total_expected * 100) if total_expected > 0 else 0
        
        report = (
            f"✅ АНАЛИЗ ЗАВЕРШЁН\n\n"
            f"🔧 Нормализация:\n"
            f"   • Видео: {normalized} файлов\n"
            f"   • Картинки: {normalized_images} файлов\n\n"
            f"📊 Статистика:\n"
            f"   • Всего картинок: {len(image_numbers)}\n"
            f"   • Всего видео: {len(video_numbers)}\n"
            f"   • Пропущено видео: {len(missing_numbers)}\n"
            f"   • Успешность: {success_rate:.1f}%\n\n"
            f"📁 Результаты:\n"
            f"   • Скопировано: {copied} файлов\n"
            f"   • Папка: {errors_folder}\n"
            f"   • Промпты: failed_video_prompts.txt\n\n"
            f"🔢 Пропущенные: {', '.join(map(str, missing_numbers[:20]))}"
            f"{'...' if len(missing_numbers) > 20 else ''}\n\n"
            f"💾 Бекапы созданы"
        )
        
        messagebox.showinfo("Анализ пропусков видео", report)
        self.app.set_status(f"✓ Пропусков: {len(missing_numbers)}, нормализовано: {normalized + normalized_images}", success=True)
