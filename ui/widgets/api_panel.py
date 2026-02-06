# ui/widgets/api_panel.py
"""Панель настроек API"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.config import Config

class APIPanel(ttk.LabelFrame):
    """Панель настроек API"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, text="⚙️ Настройки API", padding=10, **kwargs)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # API Key
        ttk.Label(self, text="API Key:").grid(row=0, column=0, sticky="w", padx=5)
        
        self.api_key_entry = ttk.Entry(self, width=30, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        self.api_key_entry.bind('<KeyRelease>', self.on_api_key_change)
        
        # Кнопки
        ttk.Button(self, text="Проверить баланс", 
                  command=self.check_balance).grid(row=0, column=2, padx=5)
        
        ttk.Button(self, text="Загрузить шаблоны", 
                  command=self.load_templates).grid(row=0, column=3, padx=5)
        
        ttk.Button(self, text="Текст для примеров", 
                  command=self.open_preview_text_dialog).grid(row=0, column=4, padx=5)
        
        # Баланс
        self.balance_label = ttk.Label(self, text="Баланс: --", 
                                       foreground=Config.COLORS['accent'])
        self.balance_label.grid(row=1, column=0, columnspan=5, pady=5)
    
    def on_api_key_change(self, event=None):
        """Автозагрузка при вводе API ключа"""
        api_key = self.api_key_entry.get().strip()
        if api_key and len(api_key) > 10:
            self.app.root.after(100, self.auto_load_data)
    
    def auto_load_data(self):
        """Фоновая загрузка данных"""
        try:
            self.check_balance(show_message=False)
            self.load_templates(show_message=False)
        except:
            pass
    
    def get_api_key(self):
        """Получить API ключ"""
        return self.api_key_entry.get().strip()
    
    def set_api_key(self, api_key):
        """Установить API ключ"""
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, api_key)
    
    def check_balance(self, show_message=True):
        """Проверить баланс"""
        api_key = self.get_api_key()
        if not api_key:
            if show_message:
                messagebox.showwarning("Предупреждение", "Введите API Key")
            return
        
        try:
            from core.api_client import VoiceAPIClient
            
            api = VoiceAPIClient(api_key)
            success, result = api.check_balance()
            
            if success:
                balance = result.get("balance", 0)
                balance_text = result.get("balance_text", str(balance))
                self.balance_label.config(text=f"Баланс: {balance_text} символов")
                
                if show_message:
                    messagebox.showinfo("Баланс", f"Баланс: {balance_text}")
            else:
                self.balance_label.config(text="Баланс: Ошибка")
                if show_message:
                    messagebox.showerror("Ошибка", f"Ошибка API: {result}")
        
        except Exception as e:
            if show_message:
                messagebox.showerror("Ошибка", f"Не удалось получить баланс: {e}")
    
    def load_templates(self, show_message=True):
        """Загрузить шаблоны"""
        api_key = self.get_api_key()
        if not api_key:
            if show_message:
                messagebox.showwarning("Предупреждение", "Введите API Key")
            return
        
        try:
            from core.api_client import VoiceAPIClient
            
            api = VoiceAPIClient(api_key)
            success, templates = api.get_templates()
            
            if success:
                self.app.set_templates(templates)
                if show_message:
                    messagebox.showinfo("Успех", f"Загружено шаблонов: {len(templates)}")
            else:
                if show_message:
                    messagebox.showerror("Ошибка", "Не удалось загрузить шаблоны")
        
        except Exception as e:
            if show_message:
                messagebox.showerror("Ошибка", f"Не удалось загрузить шаблоны: {e}")
    
    def open_preview_text_dialog(self):
        """Диалог для ввода тестового текста"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Тестовый текст для примеров голосов")
        dialog.geometry("500x200")
        dialog.configure(bg=Config.COLORS['bg'])
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Центрируем
        dialog.update_idletasks()
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Введите текст для озвучивания примеров:", 
                 font=('Segoe UI', 10)).pack(padx=20, pady=10)
        
        text_entry = tk.Text(
            dialog,
            height=5,
            width=50,
            bg=Config.COLORS['input_bg'],
            fg=Config.COLORS['fg'],
            insertbackground=Config.COLORS['fg'],
            font=('Segoe UI', 10)
        )
        text_entry.pack(padx=20, pady=10, fill="both", expand=True)
        text_entry.insert("1.0", getattr(self.app, 'preview_text', Config.DEFAULT_PREVIEW_TEXT))
        
        def save_text():
            self.app.preview_text = text_entry.get("1.0", "end-1c").strip()
            if not self.app.preview_text:
                self.app.preview_text = Config.DEFAULT_PREVIEW_TEXT
            messagebox.showinfo("Сохранено", f"Текст сохранён:\n{self.app.preview_text[:50]}...")
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_text, 
                  style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="left", padx=5)
