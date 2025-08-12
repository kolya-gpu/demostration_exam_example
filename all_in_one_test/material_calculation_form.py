import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Dict, Any, List
from material_calculator import MaterialCalculator
import re

class MaterialCalculationForm:
    
    def __init__(self, parent, material_calculator: MaterialCalculator):
        self.parent = parent
        self.material_calculator = material_calculator
        self.product_types = []
        self.material_types = []

        self.window = tk.Toplevel(parent)
        self.window.title("Калькулятор материалов")
        self.window.geometry("700x800")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()

        self.center_window()

        self.setup_styles()

        self.create_widgets()

        self.load_data()

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
            'title': tkfont.Font(family="Segoe UI", size=16, weight="bold"),
            'header': tkfont.Font(family="Segoe UI", size=12, weight="bold"),
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

        self.create_calculation_form(main_frame)

        self.create_result_panel(main_frame)

        self.create_example_panel(main_frame)

        self.create_buttons(main_frame)
    
    def create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, 
                               text="Калькулятор необходимого количества материала",
                               font=self.fonts['title'],
                               foreground=self.colors['primary'])
        title_label.pack()

        description_label = ttk.Label(header_frame, 
                                     text="Расчет количества материала для производства продукции с учетом брака",
                                     font=self.fonts['normal'],
                                     foreground=self.colors['secondary'])
        description_label.pack(pady=(5, 0))
    
    def create_calculation_form(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Параметры расчета", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 20))

        form_grid = ttk.Frame(form_frame)
        form_grid.pack(fill=tk.X)

        ttk.Label(form_grid, text="Тип продукции *:", font=self.fonts['header']).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.product_type_var = tk.StringVar()
        self.product_type_combo = ttk.Combobox(form_grid, textvariable=self.product_type_var, width=30, state="readonly")
        self.product_type_combo.grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(form_grid, text="Тип материала *:", font=self.fonts['header']).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.material_type_var = tk.StringVar()
        self.material_type_combo = ttk.Combobox(form_grid, textvariable=self.material_type_var, width=30, state="readonly")
        self.material_type_combo.grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(form_grid, text="Количество продукции *:", font=self.fonts['header']).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        self.product_quantity_var = tk.StringVar()
        self.product_quantity_entry = ttk.Entry(form_grid, textvariable=self.product_quantity_var, width=30)
        self.product_quantity_entry.grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(form_grid, text="Параметр 1 *:", font=self.fonts['header']).grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        self.param1_var = tk.StringVar()
        self.param1_entry = ttk.Entry(form_grid, textvariable=self.param1_var, width=30)
        self.param1_entry.grid(row=3, column=1, sticky='w', pady=5)

        ttk.Label(form_grid, text="Параметр 2 *:", font=self.fonts['header']).grid(row=4, column=0, sticky='w', padx=(0, 10), pady=5)
        self.param2_var = tk.StringVar()
        self.param2_entry = ttk.Entry(form_grid, textvariable=self.param2_var, width=30)
        self.param2_entry.grid(row=4, column=1, sticky='w', pady=5)

        form_grid.grid_columnconfigure(1, weight=1)

        self.product_type_combo.bind('<<ComboboxSelected>>', self.on_product_type_change)
        self.material_type_combo.bind('<<ComboboxSelected>>', self.on_material_type_change)
    
    def create_result_panel(self, parent):
        result_frame = ttk.LabelFrame(parent, text="Результат расчета", padding=15)
        result_frame.pack(fill=tk.X, pady=(0, 20))

        result_content = ttk.Frame(result_frame)
        result_content.pack(fill=tk.X)
        
        ttk.Label(result_content, text="Необходимое количество материала:", font=self.fonts['header']).pack(side=tk.LEFT)
        self.result_label = ttk.Label(result_content, text="", font=self.fonts['header'], foreground=self.colors['success'])
        self.result_label.pack(side=tk.LEFT, padx=(10, 0))

        self.details_text = tk.Text(result_frame, height=6, width=70, font=self.fonts['normal'], wrap=tk.WORD)
        self.details_text.pack(fill=tk.X, pady=(10, 0))

        details_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_example_panel(self, parent):
        example_frame = ttk.LabelFrame(parent, text="Пример расчета", padding=15)
        example_frame.pack(fill=tk.X, pady=(0, 20))

        example_btn = ttk.Button(example_frame, 
                                text="Показать пример расчета",
                                style="Accent.TButton",
                                command=self.show_calculation_example)
        example_btn.pack()

        self.example_text = tk.Text(example_frame, height=8, width=70, font=self.fonts['normal'], wrap=tk.WORD)
        self.example_text.pack(fill=tk.X, pady=(10, 0))

        example_scrollbar = ttk.Scrollbar(example_frame, orient=tk.VERTICAL, command=self.example_text.yview)
        self.example_text.configure(yscrollcommand=example_scrollbar.set)
        example_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=(20, 0))

        calculate_btn = ttk.Button(button_frame, 
                                  text="Рассчитать",
                                  style="Success.TButton",
                                  command=self.calculate_material)
        calculate_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(button_frame, 
                              text="Очистить",
                              style="Warning.TButton",
                              command=self.clear_form)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        close_btn = ttk.Button(button_frame, 
                              text="Закрыть",
                              style="Danger.TButton",
                              command=self.window.destroy)
        close_btn.pack(side=tk.LEFT)
    
    def load_data(self):
        try:
            product_types_result = self.material_calculator.db_manager.fetch_all(
                "SELECT product_type_id, product_type_name, coefficient FROM product_types ORDER BY product_type_name"
            )
            self.product_types = [
                {'id': row[0], 'name': row[1], 'coefficient': row[2]} 
                for row in product_types_result
            ]
            
            material_types_result = self.material_calculator.db_manager.fetch_all(
                "SELECT material_type_id, material_type_name, waste_percentage FROM material_types ORDER BY material_type_name"
            )
            self.material_types = [
                {'id': row[0], 'name': row[1], 'waste_percentage': row[2]} 
                for row in material_types_result
            ]
            
            self.product_type_combo['values'] = [f"{pt['id']} - {pt['name']} (коэф. {pt['coefficient']})" for pt in self.product_types]
            self.material_type_combo['values'] = [f"{mt['id']} - {mt['name']} (брак {mt['waste_percentage']}%)" for mt in self.material_types]
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")
    
    def on_product_type_change(self, event):
        self.clear_result()
    
    def on_material_type_change(self, event):
        self.clear_result()
    
    def validate_input(self) -> bool:
        if not self.product_type_var.get():
            messagebox.showerror("Ошибка валидации", "Выберите тип продукции")
            self.product_type_combo.focus()
            return False
        
        if not self.material_type_var.get():
            messagebox.showerror("Ошибка валидации", "Выберите тип материала")
            self.material_type_combo.focus()
            return False
        
        try:
            quantity = int(self.product_quantity_var.get())
            if quantity <= 0:
                raise ValueError("Количество должно быть положительным")
        except ValueError:
            messagebox.showerror("Ошибка валидации", "Количество продукции должно быть положительным целым числом")
            self.product_quantity_entry.focus()
            return False

        try:
            param1 = float(self.param1_var.get())
            if param1 <= 0:
                raise ValueError("Параметр должен быть положительным")
        except ValueError:
            messagebox.showerror("Ошибка валидации", "Параметр 1 должен быть положительным числом")
            self.param1_entry.focus()
            return False
        
        try:
            param2 = float(self.param2_var.get())
            if param2 <= 0:
                raise ValueError("Параметр должен быть положительным")
        except ValueError:
            messagebox.showerror("Ошибка валидации", "Параметр 2 должен быть положительным числом")
            self.param2_entry.focus()
            return False
        
        return True
    
    def get_selected_ids(self) -> tuple:
        product_type_text = self.product_type_var.get()
        product_type_id = int(product_type_text.split(' - ')[0])
        
        material_type_text = self.material_type_var.get()
        material_type_id = int(material_type_text.split(' - ')[0])
        
        return product_type_id, material_type_id
    
    def calculate_material(self):
        try:
            if not self.validate_input():
                return

            product_type_id, material_type_id = self.get_selected_ids()
            product_quantity = int(self.product_quantity_var.get())
            product_param1 = float(self.param1_var.get())
            product_param2 = float(self.param2_var.get())
            
            result = self.material_calculator.calculate_material_required(
                product_type_id, material_type_id, product_quantity, 
                product_param1, product_param2
            )

            if result == -1:
                messagebox.showerror("Ошибка расчета", 
                                   "Не удалось выполнить расчет. Проверьте правильность введенных данных.")
                return

            self.display_result(result, product_type_id, material_type_id, 
                              product_quantity, product_param1, product_param2)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при расчете: {e}")
    
    def display_result(self, result: int, product_type_id: int, material_type_id: int,
                      product_quantity: int, product_param1: float, product_param2: float):
        self.result_label.config(text=f"{result:,} единиц")

        product_type_info = next((pt for pt in self.product_types if pt['id'] == product_type_id), None)
        material_type_info = next((mt for mt in self.material_types if mt['id'] == material_type_id), None)
        
        if product_type_info and material_type_info:
            material_per_unit = product_param1 * product_param2 * product_type_info['coefficient']
            total_material_needed = material_per_unit * product_quantity
            waste_factor = 1 + (material_type_info['waste_percentage'] / 100.0)
            material_with_waste = total_material_needed * waste_factor

            details_text = f"""Детали расчета:

1. Материал на единицу продукции:
   Параметр 1 × Параметр 2 × Коэффициент типа продукции
   {product_param1} × {product_param2} × {product_type_info['coefficient']} = {material_per_unit:.2f}

2. Общий материал без учета брака:
   Материал на единицу × Количество продукции
   {material_per_unit:.2f} × {product_quantity:,} = {total_material_needed:.2f}

3. Учет брака материала:
   Коэффициент брака: 1 + ({material_type_info['waste_percentage']}% / 100) = {waste_factor:.2f}
   Материал с учетом брака: {total_material_needed:.2f} × {waste_factor:.2f} = {material_with_waste:.2f}

4. Итоговое количество (округлено вверх): {result:,} единиц

Тип продукции: {product_type_info['name']} (коэффициент: {product_type_info['coefficient']})
Тип материала: {material_type_info['name']} (брак: {material_type_info['waste_percentage']}%)
            """
            
            self.details_text.delete('1.0', tk.END)
            self.details_text.insert('1.0', details_text)
    
    def show_calculation_example(self):
        try:
            example_text = self.material_calculator.get_calculation_example()
            self.example_text.delete('1.0', tk.END)
            self.example_text.insert('1.0', example_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении примера: {e}")
    
    def clear_form(self):
        self.product_type_var.set('')
        self.material_type_var.set('')
        self.product_quantity_var.set('')
        self.param1_var.set('')
        self.param2_var.set('')
        self.clear_result()
        self.product_type_combo.focus()
    
    def clear_result(self):
        self.result_label.config(text="")
        self.details_text.delete('1.0', tk.END)
