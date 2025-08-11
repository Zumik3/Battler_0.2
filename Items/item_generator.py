# item_generator.py - Генератор предметов

import random
from typing import List, Dict, Any, Optional
from Items.base_item import BaseItem

class ConsumableItem(BaseItem):
    """Класс для расходуемых предметов (зелья, свитки и т.д.)"""
    
    def __init__(self, name: str, level: int = 1, rarity: int = 0, properties: Dict[str, Any] = None):
        super().__init__(name, BaseItem.CONSUMABLE, level, rarity, properties)
    
    def use(self, user: Any) -> bool:
        """
        Использует расходуемый предмет.
        
        :param user: Объект персонажа, использующего предмет
        :return: True если использование успешно
        """
        # Пример реализации - восстановление HP
        heal_amount = self.get_property('heal_amount', 0)
        if heal_amount > 0 and hasattr(user, 'hp') and hasattr(user, 'derived_stats'):
            old_hp = user.hp
            user.hp = min(user.derived_stats.max_hp, user.hp + heal_amount)
            actual_heal = user.hp - old_hp
            print(f"{user.name} восстановил {actual_heal} HP используя {self.name}")
            return True
        return False

class WeaponItem(BaseItem):
    """Класс для оружия"""
    
    def __init__(self, name: str, level: int = 1, rarity: int = 0, properties: Dict[str, Any] = None):
        super().__init__(name, BaseItem.WEAPON, level, rarity, properties)
    
    def use(self, user: Any) -> bool:
        """
        Оружие нельзя использовать как расходуемый предмет.
        """
        print(f"{self.name} - это оружие, его нужно надеть, а не использовать.")
        return False
    
    def equip(self, character: Any) -> bool:
        """
        Надевает оружие на персонажа.
        """
        if not self.can_equip(character):
            return False
        
        if hasattr(character, 'equipped_weapon'):
            character.equipped_weapon = self
            print(f"{character.name} экипировал {self.name}")
            return True
        return False
    
    def unequip(self, character: Any) -> bool:
        """
        Снимает оружие с персонажа.
        """
        if hasattr(character, 'equipped_weapon') and character.equipped_weapon == self:
            character.equipped_weapon = None
            print(f"{character.name} снял {self.name}")
            return True
        return False

class ArmorItem(BaseItem):
    """Класс для брони"""
    
    def __init__(self, name: str, level: int = 1, rarity: int = 0, properties: Dict[str, Any] = None):
        super().__init__(name, BaseItem.ARMOR, level, rarity, properties)
    
    def use(self, user: Any) -> bool:
        """
        Броню нельзя использовать как расходуемый предмет.
        """
        print(f"{self.name} - это броня, ее нужно надеть, а не использовать.")
        return False
    
    def equip(self, character: Any) -> bool:
        """
        Надевает броню на персонажа.
        """
        if not self.can_equip(character):
            return False
        
        if hasattr(character, 'equipped_armor'):
            character.equipped_armor = self
            print(f"{character.name} надел {self.name}")
            return True
        return False
    
    def unequip(self, character: Any) -> bool:
        """
        Снимает броню с персонажа.
        """
        if hasattr(character, 'equipped_armor') and character.equipped_armor == self:
            character.equipped_armor = None
            print(f"{character.name} снял {self.name}")
            return True
        return False

class AccessoryItem(BaseItem):
    """Класс для аксессуаров"""
    
    def __init__(self, name: str, level: int = 1, rarity: int = 0, properties: Dict[str, Any] = None):
        super().__init__(name, BaseItem.ACCESSORY, level, rarity, properties)
    
    def use(self, user: Any) -> bool:
        """
        Аксессуар нельзя использовать как расходуемый предмет.
        """
        print(f"{self.name} - это аксессуар, его нужно надеть, а не использовать.")
        return False
    
    def equip(self, character: Any) -> bool:
        """
        Надевает аксессуар на персонажа.
        """
        if not self.can_equip(character):
            return False
        
        if hasattr(character, 'equipped_accessory'):
            character.equipped_accessory = self
            print(f"{character.name} надел {self.name}")
            return True
        return False
    
    def unequip(self, character: Any) -> bool:
        """
        Снимает аксессуар с персонажа.
        """
        if hasattr(character, 'equipped_accessory') and character.equipped_accessory == self:
            character.equipped_accessory = None
            print(f"{character.name} снял {self.name}")
            return True
        return False

