import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
import os
from typing import Dict, Any, Optional
from database_manager import DatabaseManager
from material_calculator import MaterialCalculator
from partner_form import PartnerForm
from sales_history_form import SalesHistoryForm
from material_calculation_form import MaterialCalculationForm

class PartnersGUI:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Система работы с партнерами компании")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        self.db_manager = DatabaseManager()
        self.material_calculator = MaterialCalculator(self.db_manager)

        self.current_partner_id = None
        self.partners_data = []

        self.setup_styles()

        self.create_widgets()

        self.initialize_database()

        self.load_partners_data()
    
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
            'title': tkfont.Font(family="Segoe UI", size=16, weight="bold"),
            'header': tkfont.Font(family="Segoe UI", size=12, weight="bold"),
            'normal': tkfont.Font(family="Segoe UI", size=10),
            'small': tkfont.Font(family="Segoe UI", size=9)
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview", 
                       background=self.colors['light'],
                       foreground=self.colors['dark'],
                       rowheight=25,
                       fieldbackground=self.colors['light'])
        
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=self.fonts['header'])
        
        style.configure("Accent.TButton",
                       background=self.colors['accent'],
                       foreground=self.colors['white'])
        
        style.configure("Success.TButton",
                       background=self.colors['success'],
                       foreground=self.colors['white'])
        
        style.configure("Warning.TButton",
                       background=self.colors['warning'],
                       foreground=self.colors['white'])
        
        style.configure("Danger.TButton",
                       background=self.colors['danger'],
                       foreground=self.colors['white'])
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_header(main_frame)
        
        self.create_toolbar(main_frame)
        
        self.create_main_content(main_frame)
        
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        try:
            logo_path = os.path.join("KOD_09_02_07-2-2025_Prilozhenia_k_obraztsu_zadania_Tom_1", "Ресурсы", "Мастер пол.png")
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = ttk.Label(header_frame, image=logo_photo)
                logo_label.image = logo_photo
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
        
        title_label = ttk.Label(header_frame, 
                               text="Система работы с партнерами компании",
                               font=self.fonts['title'],
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        calc_btn = ttk.Button(header_frame, 
                             text="Калькулятор материалов",
                             style="Accent.TButton",
                             command=self.open_material_calculator)
        calc_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_toolbar(self, parent):
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_btn = ttk.Button(toolbar_frame, 
                            text="Добавить партнера",
                            style="Success.TButton",
                            command=self.add_partner)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_btn = ttk.Button(toolbar_frame, 
                             text="Редактировать",
                             style="Accent.TButton",
                             command=self.edit_partner)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = ttk.Button(toolbar_frame, 
                               text="Удалить",
                               style="Danger.TButton",
                               command=self.delete_partner)
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        history_btn = ttk.Button(toolbar_frame, 
                                text="История продаж",
                                style="Warning.TButton",
                                command=self.view_sales_history)
        history_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = ttk.Button(toolbar_frame, 
                                text="Обновить",
                                style="Accent.TButton",
                                command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_main_content(self, parent):
        """Создание основной области с данными"""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Название', 'Контактное лицо', 'Телефон', 'Email', 'Адрес', 'Дата регистрации', 'Общие продажи', 'Скидка (%)')
        
        self.partners_tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.partners_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.partners_tree.column(col, width=120, minwidth=100)
        
        self.partners_tree.column('ID', width=50, minwidth=50)
        self.partners_tree.column('Название', width=200, minwidth=150)
        self.partners_tree.column('Email', width=150, minwidth=120)
        self.partners_tree.column('Общие продажи', width=100, minwidth=80)
        self.partners_tree.column('Скидка (%)', width=80, minwidth=60)
        
        v_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.partners_tree.yview)
        h_scrollbar = ttk.Scrollbar(content_frame, orient=tk.HORIZONTAL, command=self.partners_tree.xview)
        self.partners_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.partners_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        self.partners_tree.bind('<Double-1>', self.on_partner_double_click)
        self.partners_tree.bind('<<TreeviewSelect>>', self.on_partner_select)
        
        self.create_info_panel(parent)
    
    def create_info_panel(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Информация о партнере", padding=10)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        left_col = ttk.Frame(info_grid)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_col, text="Название:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.info_name_label = ttk.Label(left_col, text="", font=self.fonts['header'])
        self.info_name_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(left_col, text="Контактное лицо:").grid(row=1, column=0, sticky='w', padx=(0, 5))
        self.info_contact_label = ttk.Label(left_col, text="")
        self.info_contact_label.grid(row=1, column=1, sticky='w')
        
        ttk.Label(left_col, text="Телефон:").grid(row=2, column=0, sticky='w', padx=(0, 5))
        self.info_phone_label = ttk.Label(left_col, text="")
        self.info_phone_label.grid(row=2, column=1, sticky='w')
        
        right_col = ttk.Frame(info_grid)
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(right_col, text="Email:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.info_email_label = ttk.Label(right_col, text="")
        self.info_email_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(right_col, text="Адрес:").grid(row=1, column=0, sticky='w', padx=(0, 5))
        self.info_address_label = ttk.Label(right_col, text="")
        self.info_address_label.grid(row=1, column=1, sticky='w')
        
        ttk.Label(right_col, text="Общие продажи:").grid(row=2, column=0, sticky='w', padx=(0, 5))
        self.info_sales_label = ttk.Label(right_col, text="", font=self.fonts['header'])
        self.info_sales_label.grid(row=2, column=1, sticky='w')
        
        discount_frame = ttk.Frame(info_frame)
        discount_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(discount_frame, text="Текущая скидка:", font=self.fonts['header']).pack(side=tk.LEFT)
        self.info_discount_label = ttk.Label(discount_frame, text="", font=self.fonts['header'], foreground=self.colors['success'])
        self.info_discount_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_status_bar(self, parent):
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе", font=self.fonts['small'])
        self.status_label.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(status_frame, text="", font=self.fonts['small'])
        self.count_label.pack(side=tk.RIGHT)
    
    def initialize_database(self):
        try:
            if not self.db_manager.connect():
                messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
                return False
            
            if not self.db_manager.create_tables():
                messagebox.showerror("Ошибка", "Не удалось создать таблицы базы данных")
                return False
            
            resources_path = os.path.join("KOD_09_02_07-2-2025_Prilozhenia_k_obraztsu_zadania_Tom_1", "Ресурсы")
            if os.path.exists(resources_path):
                if self.db_manager.import_data_from_excel(resources_path):
                    self.status_label.config(text="База данных инициализирована успешно")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось импортировать все данные")
            else:
                messagebox.showwarning("Предупреждение", "Папка с ресурсами не найдена")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации базы данных: {e}")
            return False
    
    def load_partners_data(self):
        try:
            self.partners_data = self.db_manager.get_partners_list()
            self.update_partners_tree()
            self.update_status()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")
    
    def update_partners_tree(self):
        for item in self.partners_tree.get_children():
            self.partners_tree.delete(item)
        
        search_text = self.search_var.get().lower()
        filtered_data = self.partners_data
        
        if search_text:
            filtered_data = [
                partner for partner in self.partners_data
                if search_text in partner['partner_name'].lower() or
                   (partner['contact_person'] and search_text in partner['contact_person'].lower()) or
                   (partner['email'] and search_text in partner['email'].lower())
            ]

        for partner in filtered_data:
            values = (
                partner['partner_id'],
                partner['partner_name'],
                partner['contact_person'] or '',
                partner['phone'] or '',
                partner['email'] or '',
                partner['address'] or '',
                partner['registration_date'] or '',
                f"{partner['total_sales']:,}" if partner['total_sales'] else '0',
                f"{partner['discount_percentage']}%"
            )

            tags = ()
            if partner['discount_percentage'] >= 15:
                tags = ('high_discount',)
            elif partner['discount_percentage'] >= 10:
                tags = ('medium_discount',)
            elif partner['discount_percentage'] >= 5:
                tags = ('low_discount',)
            
            self.partners_tree.insert('', 'end', values=values, tags=tags)
        
        self.partners_tree.tag_configure('high_discount', background=self.colors['success'])
        self.partners_tree.tag_configure('medium_discount', background=self.colors['warning'])
        self.partners_tree.tag_configure('low_discount', background=self.colors['accent'])
    
    def update_status(self):
        total_partners = len(self.partners_data)
        self.count_label.config(text=f"Всего партнеров: {total_partners}")
        
        if total_partners == 0:
            self.status_label.config(text="Нет данных для отображения")
        else:
            self.status_label.config(text="Данные загружены успешно")
    
    def on_search_change(self, *args):
        self.update_partners_tree()
    
    def on_partner_select(self, event):
        selection = self.partners_tree.selection()
        if selection:
            item = self.partners_tree.item(selection[0])
            partner_id = item['values'][0]
            self.show_partner_info(partner_id)
    
    def on_partner_double_click(self, event):
        selection = self.partners_tree.selection()
        if selection:
            item = self.partners_tree.item(selection[0])
            partner_id = item['values'][0]
            self.edit_partner(partner_id)
    
    def show_partner_info(self, partner_id: int):
        partner = next((p for p in self.partners_data if p['partner_id'] == partner_id), None)
        if partner:
            self.current_partner_id = partner_id
            
            self.info_name_label.config(text=partner['partner_name'])
            self.info_contact_label.config(text=partner['contact_person'] or 'Не указано')
            self.info_phone_label.config(text=partner['phone'] or 'Не указано')
            self.info_email_label.config(text=partner['email'] or 'Не указано')
            self.info_address_label.config(text=partner['address'] or 'Не указано')
            self.info_sales_label.config(text=f"{partner['total_sales']:,}" if partner['total_sales'] else '0')
            self.info_discount_label.config(text=f"{partner['discount_percentage']}%")
    
    def add_partner(self):
        partner_form = PartnerForm(self.root, self.db_manager, title="Добавление партнера")
        if partner_form.result:
            self.load_partners_data()
            messagebox.showinfo("Успех", "Партнер успешно добавлен")
    
    def edit_partner(self, partner_id: Optional[int] = None):
        if partner_id is None:
            selection = self.partners_tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите партнера для редактирования")
                return
            item = self.partners_tree.item(selection[0])
            partner_id = item['values'][0]
        
        partner = next((p for p in self.partners_data if p['partner_id'] == partner_id), None)
        if partner:
            partner_form = PartnerForm(self.root, self.db_manager, 
                                     title="Редактирование партнера", 
                                     partner_data=partner)
            if partner_form.result:
                self.load_partners_data()
                messagebox.showinfo("Успех", "Данные партнера успешно обновлены")
    
    def delete_partner(self):
        selection = self.partners_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите партнера для удаления")
            return
        
        item = self.partners_tree.item(selection[0])
        partner_id = item['values'][0]
        partner_name = item['values'][1]
        
        result = messagebox.askyesno("Подтверждение удаления", 
                                   f"Вы действительно хотите удалить партнера '{partner_name}'?\n\n"
                                   "Это действие нельзя отменить!")
        
        if result:
            try:
                if self.db_manager.delete_partner(partner_id):
                    self.load_partners_data()
                    messagebox.showinfo("Успех", "Партнер успешно удален")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить партнера")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
    
    def view_sales_history(self):
        if self.current_partner_id is None:
            messagebox.showwarning("Предупреждение", "Выберите партнера для просмотра истории продаж")
            return
        
        partner = next((p for p in self.partners_data if p['partner_id'] == self.current_partner_id), None)
        if partner:
            sales_form = SalesHistoryForm(self.root, self.db_manager, partner)
    
    def open_material_calculator(self):
        calc_form = MaterialCalculationForm(self.root, self.material_calculator)
    
    def refresh_data(self):
        self.load_partners_data()
        messagebox.showinfo("Информация", "Данные обновлены")
    
    def sort_treeview(self, col):
        items = [(self.partners_tree.set(item, col), item) for item in self.partners_tree.get_children('')]

        items.sort()

        for index, (val, item) in enumerate(items):
            self.partners_tree.move(item, '', index)
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Произошла критическая ошибка: {e}")
        finally:
            if self.db_manager:
                self.db_manager.disconnect()

if __name__ == "__main__":
    app = PartnersGUI()
    app.run()
