# player.py
from typing import Dict, Any, List, Tuple, Optional, Union
from Characters.character import Character
from Characters.Equipment.equipment import EquipmentMixin, EquipmentSlot
from Battle.battle_logger import battle_logger
from Config.game_config import (
    SLOT_TYPE_WEAPON, SLOT_TYPE_ARMOR, SLOT_TYPE_ACCESSORY,
    SLOT_NAME_WEAPON, SLOT_NAME_ARMOR, SLOT_NAME_ACCESSORY
)


class Player(Character, EquipmentMixin):
    """Базовый класс для всех игроков (персонажей, управляемых игроком)."""

    BASE_STATS: Dict[str, int] = {}
    GROWTH_RATES: Dict[str, float] = {}
    
    def __init__(self, name: str, role: str, class_icon: str, class_icon_color: Optional[int] = None, 
                 level: int = 1, can_heal: bool = False) -> None:
        super().__init__(name=name, role=role, level=level, is_player=True, can_heal=can_heal)
        # Создаем слоты для экипировки
        self.class_icon: str = class_icon
        self.class_icon_color: Optional[int] = class_icon_color

        self.equipment_slots: Dict[str, EquipmentSlot] = {
            SLOT_TYPE_WEAPON: EquipmentSlot(SLOT_NAME_WEAPON, SLOT_TYPE_WEAPON),
            SLOT_TYPE_ARMOR: EquipmentSlot(SLOT_NAME_ARMOR, SLOT_TYPE_ARMOR),
            SLOT_TYPE_ACCESSORY: EquipmentSlot(SLOT_NAME_ACCESSORY, SLOT_TYPE_ACCESSORY)
        }
        
        # Система опыта и уровней
        self.exp: int = 0
        self.exp_to_next_level: int = 0
        self.calculate_exp_for_next_level()
    
    def calculate_exp_for_next_level(self) -> None:
        """Рассчитывает количество опыта, необходимого для следующего уровня."""
        self.exp_to_next_level = int(20 * (self.level ** 1.5))
        
    def add_exp(self, exp_amount: int) -> List[str]:
        """Добавляет опыт персонажу и проверяет на повышение уровня."""
            
        self.exp += exp_amount
        level_up_messages: List[str] = []
        
        # Проверяем, достаточно ли опыта для повышения уровня
        while self.exp >= self.exp_to_next_level:
            level_up_message: str = self.level_up()
            level_up_messages.append(level_up_message)
            
        return level_up_messages
        
    def level_up(self) -> str:
        """Повышает уровень персонажа и улучшает его характеристики."""
        old_level: int = self.level
        old_dexterity: int = self.stats.dexterity
        old_constitution: int = self.stats.constitution
        old_strength: int = self.stats.strength
        old_intelligence: int = self.stats.intelligence
        
        self.level += 1
        # Отбираем опыт, который потратили на повышение уровня
        self.exp -= self.exp_to_next_level
        
        if hasattr(self, 'BASE_STATS') and hasattr(self, 'GROWTH_RATES'):
            scaled_stats: Dict[str, int] = Character.scale_stats(self.BASE_STATS, self.level, self.GROWTH_RATES)
            # Обновляем характеристики через объект stats
            self.stats.update_from_scaled_stats(scaled_stats)
        
        # Пересчитываем производные атрибуты через derived_stats
        self.derived_stats.update_level(self)
        
        # Полное восстановление HP и энергии при повышении уровня
        self.hp = self.derived_stats.max_hp
        self.energy = self.derived_stats.max_energy
        
        # Пересчитываем опыт для следующего уровня
        self.calculate_exp_for_next_level()
        
        # Создаем цветное сообщение о повышении уровня
        # Формируем элементы сообщения
        elements: List[Tuple[str, int]] = [
            (self.name, 2),           # зеленый цвет для имени
            (" получает уровень ", 0),
            (str(old_level), 3),      # желтый цвет для старого уровня
            (" ➤ ", 0),
            (str(self.level), 3),     # желтый цвет для нового уровня
            (". (", 0)
        ]
        
        # Добавляем ТОЛЬКО основные измененные характеристики
        stats_changed: List[Tuple[str, int]] = []
        if self.stats.dexterity != old_dexterity:
            stats_changed.append((f"dex:{old_dexterity} ➤ {self.stats.dexterity}", 6))
        if self.stats.constitution != old_constitution:
            stats_changed.append((f"con:{old_constitution} ➤ {self.stats.constitution}", 6))
        if self.stats.strength != old_strength:
            stats_changed.append((f"str:{old_strength} ➤ {self.stats.strength}", 6))
        if self.stats.intelligence != old_intelligence:
            stats_changed.append((f"int:{old_intelligence} ➤ {self.stats.intelligence}", 6))
        
        # Добавляем характеристики в сообщение
        for i, (stat_text, color) in enumerate(stats_changed):
            # Разбиваем текст характеристики на части для цветного отображения
            if ' ➤ ' in stat_text:
                parts = stat_text.split(' ➤ ')
                if ':' in parts[0]:
                    stat_name, old_val = parts[0].split(':')
                    new_val = parts[1]
                    # stat_name - бирюзовый, old_val и new_val - желтые
                    elements.extend([
                        (stat_name + ":", 6),  # бирюзовый
                        (old_val, 3),          # желтый
                        (" ➤ ", 0),
                        (new_val, 3)           # желтый
                    ])
                else:
                    elements.append((stat_text, 6))  # бирюзовый
            else:
                elements.append((stat_text, 6))  # бирюзовый
                
            if i < len(stats_changed) - 1:
                elements.append((", ", 0))
        
        elements.append((")", 0))
        
        # Создаем шаблон для всех элементов
        template: str = "".join([f"%{i+1}" for i in range(len(elements))])
        message: str = battle_logger.create_log_message(template, elements)
        
        return message
        
    def get_exp_progress(self) -> int:
        """Возвращает прогресс до следующего уровня в процентах."""
        if self.exp_to_next_level <= 0:
            return 100
        return int((self.exp / self.exp_to_next_level) * 100)

    def get_level_info(self) -> Dict[str, Union[int, float]]:
        """Возвращает информацию о текущем уровне и опыте."""
        return {
            'level': self.level,
            'current_exp': self.exp,
            'exp_to_next': self.exp_to_next_level,
            'exp_progress': self.get_exp_progress()
        }


