# core/config.py
"""Конфигурация приложения"""

import os

class Config:
    # Версия и название
    VERSION = "2.0.0"
    APP_NAME = "Озвучиватель текста - Voice API"
    
    # API
    API_BASE_URL = "https://voiceapi.csv666.ru"
    
    # Файлы
    CONFIG_FILE = "app_config.json"
    
    # Папки по умолчанию
    DEFAULT_OUTPUT_AUDIO = os.path.join(os.getcwd(), "output_audio")
    DEFAULT_OUTPUT_VIDEO = os.path.join(os.getcwd(), "output_video")
    DEFAULT_PROJECTS_FOLDER = os.path.join(os.getcwd(), "projects")
    
    # Цветовая схема (темная тема)
    COLORS = {
        'bg': '#202222',
        'bg_light': '#2a2d2e',
        'bg_darker': '#1a1c1d',
        'fg': '#e8e9ea',
        'fg_dim': '#9ca3af',
        'accent': '#20808d',
        'accent_hover': '#1a5f6a',
        'border': '#3a3d3f',
        'input_bg': '#2f3437',
        'button_bg': '#2a4f58',
        'button_hover': '#1e3d44',
        'error': '#ef4444',
        'success': '#10b981'
    }
    
    # Настройки по умолчанию
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_PREVIEW_TEXT = "Привет! Это пример моего голоса."
    AUTO_LOAD_DELAY = 500
