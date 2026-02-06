# utils/project_manager.py
"""Менеджер проектов"""

import os
import platform
import subprocess
from datetime import datetime
from core.config import Config

class ProjectManager:
    """Управление проектами"""
    
    def __init__(self, base_folder=None):
        self.base_folder = base_folder or Config.DEFAULT_PROJECTS_FOLDER
        os.makedirs(self.base_folder, exist_ok=True)
    
    def create_project(self, project_name):
        """Создать новый проект"""
        if not project_name or project_name.strip() == "":
            return False, "Введите название проекта"
        
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).strip()
        
        if not safe_name:
            return False, "Недопустимое имя проекта"
        
        project_path = os.path.join(self.base_folder, safe_name)
        
        if os.path.exists(project_path):
            return False, f"Проект '{safe_name}' уже существует"
        
        try:
            os.makedirs(project_path)
            
            # Создаем структуру папок
            folders = {
                "картинки": "prompts_images.txt",
                "видео": "prompts_video.txt",
                "озвучка": "text_script.txt",
                "видео_с_озвучкой": None
            }
            
            for folder_name, txt_file in folders.items():
                folder_path = os.path.join(project_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                if txt_file:
                    file_path = os.path.join(folder_path, txt_file)
                    # СОЗДАЁМ ПУСТОЙ ФАЙЛ (без заголовков)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        pass  # Пустой файл
            
            # README с информацией о проекте
            readme_path = os.path.join(project_path, "README.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"Проект: {project_name}\n")
                f.write(f"Создан: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write("Структура проекта:\n")
                f.write("├── картинки/          - Изображения и prompts_images.txt\n")
                f.write("├── видео/             - Видео и prompts_video.txt\n")
                f.write("├── озвучка/           - Аудио файлы и text_script.txt\n")
                f.write("└── видео_с_озвучкой/  - Финальные видео\n")
            
            return True, f"Проект '{safe_name}' создан!\n{project_path}"
        
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def list_projects(self):
        """Список проектов"""
        if not os.path.exists(self.base_folder):
            return []
        
        projects = []
        for item in os.listdir(self.base_folder):
            item_path = os.path.join(self.base_folder, item)
            if os.path.isdir(item_path):
                projects.append({
                    "name": item,
                    "path": item_path,
                    "created": datetime.fromtimestamp(os.path.getctime(item_path))
                })
        
        return sorted(projects, key=lambda x: x['created'], reverse=True)
    
    def open_folder(self, path):
        """Открыть папку"""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
            return True
        except:
            return False
