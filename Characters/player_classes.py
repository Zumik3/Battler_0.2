from Characters.base_class import Character
from Characters.Equipment.equipment import EquipmentMixin, EquipmentSlot
from Config.game_config import (
    SLOT_TYPE_WEAPON, SLOT_TYPE_ARMOR, SLOT_TYPE_ACCESSORY,
    SLOT_NAME_WEAPON, SLOT_NAME_ARMOR, SLOT_NAME_ACCESSORY
)


class Player(Character, EquipmentMixin):
    """Базовый класс для всех игроков (персонажей, управляемых игроком)."""

    def __init__(self, name, role, class_icon, class_icon_color=None, level=1, can_heal=False):
        super().__init__(name=name, role=role, level=level, is_player=True, can_heal=can_heal)
        # Создаем слоты для экипировки
        self.class_icon = class_icon
        self.class_icon_color = class_icon_color

        self.equipment_slots = {
            SLOT_TYPE_WEAPON: EquipmentSlot(SLOT_NAME_WEAPON, SLOT_TYPE_WEAPON),
            SLOT_TYPE_ARMOR: EquipmentSlot(SLOT_NAME_ARMOR, SLOT_TYPE_ARMOR),
            SLOT_TYPE_ACCESSORY: EquipmentSlot(SLOT_NAME_ACCESSORY, SLOT_TYPE_ACCESSORY)
        }


class Tank(Player):
    """Класс Танка - высокая защита, умеренный урон, низкая ловкость."""
    
    BASE_STATS = {
        'constitution': 15,  # Высокое телосложение
        'strength': 14,      # Высокая сила
        'dexterity': 5,
        'intelligence': 6    # Низкий интеллект
    }
    
    GROWTH_RATES = {
        'constitution': 0.10,  # +10% телосложения за уровень
        'strength': 0.09,      # +9% силы за уровень
        'attack': 0.08,        # +8% атаки за уровень
        'defense': 0.12,       # +12% защиты за уровень
        'dexterity': 0.03,     # +3% ловкости за уровень
        'intelligence': 0.02   # +2% интеллекта за уровень
    }
    
    class_icon = "T"
    class_icon_color = 1  # Красный цвет для танка
    
    def __init__(self, name, level=1):
        super().__init__(name=name, role="tank", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)


class Warrior(Player):
    """Класс Воина - сбалансированные характеристики."""
    
    BASE_STATS = {
        'constitution': 12,  # Среднее телосложение
        'strength': 16,      # Высокая сила
        'dexterity': 10,
        'intelligence': 8    # Низкий интеллект
    }
    
    GROWTH_RATES = {
        'constitution': 0.09,  # +9% телосложения за уровень
        'strength': 0.10,      # +10% силы за уровень
        'attack': 0.10,        # +10% атаки за уровень
        'defense': 0.08,       # +8% защиты за уровень
        'dexterity': 0.05,     # +5% ловкости за уровень
        'intelligence': 0.03   # +3% интеллекта за уровень
    }

    class_icon = "W"
    class_icon_color = 1  # Красный цвет для воина
    
    def __init__(self, name, level=1):
        super().__init__(name=name, role="warrior", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)


class Rogue(Player):
    """Класс Разбойника - высокая ловкость, умеренный урон, низкая защита."""
    
    BASE_STATS = {
        'constitution': 8,   # Низкое телосложение
        'strength': 6,       # Низкая сила
        'dexterity': 18,     # Высокая ловкость
        'intelligence': 10   # Средний интеллект
    }
    
    GROWTH_RATES = {
        'constitution': 0.07,  # +7% телосложения за уровень
        'strength': 0.05,      # +5% силы за уровень
        'attack': 0.12,        # +12% атаки за уровень
        'defense': 0.05,       # +5% защиты за уровень
        'dexterity': 0.08,     # +8% ловкости за уровень
        'intelligence': 0.06   # +6% интеллекта за уровень
    }
    
    class_icon = "R"
    class_icon_color = 8  # Серый цвет для разбойника
    
    def __init__(self, name, level=1):
        super().__init__(name=name, role="rogue", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)

        self.ability_manager.add_ability_by_name('Backstab')

        for name in self.ability_manager.active_abilities:
            self.ability_manager.level_up_ability(name)


class Archer(Player):
    """Класс Лучника - высокий урон, средняя ловкость, низкая защита."""
    
    BASE_STATS = {
        'constitution': 9,   # Низкое-среднее телосложение
        'strength': 8,       # Низкая сила
        'dexterity': 14,     # Высокая ловкость
        'intelligence': 10   # Средний интеллект
    }
    
    GROWTH_RATES = {
        'constitution': 0.08,  # +8% телосложения за уровень
        'strength': 0.06,      # +6% силы за уровень
        'attack': 0.11,        # +11% атаки за уровень
        'defense': 0.06,       # +6% защиты за уровень
        'dexterity': 0.07,     # +7% ловкости за уровень
        'intelligence': 0.05   # +5% интеллекта за уровень
    }
    
    class_icon = "A"
    class_icon_color = 6  # Циановый цвет для лучника
    
    def __init__(self, name, level=1):
        super().__init__(name=name, role="archer", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)
        # Добавляем способности
        self.ability_manager.add_ability_by_name('volley')


class Mage(Player):
    """Класс Мага - очень высокий урон, низкая защита и здоровье."""
    
    BASE_STATS = {
        'constitution': 7,   # Очень низкое телосложение
        'strength': 4,       # Очень низкая сила
        'dexterity': 12,
        'intelligence': 20   # Очень высокий интеллект
    }
    
    GROWTH_RATES = {
        'constitution': 0.06,  # +6% телосложения за уровень
        'strength': 0.03,      # +3% силы за уровень
        'attack': 0.13,        # +13% атаки за уровень
        'defense': 0.04,       # +4% защиты за уровень
        'dexterity': 0.06,     # +6% ловкости за уровень
        'intelligence': 0.12   # +12% интеллекта за уровень
    }
    
    class_icon = "M"
    class_icon_color = 5  # Магента цвет для мага
    
    def __init__(self, name, level=1):
        super().__init__(name=name, role="mage", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)


class Healer(Player):
    """Класс Лекаря - низкий урон, средние защита и здоровье, способность лечить."""
    
    BASE_STATS = {
        'constitution': 10,  # Среднее телосложение
        'strength': 5,       # Низкая сила
        'dexterity': 12,
        'intelligence': 16   # Высокий интеллект
    }
    
    GROWTH_RATES = {
        'constitution': 0.08,  # +8% телосложения за уровень
        'strength': 0.04,      # +4% силы за уровень
        'attack': 0.07,        # +7% атаки за уровень
        'defense': 0.07,       # +7% защиты за уровень
        'dexterity': 0.08,     # +8% ловкости за уровень
        'intelligence': 0.09   # +9% интеллекта за уровень
    }
    
    class_icon = "H"
    class_icon_color = 6  # Циан цвет для хилера
    
    def __init__(self, name, level=1):
        super().__init__(name=name, role="healer", level=level, can_heal=True, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)
        
        # Добавляем способности лечения
        self.ability_manager.add_ability_by_name('heal')
        self.ability_manager.add_ability_by_name('mass_heal')

        for name in self.ability_manager.active_abilities:
            self.ability_manager.level_up_ability(name)