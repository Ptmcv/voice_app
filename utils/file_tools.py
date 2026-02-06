# utils/file_tools.py
"""Инструменты для работы с файлами"""

import os
import re
import shutil
import time
from .helpers import natural_sort_key

class FileTools:
    """Инструменты для обработки файлов"""
    
    @staticmethod
    def sync_file_numbers(folder):
        """Синхронизация префикса: 13. 96_Comic... → 96. 96_Comic..."""
        files = FileTools._get_files(folder)
        if not files:
            return 0, "Нет файлов"
        
        out_folder = os.path.join(folder, "synced_files")
        os.makedirs(out_folder, exist_ok=True)
        
        done = 0
        for file in files:
            old_path = file['path']
            name_wo_ext = os.path.splitext(file['name'])[0]
            ext = file['ext']
            
            # Ищем число в имени файла
            match = re.search(r'(?:\.|_)(\d+)', name_wo_ext)
            if not match:
                match = re.search(r'(\d+)', name_wo_ext)
            
            number = match.group(1) if match else "0"
            new_name = f"{number}. {name_wo_ext}{ext}"
            new_path = os.path.join(out_folder, new_name)
            
            try:
                shutil.copy2(old_path, new_path)
                done += 1
            except:
                pass
        
        return done, out_folder
    
    @staticmethod
    def remove_number_duplicate(folder):
        """Удаление дубля: 2. 2_Closeup... → 2. Closeup..."""
        files = FileTools._get_files(folder)
        if not files:
            return 0, "Нет файлов"
        
        out_folder = os.path.join(folder, "cleaned_files")
        os.makedirs(out_folder, exist_ok=True)
        
        done = 0
        for file in files:
            old_path = file['path']
            name_wo_ext = os.path.splitext(file['name'])[0]
            ext = file['ext']
            
            # Ищем префикс вида "число. "
            prefix_match = re.match(r'^(\d+)\.\s*', name_wo_ext)
            if prefix_match:
                prefix_num = prefix_match.group(1)
                rest = name_wo_ext[len(prefix_match.group(0)):]
                # Удаляем дубль номера
                rest = re.sub(r'^' + prefix_num + r'[_\.\s]+', '', rest)
                new_name = f"{prefix_num}. {rest}{ext}"
            else:
                new_name = file['name']
            
            new_path = os.path.join(out_folder, new_name)
            
            try:
                shutil.copy2(old_path, new_path)
                done += 1
            except:
                pass
        
        return done, out_folder
    
    @staticmethod
    def remove_duplicate_numbers(folder):
        """3. 3. 3_Slow... → 3. Slow..."""
        files = FileTools._get_files(folder)
        if not files:
            return 0, "Нет файлов"
        
        renamed_count = 0
        for file in files:
            filename = file['name']
            name, ext = os.path.splitext(filename)
            
            match = re.match(r'^(\d+)\.\s+', name)
            if match:
                number = match.group(1)
                prefix = f"{number}. "
                rest_of_name = name[len(prefix):]
                clean_rest = re.sub(f'^{number}[\.\s_]+', '', rest_of_name)
                new_name = prefix + clean_rest + ext
                
                if new_name != filename:
                    old_path = file['path']
                    new_path = os.path.join(folder, new_name)
                    
                    try:
                        os.rename(old_path, new_path)
                        renamed_count += 1
                    except:
                        pass
        
        return renamed_count, folder
    
    @staticmethod
    def renumber_files(folder, extensions=['.mp4', '.mp3', '.wav', '.avi']):
        """Перенумеровать файлы: 1., 2., 3."""
        files = []
        for file in os.listdir(folder):
            filepath = os.path.join(folder, file)
            if os.path.isfile(filepath):
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    files.append({"path": filepath, "name": file, "ext": ext})
        
        if not files:
            return 0, "Нет файлов"
        
        # Сортируем
        files.sort(key=lambda f: natural_sort_key(f['name']))
        
        # Временные имена
        temp_files = []
        for i, file in enumerate(files, 1):
            old_path = file["path"]
            ext = file["ext"]
            temp_name = f"temp_{i}_{int(time.time()*1000000)}{ext}"
            temp_path = os.path.join(folder, temp_name)
            os.rename(old_path, temp_path)
            temp_files.append({"temp_path": temp_path, "new_number": i, "ext": ext})
        
        # Финальные имена
        for item in temp_files:
            final_name = f"{item['new_number']}.{item['ext']}"
            final_path = os.path.join(folder, final_name)
            os.rename(item['temp_path'], final_path)
        
        return len(files), folder
    
    @staticmethod
    def _get_files(folder):
        """Получить список файлов в папке"""
        files = []
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                files.append({
                    "path": file_path,
                    "name": file,
                    "ext": os.path.splitext(file)[1]
                })
        return files
