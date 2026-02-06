# main.py
"""Точка входа в приложение Voice App"""

import tkinter as tk
from core.license_manager import LicenseManager
from ui.activation_window import ActivationWindow

def check_and_run():
    """Проверить лицензию и запустить"""
    license_manager = LicenseManager()
    success, result = license_manager.check_license()
    
    if success:
        # Лицензия валидна - запускаем приложение
        run_app()
    else:
        # Требуется активация
        root = tk.Tk()
        ActivationWindow(root, on_success=lambda: run_app_after_activation(root))
        root.mainloop()

def run_app():
    """Запустить основное приложение"""
    from ui.main_window import MainWindow
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

def run_app_after_activation(activation_root):
    """Запустить после активации"""
    activation_root.destroy()
    run_app()

if __name__ == "__main__":
    check_and_run()
