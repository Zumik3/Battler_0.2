# base_stats.py

class Stats:
    """Класс для управления базовыми характеристиками персонажа."""
    
    # Множители защиты по ролям
    DEFENSE_MULTIPLIERS = {
        "tank": 1.0,
        "warrior": 0.66,
        "healer": 0.6,
        "archer": 0.44,
        "rogue": 0.375,
        "mage": 0.285
    }
    
    # Множители атаки по ролям
    PRIMARY_STAT_MULTIPLIERS = {
        "tank": 0.8,      # Танки используют силу
        "warrior": 1.0,   # Воины используют силу
        "rogue": 1.2,     # Разбойники используют ловкость
        "archer": 1.1,    # Лучники используют ловкость
        "mage": 1.3,      # Маги используют интеллект
        "healer": 0.6     # Лекари используют интеллект (низкая атака)
    }
    
    def __init__(self, character):

        rates = character.BASE_STATS

        for stat_name, default_value in rates.items():
            setattr(self, stat_name, default_value)
    
    def get_primary_stat_for_role(self, role):
        """Возвращает основную характеристику для данной роли."""
        if role in ["tank", "warrior"]:
            return self.strength
        elif role in ["rogue", "archer"]:
            return self.dexterity
        elif role in ["mage", "healer"]:
            return self.intelligence
        else:
            return self.strength
    
    def scale_stats(self, base_stats, level, growth_rates):
        """Масштабирует характеристики в зависимости от уровня."""
        scaled_stats = {}
        for stat, base_value in base_stats.items():
            growth_rate = growth_rates.get(stat, 0.05)
            scaled_stats[stat] = int(base_value * (1 + (level - 1) * growth_rate))
        return scaled_stats
    
    def update_from_scaled_stats(self, scaled_stats):
        """Обновляет характеристики из масштабированных значений."""
        stat_names = ['dexterity', 'constitution', 'strength', 'intelligence']
        for stat_name in stat_names:
            if stat_name in scaled_stats:
                setattr(self, stat_name, scaled_stats[stat_name])


class DerivedStats:
    """Класс для управления зависимыми характеристиками персонажа."""
    
    def __init__(self, stats, role, level):
        self.max_hp = 0
        self.max_energy = 0
        self.attack = 0
        self.defense = 0
        self.calculate_all(stats, level, role)
    
    def calculate_all(self, stats, level, role):
        """Пересчитывает все зависимые характеристики."""

        dm = stats.DEFENSE_MULTIPLIERS
        psm = stats.PRIMARY_STAT_MULTIPLIERS

        self.max_hp = self.calculate_max_hp(level, stats)
        self.max_energy = self.calculate_max_energy(stats)
        self.attack = self.calculate_attack(role, stats, psm)
        self.defense = self.calculate_defense(role, stats, dm)
    
    def update_level(self, character):
        """Обновляет уровень и пересчитывает характеристики."""
        self.calculate_all(character.stats, character.level, character.role)

    def calculate_defense(self, role, stats, dm):
        """Рассчитывает защиту на основе телосложения и роли."""
        base_defense = int(stats.constitution * 1.0)
        multiplier = dm.get(role, 0.5)
        return int(base_defense * multiplier)
    
    def calculate_attack(self, role, stats, psm):
        """Рассчитывает атаку на основе основной характеристики роли."""
        # Определяем основную характеристику для атаки по роли
        if role in ["tank", "warrior"]:
            primary_stat = stats.strength
        elif role in ["rogue", "archer"]:
            primary_stat = stats.dexterity
        elif role in ["mage", "healer"]:
            primary_stat = stats.intelligence
        else:
            primary_stat = stats.strength  # По умолчанию
            
        multiplier = psm.get(role, 0.8)
        return int(primary_stat * multiplier)
    
    def calculate_max_hp(self, level, stats):
        """Рассчитывает максимальное количество HP на основе телосложения."""
        return int(stats.constitution * 10 + level * 5)
    
    def calculate_max_energy(self, stats):
        """Рассчитывает максимальное количество энергии."""
        return 50 + int(stats.dexterity * 7 + stats.constitution * 2)