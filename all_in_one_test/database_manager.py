import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    
    def __init__(self, db_path: str = "partners_system.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self) -> bool:
        try:
            with open('database_script.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            cursor = self.connection.cursor()
            cursor.executescript(sql_script)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")
            return False
    
    def import_data_from_excel(self, resources_path: str) -> bool:
        try:
            material_types_file = os.path.join(resources_path, "Material_type_import.xlsx")
            if os.path.exists(material_types_file):
                df = pd.read_excel(material_types_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT OR IGNORE INTO material_types (material_type_name, waste_percentage) VALUES (?, ?)",
                        (row.iloc[0], row.iloc[1] if len(row) > 1 else 0.0)
                    )
            
            product_types_file = os.path.join(resources_path, "Product_type_import.xlsx")
            if os.path.exists(product_types_file):
                df = pd.read_excel(product_types_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT OR IGNORE INTO product_types (product_type_name, coefficient) VALUES (?, ?)",
                        (row.iloc[0], row.iloc[1] if len(row) > 1 else 1.0)
                    )
            
            materials_file = os.path.join(resources_path, "Material_type_import.xlsx")
            if os.path.exists(materials_file):
                df = pd.read_excel(materials_file)
                for _, row in df.iterrows():
                    if len(row) > 2:
                        material_name = row.iloc[2] if len(row) > 2 else row.iloc[0]
                        material_type_name = row.iloc[0]
                        material_type_id = self.get_material_type_id(material_type_name)
                        if material_type_id:
                            self.execute_query(
                                "INSERT OR IGNORE INTO materials (material_name, material_type_id) VALUES (?, ?)",
                                (material_name, material_type_id)
                            )
            
            products_file = os.path.join(resources_path, "Products_import.xlsx")
            if os.path.exists(products_file):
                df = pd.read_excel(products_file)
                for _, row in df.iterrows():
                    if len(row) > 1:
                        product_name = row.iloc[0]
                        product_type_name = row.iloc[1]
                        product_type_id = self.get_product_type_id(product_type_name)
                        if product_type_id:
                            self.execute_query(
                                "INSERT OR IGNORE INTO products (product_name, product_type_id) VALUES (?, ?)",
                                (product_name, product_type_id)
                            )

            partners_file = os.path.join(resources_path, "Partners_import.xlsx")
            if os.path.exists(partners_file):
                df = pd.read_excel(partners_file)
                for _, row in df.iterrows():
                    partner_name = row.iloc[0]
                    contact_person = row.iloc[1] if len(row) > 1 else None
                    phone = row.iloc[2] if len(row) > 2 else None
                    email = row.iloc[3] if len(row) > 3 else None
                    address = row.iloc[4] if len(row) > 4 else None
                    
                    self.execute_query(
                        """INSERT OR IGNORE INTO partners 
                           (partner_name, contact_person, phone, email, address) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (partner_name, contact_person, phone, email, address)
                    )

            partner_products_file = os.path.join(resources_path, "Partner_products_import.xlsx")
            if os.path.exists(partner_products_file):
                df = pd.read_excel(partner_products_file)
                for _, row in df.iterrows():
                    partner_name = row.iloc[0]
                    product_name = row.iloc[1]
                    
                    partner_id = self.get_partner_id(partner_name)
                    product_id = self.get_product_id(product_name)
                    
                    if partner_id and product_id:
                        self.execute_query(
                            "INSERT OR IGNORE INTO partner_products (partner_id, product_id) VALUES (?, ?)",
                            (partner_id, product_id)
                        )

            self._add_sample_sales_data()
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Ошибка импорта данных: {e}")
            return False
    
    def _add_sample_sales_data(self):
        try:
            partners = self.fetch_all("SELECT partner_id FROM partners LIMIT 5")
            products = self.fetch_all("SELECT product_id FROM products LIMIT 5")
            
            if partners and products:
                for i in range(20):
                    partner_id = partners[i % len(partners)][0]
                    product_id = products[i % len(products)][0]
                    quantity = (i + 1) * 100
                    sale_date = datetime.now().replace(day=1, month=((i % 12) + 1)).strftime('%Y-%m-%d')
                    
                    self.execute_query(
                        "INSERT OR IGNORE INTO sales (partner_id, product_id, quantity, sale_date) VALUES (?, ?, ?, ?)",
                        (partner_id, product_id, quantity, sale_date)
                    )
        except Exception as e:
            print(f"Ошибка добавления тестовых данных продаж: {e}")
    
    def get_material_type_id(self, material_type_name: str) -> Optional[int]:
        result = self.fetch_one(
            "SELECT material_type_id FROM material_types WHERE material_type_name = ?",
            (material_type_name,)
        )
        return result[0] if result else None
    
    def get_product_type_id(self, product_type_name: str) -> Optional[int]:
        result = self.fetch_one(
            "SELECT product_type_id FROM product_types WHERE product_type_name = ?",
            (product_type_name,)
        )
        return result[0] if result else None
    
    def get_partner_id(self, partner_name: str) -> Optional[int]:
        result = self.fetch_one(
            "SELECT partner_id FROM partners WHERE partner_name = ?",
            (partner_name,)
        )
        return result[0] if result else None
    
    def get_product_id(self, product_name: str) -> Optional[int]:
        result = self.fetch_one(
            "SELECT product_id FROM products WHERE product_name = ?",
            (product_name,)
        )
        return result[0] if result else None
    
    def execute_query(self, query: str, params: tuple = ()) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return True
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return False
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
    
    def get_partners_list(self) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            p.partner_id,
            p.partner_name,
            p.contact_person,
            p.phone,
            p.email,
            p.address,
            p.registration_date,
            COALESCE(SUM(s.quantity), 0) as total_sales,
            CASE 
                WHEN COALESCE(SUM(s.quantity), 0) < 10000 THEN 0
                WHEN COALESCE(SUM(s.quantity), 0) < 50000 THEN 5
                WHEN COALESCE(SUM(s.quantity), 0) < 300000 THEN 10
                ELSE 15
            END as discount_percentage
        FROM partners p
        LEFT JOIN sales s ON p.partner_id = s.partner_id
        GROUP BY p.partner_id
        ORDER BY p.partner_name
        """
        
        results = self.fetch_all(query)
        partners = []
        
        for row in results:
            partners.append({
                'partner_id': row[0],
                'partner_name': row[1],
                'contact_person': row[2],
                'phone': row[3],
                'email': row[4],
                'address': row[5],
                'registration_date': row[6],
                'total_sales': row[7],
                'discount_percentage': row[8]
            })
        
        return partners
    
    def get_partner_sales_history(self, partner_id: int) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            s.sale_id,
            p.product_name,
            s.quantity,
            s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.partner_id = ?
        ORDER BY s.sale_date DESC
        """
        
        results = self.fetch_all(query, (partner_id,))
        sales_history = []
        
        for row in results:
            sales_history.append({
                'sale_id': row[0],
                'product_name': row[1],
                'quantity': row[2],
                'sale_date': row[3]
            })
        
        return sales_history
    
    def add_partner(self, partner_data: Dict[str, Any]) -> bool:
        query = """
        INSERT INTO partners (partner_name, contact_person, phone, email, address)
        VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            partner_data.get('partner_name'),
            partner_data.get('contact_person'),
            partner_data.get('phone'),
            partner_data.get('email'),
            partner_data.get('address')
        )
        
        return self.execute_query(query, params)
    
    def update_partner(self, partner_id: int, partner_data: Dict[str, Any]) -> bool:
        query = """
        UPDATE partners 
        SET partner_name = ?, contact_person = ?, phone = ?, email = ?, address = ?
        WHERE partner_id = ?
        """
        
        params = (
            partner_data.get('partner_name'),
            partner_data.get('contact_person'),
            partner_data.get('phone'),
            partner_data.get('email'),
            partner_data.get('address'),
            partner_id
        )
        
        return self.execute_query(query, params)
    
    def delete_partner(self, partner_id: int) -> bool:
        self.execute_query("DELETE FROM partner_products WHERE partner_id = ?", (partner_id,))
        self.execute_query("DELETE FROM sales WHERE partner_id = ?", (partner_id,))
        
        return self.execute_query("DELETE FROM partners WHERE partner_id = ?", (partner_id,))
