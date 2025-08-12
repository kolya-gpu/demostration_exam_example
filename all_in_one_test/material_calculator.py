from typing import Optional
from database_manager import DatabaseManager

class MaterialCalculator:
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def calculate_material_required(self, 
                                  product_type_id: int, 
                                  material_type_id: int, 
                                  product_quantity: int, 
                                  product_param1: float, 
                                  product_param2: float) -> int:
        try:
            if not self._validate_input_parameters(product_type_id, material_type_id, 
                                                 product_quantity, product_param1, product_param2):
                return -1

            product_coefficient = self._get_product_type_coefficient(product_type_id)
            if product_coefficient is None:
                return -1

            waste_percentage = self._get_material_waste_percentage(material_type_id)
            if waste_percentage is None:
                return -1

            material_per_unit = product_param1 * product_param2 * product_coefficient

            total_material_needed = material_per_unit * product_quantity

            waste_factor = 1 + (waste_percentage / 100.0)
            material_with_waste = total_material_needed * waste_factor

            final_material_quantity = int(material_with_waste + 0.99)
            
            return final_material_quantity
            
        except Exception as e:
            print(f"Ошибка расчета материала: {e}")
            return -1
    
    def _validate_input_parameters(self, 
                                 product_type_id: int, 
                                 material_type_id: int, 
                                 product_quantity: int, 
                                 product_param1: float, 
                                 product_param2: float) -> bool:
        if not isinstance(product_type_id, int) or not isinstance(material_type_id, int):
            return False
        
        if not isinstance(product_quantity, int) or not isinstance(product_param1, float) or not isinstance(product_param2, float):
            return False
        
        if product_quantity <= 0:
            return False
        
        if product_param1 <= 0 or product_param2 <= 0:
            return False
        
        if not self._product_type_exists(product_type_id):
            return False
        
        if not self._material_type_exists(material_type_id):
            return False
        
        return True
    
    def _product_type_exists(self, product_type_id: int) -> bool:
        result = self.db_manager.fetch_one(
            "SELECT COUNT(*) FROM product_types WHERE product_type_id = ?",
            (product_type_id,)
        )
        return result and result[0] > 0
    
    def _material_type_exists(self, material_type_id: int) -> bool:
        result = self.db_manager.fetch_one(
            "SELECT COUNT(*) FROM material_types WHERE material_type_id = ?",
            (material_type_id,)
        )
        return result and result[0] > 0
    
    def _get_product_type_coefficient(self, product_type_id: int) -> Optional[float]:
        result = self.db_manager.fetch_one(
            "SELECT coefficient FROM product_types WHERE product_type_id = ?",
            (product_type_id,)
        )
        return result[0] if result else None
    
    def _get_material_waste_percentage(self, material_type_id: int) -> Optional[float]:
        result = self.db_manager.fetch_one(
            "SELECT waste_percentage FROM material_types WHERE material_type_id = ?",
            (material_type_id,)
        )
        return result[0] if result else None
    
    def get_calculation_example(self) -> str:
        try:
            product_type_result = self.db_manager.fetch_one("SELECT product_type_id, coefficient FROM product_types LIMIT 1")
            material_type_result = self.db_manager.fetch_one("SELECT material_type_id, waste_percentage FROM material_types LIMIT 1")
            
            if not product_type_result or not material_type_result:
                return "Недостаточно данных для примера расчета"
            
            product_type_id = product_type_result[0]
            product_coefficient = product_type_result[1]
            material_type_id = material_type_result[0]
            waste_percentage = material_type_result[1]
            
            product_quantity = 100
            product_param1 = 2.5
            product_param2 = 1.8
            
            result = self.calculate_material_required(
                product_type_id, material_type_id, product_quantity, 
                product_param1, product_param2
            )
            
            if result == -1:
                return "Ошибка при расчете примера"
            
            example_text = f"""
Пример расчета необходимого количества материала:

Параметры:
- Тип продукции ID: {product_type_id} (коэффициент: {product_coefficient})
- Тип материала ID: {material_type_id} (брак: {waste_percentage}%)
- Количество продукции: {product_quantity} шт.
- Параметр 1: {product_param1}
- Параметр 2: {product_param2}

Расчет:
1. Материал на единицу = {product_param1} × {product_param2} × {product_coefficient} = {product_param1 * product_param2 * product_coefficient}
2. Общий материал без брака = {product_param1 * product_param2 * product_coefficient} × {product_quantity} = {(product_param1 * product_param2 * product_coefficient) * product_quantity}
3. Коэффициент брака = 1 + ({waste_percentage}% / 100) = {1 + (waste_percentage / 100)}
4. Итоговое количество = {(product_param1 * product_param2 * product_coefficient) * product_quantity} × {1 + (waste_percentage / 100)} = {result} ед.

Результат: {result} единиц материала
            """
            
            return example_text.strip()
            
        except Exception as e:
            return f"Ошибка при создании примера: {e}"
