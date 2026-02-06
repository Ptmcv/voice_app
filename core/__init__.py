# core/__init__.py
"""Ядро приложения Voice App"""

from .config import Config
from .api_client import VoiceAPIClient
from .settings_manager import SettingsManager

__all__ = ['Config', 'VoiceAPIClient', 'SettingsManager']
