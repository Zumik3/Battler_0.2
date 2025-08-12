# character.py
from Characters.Abilities.abilities import AbilityManager
from Config.game_config import BASE_ENERGY_COST
from .base_stats import Stats, DerivedStats

class Character:
    """Базовый класс, представляющий персонажа в игре."""
    def __init__(self, name, role, level=1, is_player=False, can_heal=False):
        
        self.name = name
        self.role = role
        self.is_player = is_player
        self.level = level
        self.alive = True
        self.can_heal = can_heal
        
        # Создаем объекты характеристик
        self.stats = Stats(self)
        self.derived_stats = DerivedStats(self.stats, self.role, self.level)
        
        # Инициализируем hp и энергию
        self.hp = self.derived_stats.max_hp
        self.energy = self.derived_stats.max_energy
        
        # Способности
        self.ability_manager = AbilityManager()
        
    @staticmethod
    def scale_stats(base_stats, level, growth_rates):
        """Масштабирует характеристики в зависимости от уровня."""
        scaled_stats = {}
        for stat, base_value in base_stats.items():
            growth_rate = growth_rates.get(stat, 0.05)
            scaled_stats[stat] = int(base_value * (1 + (level - 1) * growth_rate))
        return scaled_stats
    
    # Добавляем методы для работы со способностями
    def add_ability(self, name, ability):
        """Добавляет способность персонажу."""
        self.ability_manager.add_ability(name, ability)
        
    def get_available_abilities(self):
        """Получает список доступных способностей."""
        return self.ability_manager.get_available_abilities(self)
        
    def use_ability(self, name, targets, **kwargs):
        """Использует способность по имени."""
        return self.ability_manager.use_ability(name, self, targets, **kwargs)
        
    def update_ability_cooldowns(self):
        """Обновляет кулдауны способностей в конце раунда."""
        self.ability_manager.update_cooldowns()
        
    def take_heal(self, heal_amount):
        old_hp = self.hp
        self.hp = min(self.derived_stats.max_hp, self.hp + int(heal_amount))
        return self.hp - old_hp

    def take_damage(self, damage):
        """Наносит урон персонажу, учитывая защиту."""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True
        
    def is_alive(self):
        """Проверяет, жив ли персонаж."""
        return self.alive
        
    def get_level(self):
        """Возвращает уровень персонажа."""
        return self.level
        
    def restore_energy(self, amount=None, percentage=None):
        """
        Восстанавливает энергию персонажа.
        :param amount: конкретное количество энергии для восстановления
        :param percentage: процент от максимальной энергии для восстановления
        """
        if percentage is not None:
            # Восстанавливаем указанный процент от максимальной энергии
            restore_amount = int(self.derived_stats.max_energy * (percentage / 100))
            self.energy = min(self.derived_stats.max_energy, self.energy + restore_amount)
        elif amount is not None:
            # Восстанавливаем конкретное количество энергии
            self.energy = min(self.derived_stats.max_energy, self.energy + amount)
        else:
            # Полное восстановление
            self.energy = self.derived_stats.max_energy
            
    def spend_energy(self, amount=BASE_ENERGY_COST):
        self.energy -= amount