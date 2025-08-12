# monster_classes.py - Классы монстров

from typing import Dict, Any
from Characters.character import Character  # Импортируем базовый класс


class Monster(Character):
    """Базовый класс для монстров."""
    
    BASE_STATS: Dict[str, int] = {}
    GROWTH_RATES: Dict[str, float] = {}
    
    def __init__(self, name: str, role: str, level: int = 1) -> None:
        super().__init__(name=name, role=role, level=level, is_player=False, can_heal=False)
        # Монстры не имеют системы опыта, но имеют уровень
        # Все остальные характеристики наследуются от Character


class Goblin(Monster):
    """Класс Гоблина - слабый враг."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 8,   # Телосложение
        'strength': 6,      # Сила
        'dexterity': 8,     # Ловкость
        'intelligence': 4   # Интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.05,
        'strength': 0.04,
        'dexterity': 0.04,
        'intelligence': 0.03,
        'attack': 0.08,     # +8% атаки за уровень
        'defense': 0.05,    # +5% защиты за уровень
        'hp': 0.10          # +10% HP за уровень
    }
    
    def __init__(self, name: str = "Гоблин", level: int = 1) -> None:
        super().__init__(
            name=name,
            role="goblin",
            level=level
        )


class Orc(Monster):
    """Класс Орка - сильный враг с высоким уроном."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 14,  # Телосложение
        'strength': 16,     # Сила
        'dexterity': 6,     # Ловкость
        'intelligence': 5   # Интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.09,
        'strength': 0.10,
        'dexterity': 0.03,
        'intelligence': 0.02,
        'attack': 0.10,     # +10% атаки за уровень
        'defense': 0.09,    # +9% защиты за уровень
        'hp': 0.13          # +13% HP за уровень
    }
    
    def __init__(self, name: str = "Орк", level: int = 1) -> None:
        super().__init__(
            name=name,
            role="orc",
            level=level
        )


class Skeleton(Monster):
    """Класс Скелета - средний враг."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 10,  # Телосложение
        'strength': 12,     # Сила
        'dexterity': 10,    # Ловкость
        'intelligence': 6   # Интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.07,
        'strength': 0.08,
        'dexterity': 0.05,
        'intelligence': 0.04,
        'attack': 0.09,     # +9% атаки за уровень
        'defense': 0.07,    # +7% защиты за уровень
        'hp': 0.11          # +11% HP за уровень
    }
    
    def __init__(self, name: str = "Скелет", level: int = 1) -> None:
        super().__init__(
            name=name,
            role="skeleton",
            level=level
        )


class Wizard(Monster):
    """Класс Волшебника - магический враг с высоким уроном."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 9,   # Телосложение
        'strength': 8,      # Сила
        'dexterity': 12,    # Ловкость
        'intelligence': 18  # Интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.06,
        'strength': 0.05,
        'dexterity': 0.07,
        'intelligence': 0.10,
        'attack': 0.12,     # +12% атаки за уровень
        'defense': 0.05,    # +5% защиты за уровень
        'hp': 0.09          # +9% HP за уровень
    }
    
    def __init__(self, name: str = "Волшебник", level: int = 1) -> None:
        super().__init__(
            name=name,
            role="wizard",
            level=level
        )


class Troll(Monster):
    """Класс Тролля - очень крепкий враг."""
    
    BASE_STATS: Dict[str, int] = {
        'constitution': 18,  # Телосложение
        'strength': 17,     # Сила
        'dexterity': 4,     # Ловкость
        'intelligence': 3   # Интеллект
    }
    
    GROWTH_RATES: Dict[str, float] = {
        'constitution': 0.11,
        'strength': 0.09,
        'dexterity': 0.02,
        'intelligence': 0.01,
        'attack': 0.09,     # +9% атаки за уровень
        'defense': 0.11,    # +11% защиты за уровень
        'hp': 0.15          # +15% HP за уровень
    }
    
    def __init__(self, name: str = "Тролль", level: int = 1) -> None:
        super().__init__(
            name=name,
            role="troll",
            level=level
        )