class Tank(Player):
    """Класс Танка - высокая защита, умеренный урон, низкая ловкость."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 15,  # Высокое телосложение
        'strength': 14,      # Высокая сила
        'dexterity': 5,
        'intelligence': 6    # Низкий интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.10,  # +10% телосложения за уровень
        'strength': 0.09,      # +9% силы за уровень
        'attack': 0.08,        # +8% атаки за уровень
        'defense': 0.12,       # +12% защиты за уровень
        'dexterity': 0.03,     # +3% ловкости за уровень
        'intelligence': 0.02   # +2% интеллекта за уровень
    }
    
    class_icon: str = "T"
    class_icon_color: int = 1  # Красный цвет для танка
    
    def __init__(self, name: str, level: int = 1) -> None:
        super().__init__(name=name, role="tank", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)


class Warrior(Player):
    """Класс Воина - сбалансированные характеристики."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 12,  # Среднее телосложение
        'strength': 16,      # Высокая сила
        'dexterity': 10,
        'intelligence': 8    # Низкий интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.09,  # +9% телосложения за уровень
        'strength': 0.10,      # +10% силы за уровень
        'attack': 0.10,        # +10% атаки за уровень
        'defense': 0.08,       # +8% защиты за уровень
        'dexterity': 0.05,     # +5% ловкости за уровень
        'intelligence': 0.03   # +3% интеллекта за уровень
    }

    class_icon: str = "W"
    class_icon_color: int = 1  # Красный цвет для воина
    
    def __init__(self, name: str, level: int = 1) -> None:
        super().__init__(name=name, role="warrior", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)


