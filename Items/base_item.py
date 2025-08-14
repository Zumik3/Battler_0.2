# base_item.py - Базовый класс предмета

from typing import Dict, Any, List, Never, Optional
from abc import ABC, abstractmethod

class BaseItem(ABC):
    """Базовый класс для всех предметов в игре."""
    
    # Константы для типов предметов
    CONSUMABLE = 0
    WEAPON = 1
    ARMOR = 2
    ACCESSORY = 3
    
    # Константы для редкости
    COMMON = 0      # Обычный
    UNCOMMON = 1    # Необычный
    RARE = 2        # Редкий
    EPIC = 3        # Эпический
    LEGENDARY = 4   # Легендарный
    
    def __init__(self, name: str, item_type: int, level: int = 1, rarity: int = 0, properties: Dict[str, Any] = {}):
        """
        Инициализация базового предмета.
        
        :param name: Название предмета
        :param item_type: Тип предмета (0-consumable, 1-оружие, 2-броня, 3-аксессуар)
        :param level: Уровень предмета
        :param rarity: Редкость предмета (0-4)
        :param properties: Словарь свойств предмета
        """
        self.name = name
        self.item_type = item_type  # 0-consumable, 1-оружие, 2-броня, 3-аксессуар
        self.level = level
        self.rarity = rarity
        self.color = self.get_rarity_color()
        self.properties = properties if properties is not None else {}
        
        # Валидация типа предмета
        if self.item_type not in [0, 1, 2, 3]:
            raise ValueError("Тип предмета должен быть 0, 1, 2 или 3")
        
        # Валидация редкости
        if self.rarity not in [0, 1, 2, 3, 4]:
            raise ValueError("Редкость предмета должна быть от 0 до 4")
        
        # Валидация уровня
        if self.level < 1:
            raise ValueError("Уровень предмета должен быть положительным числом")
    
    def get_property(self, property_name: str, default_value: Any = None) -> Any:
        """
        Получает значение свойства предмета.
        
        :param property_name: Название свойства
        :param default_value: Значение по умолчанию, если свойство не найдено
        :return: Значение свойства или значение по умолчанию
        """
        return self.properties.get(property_name, default_value)
    
    def set_property(self, property_name: str, value: Any) -> None:
        """
        Устанавливает значение свойства предмета.
        
        :param property_name: Название свойства
        :param value: Значение свойства
        """
        self.properties[property_name] = value
    
    def get_all_properties(self) -> Dict[str, Any]:
        """
        Возвращает все свойства предмета.
        
        :return: Словарь всех свойств
        """
        return self.properties.copy()
    
    def is_consumable(self) -> bool:
        """Проверяет, является ли предмет расходуемым."""
        return self.item_type == 0
    
    def is_weapon(self) -> bool:
        """Проверяет, является ли предмет оружием."""
        return self.item_type == 1
    
    def is_armor(self) -> bool:
        """Проверяет, является ли предмет броней."""
        return self.item_type == 2
    
    def is_accessory(self) -> bool:
        """Проверяет, является ли предмет аксессуаром."""
        return self.item_type == 3
    
    def get_item_type_name(self) -> str:
        """Возвращает строковое представление типа предмета."""
        type_names = {
            0: "Расходуемый",
            1: "Оружие",
            2: "Броня",
            3: "Аксессуар"
        }
        return type_names.get(self.item_type, "Неизвестный тип")
    
    def get_rarity_name(self) -> str:
        """Возвращает строковое представление редкости предмета."""
        rarity_names = {
            0: "Обычный",
            1: "Необычный",
            2: "Редкий",
            3: "Эпический",
            4: "Легендарный"
        }
        return rarity_names.get(self.rarity, "Неизвестная редкость")
    
    def get_rarity_color(self) -> int:
        """Возвращает цвет редкости для отображения."""
        rarity_colors = {
            0: 7,  # Белый
            1: 2,  # Зеленый
            2: 4,  # Синий
            3: 5,  # Фиолетовый
            4: 40  # Оранжевый
        }
        return rarity_colors.get(self.rarity, 7)
    
    def get_brief_display_template(self) -> tuple:
        """
        Возвращает шаблон для краткого отображения предмета (в бою/луте).
        
        :return: Кортеж (шаблон, список элементов)
        """
        template = "%1 %2 (Ур.%3)"
        elements = [
            (self.name, self.get_rarity_color()),
            (" (", 0),
            (str(self.level), 3),
            (")", 0)
        ]
        return template, elements
    
    def get_detailed_display_template(self) -> tuple:
        """
        Возвращает шаблон для детального отображения предмета (в инвентаре).
        
        :return: Кортеж (шаблон, список элементов)
        """
        template = "%1 %2 (Ур.%3, %4)"
        elements = [
            (self.name, self.get_rarity_color()),
            (" (", 0),
            (str(self.level), 3),
            (", ", 0),
            (self.get_rarity_name(), self.get_rarity_color()),
            (", ", 0),
            (self.get_item_type_name(), 6),
            (")", 0)
        ]
        return template, elements
    
    @abstractmethod
    def use(self, user: Any) -> bool:
        """
        Абстрактный метод использования предмета.
        Должен быть реализован в подклассах.
        
        :param user: Объект персонажа, использующего предмет
        :return: True если использование успешно, False если нет
        """
        pass
    
    def can_equip(self, character: Any) -> bool:
        """
        Проверяет, может ли персонаж надеть этот предмет.
        По умолчанию - да, но может быть переопределен в подклассах.
        
        :param character: Объект персонажа
        :return: True если можно надеть, False если нет
        """
        # Проверка уровня персонажа
        if hasattr(character, 'level') and character.level < self.level:
            return False
        return True
    
    def equip(self, character: Any) -> bool:
        """
        Надевает предмет на персонажа.
        По умолчанию возвращает False, так как не все предметы можно надеть.
        
        :param character: Объект персонажа
        :return: True если успешно надет, False если нет
        """
        return False
    
    def unequip(self, character: Any) -> bool:
        """
        Снимает предмет с персонажа.
        По умолчанию возвращает False, так как не все предметы можно снять.
        
        :param character: Объект персонажа
        :return: True если успешно снят, False если нет
        """
        return False
    
    def __str__(self) -> str:
        """Возвращает строковое представление предмета."""
        return f"{self.name} (Ур.{self.level}, {self.get_rarity_name()}, {self.get_item_type_name()})"
    
    def __repr__(self) -> str:
        """Возвращает формальное строковое представление предмета."""
        return f"BaseItem(name='{self.name}', type={self.item_type}, level={self.level}, rarity={self.rarity}, properties={self.properties})"
    
    def __eq__(self, other) -> bool:
        """Проверяет равенство двух предметов."""
        if not isinstance(other, BaseItem):
            return False
        return (self.name == other.name and 
                self.item_type == other.item_type and 
                self.level == other.level and
                self.rarity == other.rarity and
                self.properties == other.properties)
    
    def __hash__(self) -> int:
        """Хэш для использования предмета как ключа в словаре."""
        return hash((self.name, self.item_type, self.level, self.rarity, tuple(sorted(self.properties.items()))))