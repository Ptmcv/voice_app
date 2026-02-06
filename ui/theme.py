# ui/theme.py
"""Темная тема приложения"""

from tkinter import ttk
from core.config import Config

class DarkTheme:
    """Применение темной темы"""
    
    @staticmethod
    def apply_to_root(root):
        """Применить тему к главному окну"""
        colors = Config.COLORS
        
        root.configure(bg=colors['bg'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Базовые стили
        style.configure('.',
            background=colors['bg'],
            foreground=colors['fg'],
            fieldbackground=colors['input_bg'],
            bordercolor=colors['border'],
            darkcolor=colors['bg_darker'],
            lightcolor=colors['bg_light'],
            troughcolor=colors['bg_darker'],
            selectbackground=colors['accent'],
            selectforeground=colors['fg']
        )
        
        # LabelFrame
        style.configure('TLabelframe',
            background=colors['bg'],
            bordercolor=colors['border'],
            relief='flat'
        )
        
        style.configure('TLabelframe.Label',
            background=colors['bg'],
            foreground=colors['accent'],
            font=('Segoe UI', 11, 'bold')
        )
        
        # Label
        style.configure('TLabel',
            background=colors['bg'],
            foreground=colors['fg']
        )
        
        # Entry
        style.configure('TEntry',
            fieldbackground=colors['input_bg'],
            foreground=colors['fg'],
            bordercolor=colors['border'],
            lightcolor=colors['border'],
            darkcolor=colors['border'],
            insertcolor=colors['fg']
        )
        
        style.map('TEntry',
            fieldbackground=[('focus', colors['input_bg'])],
            lightcolor=[('focus', colors['accent'])],
            darkcolor=[('focus', colors['accent'])]
        )
        
        # Button
        style.configure('TButton',
            background=colors['button_bg'],
            foreground=colors['fg'],
            bordercolor=colors['border'],
            focuscolor=colors['accent'],
            lightcolor=colors['button_bg'],
            darkcolor=colors['button_bg'],
            padding=6
        )
        
        style.map('TButton',
            background=[('active', colors['button_hover']), ('pressed', colors['accent'])],
            foreground=[('active', colors['fg'])],
            lightcolor=[('active', colors['button_hover'])],
            darkcolor=[('active', colors['button_hover'])]
        )
        
        # Accent Button
        style.configure('Accent.TButton',
            background=colors['accent'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=8
        )
        
        style.map('Accent.TButton',
            background=[('active', colors['accent_hover']), ('pressed', colors['accent_hover'])],
            foreground=[('active', 'white')]
        )
        
        # Small Button
        style.configure('Small.TButton',
            font=('Segoe UI', 9),
            padding=4
        )
        
        # Checkbutton
        style.configure('TCheckbutton',
            background=colors['bg'],
            foreground=colors['fg']
        )
        
        style.map('TCheckbutton',
            background=[('active', colors['bg'])],
            foreground=[('active', colors['fg'])]
        )
        
        # Radiobutton
        style.configure('TRadiobutton',
            background=colors['bg'],
            foreground=colors['fg']
        )
        
        style.map('TRadiobutton',
            background=[('active', colors['bg'])],
            foreground=[('active', colors['fg'])]
        )
        
        # Combobox
        style.configure('TCombobox',
            fieldbackground=colors['input_bg'],
            background=colors['input_bg'],
            foreground=colors['fg'],
            arrowcolor=colors['fg'],
            bordercolor=colors['border']
        )
        
        style.map('TCombobox',
            fieldbackground=[('readonly', colors['input_bg'])],
            selectbackground=[('readonly', colors['input_bg'])],
            selectforeground=[('readonly', colors['fg'])]
        )
        
        # Spinbox
        style.configure('TSpinbox',
            fieldbackground=colors['input_bg'],
            background=colors['input_bg'],
            foreground=colors['fg'],
            arrowcolor=colors['fg'],
            bordercolor=colors['border']
        )
        
        # Progressbar
        style.configure('TProgressbar',
            background=colors['accent'],
            troughcolor=colors['bg_darker'],
            bordercolor=colors['border'],
            lightcolor=colors['accent'],
            darkcolor=colors['accent']
        )
        
        # Frame
        style.configure('TFrame',
            background=colors['bg']
        )
        
        return colors
