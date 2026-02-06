# core/updater.py
"""Система проверки обновлений"""

import requests
import json
from core.config import Config

class Updater:
    """Проверка обновлений"""
    
    # URL с информацией о версиях (замените на свой GitHub)
    VERSION_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/voice-app-updates/main/version.json"
    
    @staticmethod
    def check_for_updates():
        """Проверить наличие обновлений"""
        try:
            response = requests.get(Updater.VERSION_URL, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('latest_version', Config.VERSION)
                download_url = data.get('download_url', '')
                
                # Сравниваем версии
                current = Updater._parse_version(Config.VERSION)
                latest = Updater._parse_version(latest_version)
                
                if latest > current:
                    return True, latest_version, download_url
                
                return False, None, None
            
            return False, None, None
        
        except:
            return False, None, None
    
    @staticmethod
    def _parse_version(version_str):
        """Парсить версию для сравнения"""
        try:
            parts = version_str.replace('v', '').split('.')
            return tuple(int(p) for p in parts)
        except:
            return (0, 0, 0)
