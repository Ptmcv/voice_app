# ui/widgets/project_panel.py
"""Панель управления проектами"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from core.config import Config
from utils.project_manager import ProjectManager
from utils.helpers import open_file_in_system

class ProjectPanel(ttk.LabelFrame):
    """Панель управления проектами"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="📁 Управление проектами", padding=10, **kwargs)
        self.app = app
        self.project_manager = ProjectManager()
        self.current_project = None
        self.create_widgets()
    
    def create_widgets(self):
        # Название проекта
        project_name_frame = ttk.Frame(self)
        project_name_frame.pack(fill="x", pady=5)
        
        ttk.Label(project_name_frame, text="Текущий проект:", 
                 font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        
        self.current_project_label = ttk.Label(project_name_frame, 
                                               text="Не выбран",
                                               foreground=Config.COLORS['fg_dim'])
        self.current_project_label.pack(side="left", padx=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="➕ Создать проект",
                  command=self.create_new_project,
                  style='Accent.TButton').pack(side="left", padx=5, fill="x", expand=True)
        
        ttk.Button(btn_frame, text="📂 Открыть проект",
                  command=self.open_existing_project).pack(side="left", padx=5, fill="x", expand=True)
        
        ttk.Button(btn_frame, text="📂 Папка проектов",
                  command=self.open_projects_folder).pack(side="left", padx=5)
        
        # Информация о текущем проекте
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", pady=5)
        
        self.project_info_label = ttk.Label(info_frame, text="", 
                                           foreground=Config.COLORS['fg_dim'],
                                           font=('Segoe UI', 8))
        self.project_info_label.pack(anchor="w", padx=5)
    
    def create_new_project(self):
        """Создать новый проект"""
        # Диалог ввода названия
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Создание нового проекта")
        dialog.geometry("500x180")
        dialog.configure(bg=Config.COLORS['bg'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Центрируем
        dialog.update_idletasks()
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Введите название проекта:", 
                 font=('Segoe UI', 11, 'bold')).pack(padx=20, pady=15)
        
        name_entry = ttk.Entry(dialog, width=40, font=('Segoe UI', 10))
        name_entry.pack(padx=20, pady=10)
        name_entry.focus()
        
        def create():
            project_name = name_entry.get().strip()
            if not project_name:
                messagebox.showwarning("Предупреждение", "Введите название проекта")
                return
            
            success, message = self.project_manager.create_project(project_name)
            
            if success:
                dialog.destroy()
                # Автоматически открываем созданный проект
                self.load_project(project_name)
                messagebox.showinfo("Успех", f"Проект '{project_name}' создан и открыт!")
                # Открываем папку проекта
                project_path = os.path.join(self.project_manager.base_folder, project_name)
                open_file_in_system(project_path)
            else:
                messagebox.showerror("Ошибка", message)
        
        def cancel():
            dialog.destroy()
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Создать", command=create, 
                  style='Accent.TButton').pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Отмена", command=cancel).pack(side="left", padx=10)
        
        # Enter для создания
        name_entry.bind('<Return>', lambda e: create())
    
    def open_existing_project(self):
        """Открыть существующий проект"""
        projects = self.project_manager.list_projects()
        
        if not projects:
            messagebox.showinfo("Информация", "Нет созданных проектов")
            return
        
        # Диалог выбора проекта
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Выбор проекта")
        dialog.geometry("600x400")
        dialog.configure(bg=Config.COLORS['bg'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Центрируем
        dialog.update_idletasks()
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Выберите проект:", 
                 font=('Segoe UI', 11, 'bold')).pack(padx=20, pady=15)
        
        # Список проектов
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(listbox_frame, 
                            yscrollcommand=scrollbar.set,
                            font=('Segoe UI', 10),
                            bg=Config.COLORS['input_bg'],
                            fg=Config.COLORS['fg'],
                            selectbackground=Config.COLORS['accent'],
                            selectforeground=Config.COLORS['fg'])
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Заполняем список
        for project in projects:
            created_str = project['created'].strftime('%Y-%m-%d %H:%M')
            listbox.insert(tk.END, f"{project['name']} (создан: {created_str})")
        
        def open_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите проект")
                return
            
            project_name = projects[selection[0]]['name']
            self.load_project(project_name)
            dialog.destroy()
            messagebox.showinfo("Успех", f"Проект '{project_name}' открыт!")
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Открыть", command=open_selected,
                  style='Accent.TButton').pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="left", padx=10)
        
        # Двойной клик для открытия
        listbox.bind('<Double-Button-1>', lambda e: open_selected())
    
    def load_project(self, project_name):
        """Загрузить проект и обновить все пути"""
        self.current_project = project_name
        project_path = os.path.join(self.project_manager.base_folder, project_name)
        
        # Обновляем метки
        self.current_project_label.config(text=project_name, 
                                         foreground=Config.COLORS['accent'])
        self.project_info_label.config(text=f"Путь: {project_path}")
        
        # Обновляем пути во всех панелях
        
        # 1. Папка для аудио (озвучка)
        audio_folder = os.path.join(project_path, "озвучка")
        self.app.settings_panel.output_folder_var.set(audio_folder)
        
        # 2. Папка с видео (исходные видео)
        video_input_folder = os.path.join(project_path, "видео")
        self.app.video_panel.video_input_folder_var.set(video_input_folder)
        
        # 3. Папка для обработанных видео (видео с озвучкой)
        video_output_folder = os.path.join(project_path, "видео_с_озвучкой")
        self.app.video_panel.video_output_folder_var.set(video_output_folder)
        
        # 4. Папка для монтажа (тоже видео с озвучкой)
        self.app.montage_panel.montage_input_var.set(video_output_folder)
        
        # 5. Итоговое видео
        final_video_path = os.path.join(project_path, f"{project_name}_final.mp4")
        self.app.montage_panel.montage_output_var.set(final_video_path)
        
        # 6. Загружаем текст для озвучки (если есть)
        text_file_path = os.path.join(audio_folder, f"text_{project_name}.txt")
        if os.path.exists(text_file_path):
            try:
                with open(text_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Пропускаем заголовок
                    lines = content.split('\n')
                    actual_text = '\n'.join(lines[3:]) if len(lines) > 3 else content
                    if actual_text.strip():
                        self.app.text_panel.set_text(actual_text)
            except:
                pass
        
        self.app.set_status(f"✓ Проект '{project_name}' открыт!", success=True)
    
    def open_projects_folder(self):
        """Открыть папку с проектами"""
        open_file_in_system(self.project_manager.base_folder)
    
    def get_current_project_name(self):
        """Получить имя текущего проекта"""
        return self.current_project
