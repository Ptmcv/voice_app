# ui/activation_window.py
"""Окно активации лицензии"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from core.config import Config
from core.license_manager import LicenseManager

class ActivationWindow:
    """Окно активации"""
    
    TELEGRAM_LINK = "https://t.me/your_username"  # ИЗМЕНИТЕ НА СВОЙ!
    
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.license_manager = LicenseManager()
        
        # Настраиваем окно
        self.root.title("Активация Voice App")
        self.root.geometry("500x400")
        self.root.configure(bg=Config.COLORS['bg'])
        self.root.resizable(False, False)
        
        # Центрируем
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        # Блокируем закрытие
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=40)
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_label = tk.Label(main_frame, 
                              text="🔐 Активация Voice App",
                              font=('Segoe UI', 18, 'bold'),
                              bg=Config.COLORS['bg'],
                              fg=Config.COLORS['accent'])
        title_label.pack(pady=20)
        
        # Описание
        desc_label = tk.Label(main_frame,
                             text="Для использования программы необходима лицензия.\nВведите лицензионный ключ ниже:",
                             font=('Segoe UI', 10),
                             bg=Config.COLORS['bg'],
                             fg=Config.COLORS['fg'],
                             justify="center")
        desc_label.pack(pady=10)
        
        # Поле ввода ключа
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(pady=20, fill="x")
        
        ttk.Label(key_frame, text="Лицензионный ключ:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=5)
        
        self.key_entry = ttk.Entry(key_frame, font=('Segoe UI', 10), width=45)
        self.key_entry.pack(fill="x", pady=5)
        self.key_entry.focus()
        
        # Кнопка активации
        activate_btn = ttk.Button(key_frame, text="✓ Активировать",
                                  command=self.activate,
                                  style='Accent.TButton')
        activate_btn.pack(pady=15, fill="x")
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').pack(fill="x", pady=20)
        
        # Ссылка на Telegram
        telegram_frame = ttk.Frame(main_frame)
        telegram_frame.pack(pady=10)
        
        tk.Label(telegram_frame,
                text="Для получения лицензии свяжитесь со мной:",
                font=('Segoe UI', 9),
                bg=Config.COLORS['bg'],
                fg=Config.COLORS['fg_dim']).pack()
        
        telegram_link = tk.Label(telegram_frame,
                                text="📱 Мой Telegram",
                                font=('Segoe UI', 11, 'bold', 'underline'),
                                bg=Config.COLORS['bg'],
                                fg=Config.COLORS['accent'],
                                cursor="hand2")
        telegram_link.pack(pady=5)
        telegram_link.bind("<Button-1>", lambda e: self.open_telegram())
        
        # Версия
        version_label = tk.Label(main_frame,
                                text=f"Версия {Config.VERSION}",
                                font=('Segoe UI', 8),
                                bg=Config.COLORS['bg'],
                                fg=Config.COLORS['fg_dim'])
        version_label.pack(side="bottom", pady=10)
        
        # Enter для активации
        self.key_entry.bind('<Return>', lambda e: self.activate())
    
    def activate(self):
        """Активировать лицензию"""
        license_key = self.key_entry.get().strip()
        
        if not license_key:
            messagebox.showwarning("Предупреждение", "Введите лицензионный ключ")
            return
        
        success, result = self.license_manager.activate_license(license_key)
        
        if success:
            expire_date = result['expire_date']
            days = result['days']
            
            messagebox.showinfo("Успех!", 
                              f"✅ Лицензия успешно активирована!\n\n"
                              f"Срок действия: {days} дней\n"
                              f"Действительна до: {expire_date[:10]}")
            
            self.root.destroy()
            self.on_success()
        else:
            messagebox.showerror("Ошибка активации", result)
    
    def open_telegram(self):
        """Открыть Telegram"""
        webbrowser.open(self.TELEGRAM_LINK)
    
    def on_close(self):
        """Закрытие окна"""
        if messagebox.askokcancel("Выход", "Без лицензии программа не запустится. Выйти?"):
            self.root.quit()
