#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный файл для запуска системы работы с партнерами компании

Автор: Система демоэкзамена
Версия: 1.0
Дата: 2025
"""

import sys
import os
import traceback
from tkinter import messagebox, Tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    required_modules = ['pandas', 'openpyxl', 'PIL']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Отсутствуют необходимые модули: {', '.join(missing_modules)}\n\n"
        error_msg += "Установите их с помощью команды:\n"
        error_msg += "pip install -r requirements.txt"

        root = Tk()
        root.withdraw()
        messagebox.showerror("Ошибка зависимостей", error_msg)
        root.destroy()
        return False
    
    return True

def check_resources():
    resources_path = os.path.join("KOD_09_02_07-2-2025_Prilozhenia_k_obraztsu_zadania_Tom_1", "Ресурсы")
    
    if not os.path.exists(resources_path):
        error_msg = f"Папка с ресурсами не найдена: {resources_path}\n\n"
        error_msg += "Убедитесь, что файлы ресурсов находятся в правильной директории."
        
        root = Tk()
        root.withdraw()
        messagebox.showerror("Ошибка ресурсов", error_msg)
        root.destroy()
        return False

    required_files = [
        "Partners_import.xlsx",
        "Material_type_import.xlsx", 
        "Product_type_import.xlsx",
        "Products_import.xlsx",
        "Partner_products_import.xlsx"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(resources_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        warning_msg = f"Отсутствуют некоторые файлы ресурсов:\n{', '.join(missing_files)}\n\n"
        warning_msg += "Приложение будет работать с ограниченным функционалом."
        
        root = Tk()
        root.withdraw()
        messagebox.showwarning("Предупреждение о ресурсах", warning_msg)
        root.destroy()
    
    return True

def main():
    try:
        print("Запуск системы работы с партнерами компании...")
        
        if not check_dependencies():
            print("Ошибка: отсутствуют необходимые зависимости")
            return 1
        
        if not check_resources():
            print("Ошибка: отсутствуют необходимые ресурсы")
            return 1
        
        from partners_gui import PartnersGUI
        
        print("Инициализация приложения...")
        
        app = PartnersGUI()
        print("Приложение запущено успешно")
        
        # Запуск главного цикла
        app.run()
        
        print("Приложение завершено")
        return 0
        
    except ImportError as e:
        error_msg = f"Ошибка импорта модуля: {e}\n\n"
        error_msg += "Убедитесь, что все файлы проекта находятся в одной директории."
        
        root = Tk()
        root.withdraw()
        messagebox.showerror("Ошибка импорта", error_msg)
        root.destroy()
        
        print(f"Ошибка импорта: {e}")
        return 1
        
    except Exception as e:
        error_msg = f"Критическая ошибка при запуске приложения:\n{str(e)}\n\n"
        error_msg += "Детали ошибки:\n{traceback.format_exc()}"
        
        root = Tk()
        root.withdraw()
        messagebox.showerror("Критическая ошибка", error_msg)
        root.destroy()
        
        print(f"Критическая ошибка: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
