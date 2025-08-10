# monster_classes.py - Классы монстров

from Characters.base_class import Character  # Импортируем базовый класс

class Goblin(Character):
    """Класс Гоблина - слабый враг."""
    
    BASE_STATS = {
        'hp': 40,
        'attack': 12,
        'defense': 2,
        'dexterity': 8,
        'constitution': 8,   # Добавляем недостающие характеристики
        'strength': 6,
        'intelligence': 4
    }
    
    GROWTH_RATES = {
        'hp': 0.10,          # +10% HP за уровень
        'attack': 0.08,      # +8% атаки за уровень
        'defense': 0.05,     # +5% защиты за уровень
        'dexterity': 0.04,   # +4% ловкости за уровень
        'constitution': 0.05,
        'strength': 0.04,
        'intelligence': 0.03
    }
    
    def __init__(self, name, level=1):
        scaled_stats = Character.scale_stats(self.BASE_STATS, level, self.GROWTH_RATES)
        
        # У врагов нет системы опыта, поэтому устанавливаем exp в 0
        # и не будем его использовать
        super().__init__(
            name=name,
            role="goblin",
            level=level,
            **scaled_stats
        )
        # У врагов нет системы опыта
        delattr(self, 'exp_to_next_level')

class Orc(Character):
    """Класс Орка - сильный враг с высоким уроном."""
    
    BASE_STATS = {
        'hp': 90,
        'attack': 20,
        'defense': 8,
        'dexterity': 6,
        'constitution': 14,
        'strength': 16,
        'intelligence': 5
    }
    
    GROWTH_RATES = {
        'hp': 0.13,          # +13% HP за уровень
        'attack': 0.10,      # +10% атаки за уровень
        'defense': 0.09,     # +9% защиты за уровень
        'dexterity': 0.03,   # +3% ловкости за уровень
        'constitution': 0.09,
        'strength': 0.10,
        'intelligence': 0.02
    }
    
    def __init__(self, name, level=1):
        scaled_stats = Character.scale_stats(self.BASE_STATS, level, self.GROWTH_RATES)
        
        super().__init__(
            name=name,
            role="orc",
            level=level,
            **scaled_stats
        )
        delattr(self, 'exp_to_next_level')

class Skeleton(Character):
    """Класс Скелета - средний враг."""
    
    BASE_STATS = {
        'hp': 60,
        'attack': 15,
        'defense': 4,
        'dexterity': 10,
        'constitution': 10,
        'strength': 12,
        'intelligence': 6
    }
    
    GROWTH_RATES = {
        'hp': 0.11,          # +11% HP за уровень
        'attack': 0.09,      # +9% атаки за уровень
        'defense': 0.07,     # +7% защиты за уровень
        'dexterity': 0.05,   # +5% ловкости за уровень
        'constitution': 0.07,
        'strength': 0.08,
        'intelligence': 0.04
    }
    
    def __init__(self, name, level=1):
        scaled_stats = Character.scale_stats(self.BASE_STATS, level, self.GROWTH_RATES)
        
        super().__init__(
            name=name,
            role="skeleton",
            level=level,
            **scaled_stats
        )
        delattr(self, 'exp_to_next_level')

class Wizard(Character):
    """Класс Волшебника - магический враг с высоким уроном."""
    
    BASE_STATS = {
        'hp': 55,
        'attack': 25,
        'defense': 3,
        'dexterity': 12,
        'constitution': 9,
        'strength': 8,
        'intelligence': 18
    }
    
    GROWTH_RATES = {
        'hp': 0.09,          # +9% HP за уровень
        'attack': 0.12,      # +12% атаки за уровень
        'defense': 0.05,     # +5% защиты за уровень
        'dexterity': 0.07,   # +7% ловкости за уровень
        'constitution': 0.06,
        'strength': 0.05,
        'intelligence': 0.10
    }
    
    def __init__(self, name, level=1):
        scaled_stats = Character.scale_stats(self.BASE_STATS, level, self.GROWTH_RATES)
        
        super().__init__(
            name=name,
            role="wizard",
            level=level,
            **scaled_stats
        )
        delattr(self, 'exp_to_next_level')

class Troll(Character):
    """Класс Тролля - очень крепкий враг."""
    
    BASE_STATS = {
        'hp': 120,
        'attack': 18,
        'defense': 12,
        'dexterity': 4,
        'constitution': 18,
        'strength': 17,
        'intelligence': 3
    }
    
    GROWTH_RATES = {
        'hp': 0.15,          # +15% HP за уровень
        'attack': 0.09,      # +9% атаки за уровень
        'defense': 0.11,     # +11% защиты за уровень
        'dexterity': 0.02,   # +2% ловкости за уровень
        'constitution': 0.11,
        'strength': 0.09,
        'intelligence': 0.01
    }
    
    def __init__(self, name, level=1):
        scaled_stats = Character.scale_stats(self.BASE_STATS, level, self.GROWTH_RATES)
        
        super().__init__(
            name=name,
            role="troll",
            level=level,
            **scaled_stats
        )
        delattr(self, 'exp_to_next_level')