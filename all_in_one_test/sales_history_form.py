import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Dict, Any, List
from database_manager import DatabaseManager
from datetime import datetime
import csv
import os

class SalesHistoryForm:
    
    def __init__(self, parent, db_manager: DatabaseManager, partner_data: Dict[str, Any]):
        self.parent = parent
        self.db_manager = db_manager
        self.partner_data = partner_data
        self.sales_data = []

        self.window = tk.Toplevel(parent)
        self.window.title(f"История продаж - {partner_data['partner_name']}")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()

        self.center_window()

        self.setup_styles()

        self.create_widgets()

        self.load_sales_data()

        self.window.wait_window()
    
    def setup_styles(self):
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'white': '#ffffff'
        }
        
        self.fonts = {
            'title': tkfont.Font(family="Segoe UI", size=14, weight="bold"),
            'header': tkfont.Font(family="Segoe UI", size=11, weight="bold"),
            'normal': tkfont.Font(family="Segoe UI", size=10),
            'small': tkfont.Font(family="Segoe UI", size=9)
        }
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_header(main_frame)

        self.create_statistics_panel(main_frame)

        self.create_sales_table(main_frame)

        self.create_toolbar(main_frame)
    
    def create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        partner_name_label = ttk.Label(header_frame, 
                                      text=f"Партнер: {self.partner_data['partner_name']}",
                                      font=self.fonts['title'],
                                      foreground=self.colors['primary'])
        partner_name_label.pack(side=tk.LEFT)

        close_btn = ttk.Button(header_frame, 
                              text="Закрыть",
                              style="Danger.TButton",
                              command=self.window.destroy)
        close_btn.pack(side=tk.RIGHT)
    
    def create_statistics_panel(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Статистика продаж", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        left_col = ttk.Frame(stats_grid)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_col, text="Общие продажи:", font=self.fonts['header']).grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.total_sales_label = ttk.Label(left_col, text="0", font=self.fonts['header'], foreground=self.colors['success'])
        self.total_sales_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(left_col, text="Количество транзакций:").grid(row=1, column=0, sticky='w', padx=(0, 5))
        self.transactions_count_label = ttk.Label(left_col, text="0")
        self.transactions_count_label.grid(row=1, column=1, sticky='w')

        right_col = ttk.Frame(stats_grid)
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(right_col, text="Текущая скидка:", font=self.fonts['header']).grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.current_discount_label = ttk.Label(right_col, text="0%", font=self.fonts['header'], foreground=self.colors['accent'])
        self.current_discount_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(right_col, text="Дата регистрации:").grid(row=1, column=0, sticky='w', padx=(0, 5))
        self.registration_date_label = ttk.Label(right_col, text="")
        self.registration_date_label.grid(row=1, column=1, sticky='w')

        left_col.grid_columnconfigure(1, weight=1)
        right_col.grid_columnconfigure(1, weight=1)
    
    def create_sales_table(self, parent):
        table_frame = ttk.LabelFrame(parent, text="История продаж", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        columns = ('ID', 'Продукт', 'Количество', 'Дата продажи')
        
        self.sales_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.sales_tree.heading(col, text=col, command=lambda c=col: self.sort_table(c))
            self.sales_tree.column(col, width=150, minwidth=100)

        self.sales_tree.column('ID', width=80, minwidth=60)
        self.sales_tree.column('Продукт', width=250, minwidth=200)
        self.sales_tree.column('Количество', width=120, minwidth=100)
        self.sales_tree.column('Дата продажи', width=150, minwidth=120)

        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
        self.sales_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.sales_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.sales_tree.bind('<Double-1>', self.on_sale_double_click)
    
    def create_toolbar(self, parent):
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X)

        export_btn = ttk.Button(toolbar_frame, 
                               text="Экспорт в CSV",
                               style="Success.TButton",
                               command=self.export_to_csv)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = ttk.Button(toolbar_frame, 
                                text="Обновить",
                                style="Accent.TButton",
                                command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
    
    def load_sales_data(self):
        try:
            self.sales_data = self.db_manager.get_partner_sales_history(self.partner_data['partner_id'])
            self.update_sales_table()
            self.update_statistics()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных о продажах: {e}")
    
    def update_sales_table(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        search_text = self.search_var.get().lower()
        filtered_data = self.sales_data
        
        if search_text:
            filtered_data = [
                sale for sale in self.sales_data
                if search_text in sale['product_name'].lower() or
                   search_text in str(sale['quantity']) or
                   search_text in sale['sale_date']
            ]
        
        for sale in filtered_data:
            values = (
                sale['sale_id'],
                sale['product_name'],
                f"{sale['quantity']:,}",
                sale['sale_date']
            )
            
            self.sales_tree.insert('', 'end', values=values)
    
    def update_statistics(self):
        if not self.sales_data:
            self.total_sales_label.config(text="0")
            self.transactions_count_label.config(text="0")
            self.current_discount_label.config(text="0%")
            self.registration_date_label.config(text="")
            return

        total_sales = sum(sale['quantity'] for sale in self.sales_data)
        self.total_sales_label.config(text=f"{total_sales:,}")

        transactions_count = len(self.sales_data)
        self.transactions_count_label.config(text=str(transactions_count))

        current_discount = self.partner_data.get('discount_percentage', 0)
        self.current_discount_label.config(text=f"{current_discount}%")

        registration_date = self.partner_data.get('registration_date', '')
        if registration_date:
            self.registration_date_label.config(text=str(registration_date))
    
    def on_search_change(self, *args):
        self.update_sales_table()
    
    def on_sale_double_click(self, event):
        selection = self.sales_tree.selection()
        if selection:
            item = self.sales_tree.item(selection[0])
            sale_id = item['values'][0]
            product_name = item['values'][1]
            quantity = item['values'][2]
            sale_date = item['values'][3]
            
            # Показ детальной информации о продаже
            messagebox.showinfo("Детали продажи", 
                              f"ID продажи: {sale_id}\n"
                              f"Продукт: {product_name}\n"
                              f"Количество: {quantity}\n"
                              f"Дата: {sale_date}")
    
    def export_to_csv(self):
        if not self.sales_data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        try:
            partner_name = self.partner_data['partner_name'].replace(' ', '_')
            current_date = datetime.now().strftime('%Y%m%d')
            default_filename = f"sales_history_{partner_name}_{current_date}.csv"
            
            filename = default_filename
            
            # Экспорт в CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID продажи', 'Продукт', 'Количество', 'Дата продажи']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for sale in self.sales_data:
                    writer.writerow({
                        'ID продажи': sale['sale_id'],
                        'Продукт': sale['product_name'],
                        'Количество': sale['quantity'],
                        'Дата продажи': sale['sale_date']
                    })
            
            messagebox.showinfo("Успех", f"Данные успешно экспортированы в файл {filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {e}")
    
    def refresh_data(self):
        self.load_sales_data()
        messagebox.showinfo("Информация", "Данные обновлены")
    
    def sort_table(self, col):
        items = [(self.sales_tree.set(item, col), item) for item in self.sales_tree.get_children('')]

        items.sort()

        for index, (val, item) in enumerate(items):
            self.sales_tree.move(item, '', index)