class Rogue(Player):
    """Класс Разбойника - высокая ловкость, умеренный урон, низкая защита."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 7,   # Низкое телосложение
        'strength': 6,       # Низкая сила
        'dexterity': 18,     # Высокая ловкость
        'intelligence': 10   # Средний интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.07,  # +7% телосложения за уровень
        'strength': 0.05,      # +5% силы за уровень
        'attack': 0.12,        # +12% атаки за уровень
        'defense': 0.05,       # +5% защиты за уровень
        'dexterity': 0.08,     # +8% ловкости за уровень
        'intelligence': 0.06   # +6% интеллекта за уровень
    }
    
    class_icon: str = "R"
    class_icon_color: int = 8  # Серый цвет для разбойника
    
    def __init__(self, name: str, level: int = 1) -> None:
        super().__init__(name=name, role="rogue", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)

        self.ability_manager.add_ability_by_name('Backstab')
        self.ability_manager.add_ability_by_name('SlidingStrike')
        self.ability_manager.add_ability_by_name('CriticalStrike')
        self.ability_manager.add_ability_by_name('PoisonStrike')

        for name in self.ability_manager.active_abilities:
            self.ability_manager.level_up_ability(name)

        for name in self.ability_manager.passive_abilities:
            self.ability_manager.set_ability_level(name, 5)


class Archer(Player):
    """Класс Лучника - высокий урон, средняя ловкость, низкая защита."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 9,   # Низкое-среднее телосложение
        'strength': 8,       # Низкая сила
        'dexterity': 14,     # Высокая ловкость
        'intelligence': 10   # Средний интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.08,  # +8% телосложения за уровень
        'strength': 0.06,      # +6% силы за уровень
        'attack': 0.11,        # +11% атаки за уровень
        'defense': 0.06,       # +6% защиты за уровень
        'dexterity': 0.07,     # +7% ловкости за уровень
        'intelligence': 0.05   # +5% интеллекта за уровень
    }
    
    class_icon: str = "A"
    class_icon_color: int = 6  # Циановый цвет для лучника
    
    def __init__(self, name: str, level: int = 1) -> None:
        super().__init__(name=name, role="archer", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)
        # Добавляем способности
        self.ability_manager.add_ability_by_name('Volley')


class Mage(Player):
    """Класс Мага - очень высокий урон, низкая защита и здоровье."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 6,   # Очень низкое телосложение
        'strength': 4,       # Очень низкая сила
        'dexterity': 12,
        'intelligence': 20   # Очень высокий интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.06,  # +6% телосложения за уровень
        'strength': 0.03,      # +3% силы за уровень
        'attack': 0.13,        # +13% атаки за уровень
        'defense': 0.04,       # +4% защиты за уровень
        'dexterity': 0.06,     # +6% ловкости за уровень
        'intelligence': 0.12   # +12% интеллекта за уровень
    }
    
    class_icon: str = "M"
    class_icon_color: int = 5  # Магента цвет для мага
    
    def __init__(self, name: str, level: int = 1) -> None:
        super().__init__(name=name, role="mage", level=level, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)

        self.ability_manager.add_ability_by_name('Fireball')

        for name in self.ability_manager.active_abilities:
            self.ability_manager.level_up_ability(name)


class Healer(Player):
    """Класс Лекаря - низкий урон, средние защита и здоровье, способность лечить."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 10,  # Среднее телосложение
        'strength': 5,       # Низкая сила
        'dexterity': 12,
        'intelligence': 16   # Высокий интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.08,  # +8% телосложения за уровень
        'strength': 0.04,      # +4% силы за уровень
        'attack': 0.07,        # +7% атаки за уровень
        'defense': 0.07,       # +7% защиты за уровень
        'dexterity': 0.08,     # +8% ловкости за уровень
        'intelligence': 0.09   # +9% интеллекта за уровень
    }
    
    class_icon: str = "H"
    class_icon_color: int = 6  # Циан цвет для хилера
    
    def __init__(self, name: str, level: int = 1) -> None:
        super().__init__(name=name, role="healer", level=level, can_heal=True, 
                        class_icon=self.class_icon, class_icon_color=self.class_icon_color)
        
        # Добавляем способности лечения
        self.ability_manager.add_ability_by_name('Heal')
        self.ability_manager.add_ability_by_name('MassHeal')

        for name in self.ability_manager.active_abilities:
            self.ability_manager.level_up_ability(name)