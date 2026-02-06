# ui/widgets/__init__.py
"""Виджеты интерфейса"""

from .voice_preview import VoicePreviewCombobox
from .api_panel import APIPanel
from .text_panel import TextPanel
from .settings_panel import SettingsPanel
from .video_panel import VideoPanel
from .tools_panel import ToolsPanel
from .montage_panel import MontagePanel
from .project_panel import ProjectPanel  # НОВОЕ!

__all__ = [
    'VoicePreviewCombobox',
    'APIPanel',
    'TextPanel',
    'SettingsPanel',
    'VideoPanel',
    'ToolsPanel',
    'MontagePanel',
    'ProjectPanel'  # НОВОЕ!
]
