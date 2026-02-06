# core/settings_manager.py
"""Управление настройками приложения"""

import os
import json
from .config import Config

class SettingsManager:
    def __init__(self, config_file=None):
        self.config_file = config_file or Config.CONFIG_FILE
    
    def save_settings(self, settings):
        """Сохранить настройки"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True, "Настройки сохранены"
        except Exception as e:
            return False, str(e)
    
    def load_settings(self):
        """Загрузить настройки"""
        if not os.path.exists(self.config_file):
            return self.get_default_settings()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return self.get_default_settings()
    
    def get_default_settings(self):
        """Получить настройки по умолчанию"""
        return {
            "api_key": "",
            "output_folder": Config.DEFAULT_OUTPUT_AUDIO,
            "video_input_folder": "",
            "video_output_folder": Config.DEFAULT_OUTPUT_VIDEO,
            "chunk_size": Config.DEFAULT_CHUNK_SIZE,
            "disable_chunks": True,
            "mode": "full",
            "end_pause": 0.0,
            "adjust_speed": False,
            "target_duration": 8.0,
            "keep_original_audio": False,
            "original_volume": 30,
            "video_fit_mode": "fit",
            "preview_text": Config.DEFAULT_PREVIEW_TEXT
        }