class ItemGenerator:
    """Генератор случайных предметов"""
    
    # Базовые названия для разных типов предметов
    WEAPON_NAMES = [
        "Меч", "Топор", "Кинжал", "Посох", "Лук", "Арбалет", 
        "Булава", "Копье", "Коса", "Цеп", "Когти", "Кинжалы"
    ]
    
    ARMOR_NAMES = [
        "Доспех", "Кольчуга", "Роба", "Плащ", "Щит", "Шлем",
        "Перчатки", "Сапоги", "Нагрудник", "Поножи", "Наручи"
    ]
    
    CONSUMABLE_NAMES = [
        "Зелье", "Свиток", "Эликсир", "Настойка", "Отвар",
        "Микстура", "Тоник", "Бальзам"
    ]
    
    ACCESSORY_NAMES = [
        "Кольцо", "Амулет", "Ожерелье", "Браслет", "Печатка",
        "Медальон", "Кулон", "Подвеска"
    ]
    
    # Модификаторы для редких предметов
    RARE_MODIFIERS = [
        "Сверкающий", "Могущественный", "Легендарный", "Древний",
        "Божественный", "Великий", "Вечный", "Священный"
    ]
    
    # Базовые характеристики персонажа
    CHARACTER_STATS = [
        'strength_bonus',      # Бонус силы
        'dexterity_bonus',     # Бонус ловкости
        'intelligence_bonus',  # Бонус интеллекта
        'constitution_bonus',   # Бонус телосложения
        'crit_chance_bonus',   # Бонус шанса критического удара
        'dodge_chance_bonus'   # Бонус шанса уклонения
    ]
    
    # Базовые значения бонусов (будут масштабироваться по уровню)
    BASE_STAT_VALUES = {
        'strength_bonus': 1,
        'dexterity_bonus': 1,
        'intelligence_bonus': 1,
        'constitution_bonus': 1,
        'crit_chance_bonus': 1,
        'dodge_chance_bonus': 1
    }
    
    # Свойства расходуемых предметов (базовые значения)
    BASE_CONSUMABLE_VALUES = {
        'heal_amount': 20,
        'temp_strength': 1,
        'temp_dexterity': 1,
        'temp_intelligence': 1,
        'temp_constitution': 1
    }
    
    # Количество свойств по редкости
    PROPERTIES_COUNT_BY_RARITY = {
        0: 1,  # Обычный - 1 свойство
        1: 1,  # Необычный - 1 свойство
        2: 2,  # Редкий - 2 свойства
        3: 3,  # Эпический - 3 свойства
        4: 4   # Легендарный - 4 свойства
    }
    
    @staticmethod
    def generate_random_item(item_type: Optional[int] = None, 
                           min_level: int = 1, 
                           max_level: int = 10,
                           rarity_weights: Optional[List[float]] = None) -> BaseItem:
        """
        Генерирует случайный предмет.
        
        :param item_type: Тип предмета (0-3), если None - случайный тип
        :param min_level: Минимальный уровень предмета
        :param max_level: Максимальный уровень предмета
        :param rarity_weights: Веса редкости [обычный, необычный, редкий, эпический, легендарный]
        :return: Сгенерированный предмет
        """
        # Если тип не указан, выбираем случайный
        if item_type is None:
            item_type = random.choice([BaseItem.CONSUMABLE, BaseItem.WEAPON, BaseItem.ARMOR, BaseItem.ACCESSORY])
        
        # Генерируем уровень
        level = random.randint(min_level, max_level)
        
        # Генерируем редкость
        if rarity_weights is None:
            # По умолчанию: обычные чаще, легендарные реже
            rarity_weights = [0.5, 0.3, 0.15, 0.04, 0.01]
        
        rarity = random.choices([0, 1, 2, 3, 4], weights=rarity_weights)[0]
        
        # Генерируем имя
        name = ItemGenerator._generate_item_name(item_type, rarity)
        
        # Генерируем свойства
        properties = ItemGenerator._generate_item_properties(item_type, rarity, level)
        
        # Создаем предмет в зависимости от типа
        if item_type == BaseItem.CONSUMABLE:
            return ConsumableItem(name, level, rarity, properties)
        elif item_type == BaseItem.WEAPON:
            return WeaponItem(name, level, rarity, properties)
        elif item_type == BaseItem.ARMOR:
            return ArmorItem(name, level, rarity, properties)
        elif item_type == BaseItem.ACCESSORY:
            return AccessoryItem(name, level, rarity, properties)
        
        # На случай ошибки
        return BaseItem(name, item_type, level, rarity, properties)
    
    @staticmethod
    def _generate_item_name(item_type: int, rarity: int) -> str:
        """Генерирует имя предмета."""
        # Выбираем базовое имя по типу
        if item_type == BaseItem.WEAPON:
            base_name = random.choice(ItemGenerator.WEAPON_NAMES)
        elif item_type == BaseItem.ARMOR:
            base_name = random.choice(ItemGenerator.ARMOR_NAMES)
        elif item_type == BaseItem.CONSUMABLE:
            base_name = random.choice(ItemGenerator.CONSUMABLE_NAMES)
        elif item_type == BaseItem.ACCESSORY:
            base_name = random.choice(ItemGenerator.ACCESSORY_NAMES)
        else:
            base_name = "Предмет"
        
        # Для редких предметов добавляем модификатор
        if rarity >= 2:  # Редкий и выше
            modifier = random.choice(ItemGenerator.RARE_MODIFIERS)
            return f"{modifier} {base_name}"
        elif rarity == 1:  # Необычный
            prefixes = ["Улучшенный", "Крепкий", "Прочный"]
            prefix = random.choice(prefixes)
            return f"{prefix} {base_name}"
        
        return base_name
    
    @staticmethod
    def _calculate_stat_value(base_value: int, level: int, rarity: int) -> int:
        """
        Рассчитывает значение характеристики на основе уровня и редкости.
        
        :param base_value: Базовое значение характеристики
        :param level: Уровень предмета
        :param rarity: Редкость предмета
        :return: Рассчитанное значение характеристики
        """
        # Базовое значение увеличивается с уровнем
        level_multiplier = 1 + (level - 1) * 0.2  # Каждый уровень добавляет 20%
        
        # Редкость увеличивает значение
        rarity_multiplier = 1 + rarity * 0.25  # Каждая ступень редкости добавляет 25%
        
        # Рассчитываем финальное значение
        final_value = base_value * level_multiplier * rarity_multiplier
        
        # Округляем до целого числа, минимум 1
        return max(1, int(final_value))
    
    @staticmethod
    def _generate_item_properties(item_type: int, rarity: int, level: int) -> Dict[str, Any]:
        """Генерирует свойства предмета."""
        properties = {}
        
        # Определяем количество свойств для данного предмета
        num_properties = ItemGenerator.PROPERTIES_COUNT_BY_RARITY.get(rarity, 1)
        
        if item_type == BaseItem.CONSUMABLE:
            # Для расходуемых предметов все параметры влияют на эффект
            # Выбираем свойства для расходуемого предмета
            consumable_props = list(ItemGenerator.BASE_CONSUMABLE_VALUES.keys())
            
            # Выбираем нужное количество свойств
            if len(consumable_props) >= num_properties:
                selected_props = random.sample(consumable_props, num_properties)
            else:
                selected_props = consumable_props
            
            # Рассчитываем значения для каждого свойства
            for prop in selected_props:
                base_value = ItemGenerator.BASE_CONSUMABLE_VALUES[prop]
                # Для расходуемых предметов и уровень, и редкость влияют на эффект
                final_value = ItemGenerator._calculate_stat_value(base_value, level, rarity)
                properties[prop] = final_value
        else:
            # Для экипировки выбираем характеристики
            if len(ItemGenerator.CHARACTER_STATS) >= num_properties:
                selected_stats = random.sample(ItemGenerator.CHARACTER_STATS, num_properties)
            else:
                selected_stats = ItemGenerator.CHARACTER_STATS
            
            # Рассчитываем значения для каждой характеристики
            for stat in selected_stats:
                base_value = ItemGenerator.BASE_STAT_VALUES[stat]
                # Для экипировки уровень влияет на значение, редкость влияет на количество свойств
                final_value = ItemGenerator._calculate_stat_value(base_value, level, 1)  # Базовая редкость для значения
                properties[stat] = final_value
        
        return properties
    
    @staticmethod
    def generate_loot_pack(num_items: int = 3, 
                          min_level: int = 1, 
                          max_level: int = 10,
                          rarity_weights: Optional[List[float]] = None) -> List[BaseItem]:
        """
        Генерирует набор предметов (лут).
        
        :param num_items: Количество предметов в наборе
        :param min_level: Минимальный уровень предметов
        :param max_level: Максимальный уровень предметов
        :param rarity_weights: Веса редкости
        :return: Список сгенерированных предметов
        """
        items = []
        for _ in range(num_items):
            item = ItemGenerator.generate_random_item(
                min_level=min_level,
                max_level=max_level,
                rarity_weights=rarity_weights
            )
            items.append(item)
        return items