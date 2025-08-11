# inventory.py - Система инвентаря (Singleton)

from typing import Dict, List, Any

class Inventory:
    """Класс для управления инвентарем персонажа или группы (Singleton)."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Inventory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Предотвращаем повторную инициализацию
        if not Inventory._initialized:
            self.gold = 0
            self.items: Dict[Any, int] = {}  # объект предмета: количество
            Inventory._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Возвращает экземпляр инвентаря (создает, если не существует)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Сбрасывает инстанс для тестирования."""
        cls._instance = None
        cls._initialized = False
    
    def add_gold(self, amount: int) -> None:
        """
        Добавляет золото в инвентарь.
        
        :param amount: Количество золота для добавления
        """
        if amount > 0:
            self.gold += amount
    
    def remove_gold(self, amount: int) -> bool:
        """
        Удаляет золото из инвентаря.
        
        :param amount: Количество золота для удаления
        :return: True если успешно, False если недостаточно золота
        """
        if amount <= 0:
            return True
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def get_gold(self) -> int:
        """Возвращает количество золота в инвентаре."""
        return self.gold
    
    def add_item(self, item_object: Any, quantity: int = 1) -> None:
        """
        Добавляет предмет в инвентарь.
        
        :param item_object: Объект предмета
        :param quantity: Количество предметов для добавления
        """
        if quantity > 0:
            if item_object in self.items:
                self.items[item_object] += quantity
            else:
                self.items[item_object] = quantity
    
    def remove_item(self, item_object: Any, quantity: int = 1) -> bool:
        """
        Удаляет предмет из инвентаря.
        
        :param item_object: Объект предмета
        :param quantity: Количество предметов для удаления
        :return: True если успешно, False если недостаточно предметов
        """
        if item_object not in self.items:
            return False
        
        if quantity <= 0:
            return True
            
        if self.items[item_object] >= quantity:
            self.items[item_object] -= quantity
            if self.items[item_object] == 0:
                del self.items[item_object]
            return True
        return False
    
    def get_item_count(self, item_object: Any) -> int:
        """
        Возвращает количество конкретного предмета в инвентаре.
        
        :param item_object: Объект предмета
        :return: Количество предметов
        """
        return self.items.get(item_object, 0)
    
    def has_item(self, item_object: Any, quantity: int = 1) -> bool:
        """
        Проверяет, есть ли нужное количество предмета в инвентаре.
        
        :param item_object: Объект предмета
        :param quantity: Требуемое количество
        :return: True если есть достаточно предметов, False если нет
        """
        return self.get_item_count(item_object) >= quantity
    
    def get_all_items(self) -> Dict[Any, int]:
        """
        Возвращает копию словаря всех предметов в инвентаре.
        
        :return: Словарь предметов
        """
        return self.items.copy()
    
    def is_empty(self) -> bool:
        """
        Проверяет, пуст ли инвентарь.
        
        :return: True если инвентарь пуст, False если есть предметы
        """
        return len(self.items) == 0 and self.gold == 0
    
    def clear(self) -> None:
        """Очищает весь инвентарь."""
        self.gold = 0
        self.items.clear()
    
    def get_total_items_count(self) -> int:
        """
        Возвращает общее количество предметов в инвентаре.
        
        :return: Общее количество предметов
        """
        return sum(self.items.values())
    
    def __str__(self) -> str:
        """Возвращает строковое представление инвентаря."""
        if self.is_empty():
            return "Инвентарь пуст"
        
        result = []
        if self.gold > 0:
            result.append(f"💰 Золото: {self.gold}")
        
        if self.items:
            result.append("Предметы:")
            for item_object, quantity in self.items.items():
                # Получаем имя предмета из объекта, если возможно
                item_name = getattr(item_object, 'name', str(item_object))
                result.append(f"  {item_name}: {quantity}")
        
        return "\n".join(result)
    
    def __repr__(self) -> str:
        """Возвращает формальное строковое представление инвентаря."""
        return f"Inventory(gold={self.gold}, items={len(self.items)})"


# Фабричная функция для удобного получения инвентаря
def get_inventory() -> Inventory:
    """
    Возвращает экземпляр инвентаря (Singleton).
    Это основная точка доступа к инвентарю из других модулей.
    """
    return Inventory.get_instance()