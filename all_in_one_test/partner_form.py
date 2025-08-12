import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Dict, Any, Optional
from database_manager import DatabaseManager
import re

class PartnerForm:
    
    def __init__(self, parent, db_manager: DatabaseManager, title: str = "Партнер", partner_data: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.db_manager = db_manager
        self.partner_data = partner_data
        self.result = None

        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        self.center_window()

        self.setup_styles()

        self.create_widgets()

        if partner_data:
            self.fill_form_data()

        self.window.wait_window()
    
    def setup_styles(self):
        """Настройка стилей формы"""
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

        title_label = ttk.Label(main_frame, text="Данные партнера", font=self.fonts['title'])
        title_label.pack(pady=(0, 20))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)

        self.create_field(form_frame, "Название партнера *:", "partner_name", 0, required=True)

        self.create_field(form_frame, "Контактное лицо:", "contact_person", 1)

        self.create_field(form_frame, "Телефон:", "phone", 2, validation=self.validate_phone)

        self.create_field(form_frame, "Email:", "email", 3, validation=self.validate_email)

        self.create_field(form_frame, "Адрес:", "address", 4, field_type="text")

        self.create_buttons(main_frame)

        self.window.bind('<Return>', lambda e: self.save_partner())
        self.window.bind('<Escape>', lambda e: self.cancel())

        self.fields['partner_name'].focus()
    
    def create_field(self, parent, label_text: str, field_name: str, row: int, 
                    required: bool = False, validation: callable = None, field_type: str = "entry"):
        label = ttk.Label(parent, text=label_text, font=self.fonts['normal'])
        label.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=5)

        if field_type == "text":
            field = tk.Text(parent, height=3, width=40, font=self.fonts['normal'])
        else:
            field = ttk.Entry(parent, width=40, font=self.fonts['normal'])
        
        field.grid(row=row, column=1, sticky='ew', padx=(0, 0), pady=5)

        if not hasattr(self, 'fields'):
            self.fields = {}
        self.fields[field_name] = field

        if not hasattr(self, 'field_validations'):
            self.field_validations = {}
        if validation:
            self.field_validations[field_name] = validation

        if not hasattr(self, 'required_fields'):
            self.required_fields = set()
        if required:
            self.required_fields.add(field_name)
        
        parent.grid_columnconfigure(1, weight=1)
    
    def create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=(20, 0))
        
        save_btn = ttk.Button(button_frame, 
                             text="Сохранить",
                             style="Success.TButton",
                             command=self.save_partner)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, 
                               text="Отмена",
                               style="Danger.TButton",
                               command=self.cancel)
        cancel_btn.pack(side=tk.LEFT)
    
    def fill_form_data(self):
        if not self.partner_data:
            return

        self.fields['partner_name'].delete(0, tk.END)
        self.fields['partner_name'].insert(0, self.partner_data.get('partner_name', ''))
        
        self.fields['contact_person'].delete(0, tk.END)
        self.fields['contact_person'].insert(0, self.partner_data.get('contact_person', ''))
        
        self.fields['phone'].delete(0, tk.END)
        self.fields['phone'].insert(0, self.partner_data.get('phone', ''))
        
        self.fields['email'].delete(0, tk.END)
        self.fields['email'].insert(0, self.partner_data.get('email', ''))
        
        self.fields['address'].delete('1.0', tk.END)
        self.fields['address'].insert('1.0', self.partner_data.get('address', ''))
    
    def get_field_value(self, field_name: str) -> str:
        field = self.fields[field_name]
        if isinstance(field, tk.Text):
            return field.get('1.0', tk.END).strip()
        else:
            return field.get().strip()
    
    def validate_required_fields(self) -> bool:
        for field_name in self.required_fields:
            value = self.get_field_value(field_name)
            if not value:
                messagebox.showerror("Ошибка валидации", 
                                   f"Поле '{field_name.replace('_', ' ').title()}' обязательно для заполнения")
                self.fields[field_name].focus()
                return False
        return True
    
    def validate_phone(self, phone: str) -> bool:
        if not phone:
            return True

        phone_pattern = r'^[\d\s\(\)\-\+]+$'
        if not re.match(phone_pattern, phone):
            messagebox.showerror("Ошибка валидации", 
                               "Номер телефона содержит недопустимые символы")
            return False
        
        # Проверка минимальной длины
        digits_only = re.sub(r'[\s\(\)\-\+]', '', phone)
        if len(digits_only) < 10:
            messagebox.showerror("Ошибка валидации", 
                               "Номер телефона должен содержать минимум 10 цифр")
            return False
        
        return True
    
    def validate_email(self, email: str) -> bool:
        if not email:
            return True

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Ошибка валидации", 
                               "Email адрес имеет неверный формат")
            return False
        
        return True
    
    def validate_form(self) -> bool:
        if not self.validate_required_fields():
            return False

        for field_name, validation_func in self.field_validations.items():
            value = self.get_field_value(field_name)
            if not validation_func(value):
                self.fields[field_name].focus()
                return False
        
        return True
    
    def save_partner(self):
        try:
            if not self.validate_form():
                return

            partner_data = {
                'partner_name': self.get_field_value('partner_name'),
                'contact_person': self.get_field_value('contact_person'),
                'phone': self.get_field_value('phone'),
                'email': self.get_field_value('email'),
                'address': self.get_field_value('address')
            }

            if self.partner_data:
                success = self.db_manager.update_partner(self.partner_data['partner_id'], partner_data)
                if success:
                    self.result = partner_data
                    messagebox.showinfo("Успех", "Данные партнера успешно обновлены")
                    self.window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить данные партнера")
            else:
                success = self.db_manager.add_partner(partner_data)
                if success:
                    self.result = partner_data
                    messagebox.showinfo("Успех", "Партнер успешно добавлен")
                    self.window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить партнера")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении: {e}")
    
    def cancel(self):
        if self.partner_data:
            result = messagebox.askyesno("Подтверждение", 
                                       "Вы действительно хотите отменить изменения?\n"
                                       "Все несохраненные данные будут потеряны.")
            if not result:
                return
        
        self.result = None
        self.window.destroy()
