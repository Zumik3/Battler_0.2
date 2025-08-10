# character.py
from Characters.abilities import AbilityManager
from Config.game_config import BASE_ENERGY_COST
from Battle.battle_logger import battle_logger
from .base_stats import Stats, DerivedStats

class Character:
    """Базовый класс, представляющий персонажа в игре."""
    def __init__(self, name, role, level=1, is_player=False, can_heal=False):
        
        self.name = name
        self.role = role
        self.is_player = is_player
        self.level = level
        self.alive = True
        self.exp = 0
        self.can_heal = can_heal
        
        # Создаем объекты характеристик
        self.stats = Stats(self)
        self.derived_stats = DerivedStats(self.stats, self.role, self.level)
        
        # Инициализируем hp и энергию
        self.hp = self.derived_stats.max_hp
        self.energy = self.derived_stats.max_energy
        
        # Способности
        self.ability_manager = AbilityManager()

        self.calculate_exp_for_next_level()
        
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
        
    def take_damage(self, damage):
        """Наносит урон персонажу, учитывая защиту."""
        blocked = int((1 - (1 / (1 + self.derived_stats.defense * 0.1))) * damage)
        blocked = min(blocked, int(damage * 0.7))
        blocked = max(0, blocked)
        final_damage = max(1, damage - blocked)
        self.hp -= final_damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return final_damage, blocked
        
    def is_alive(self):
        """Проверяет, жив ли персонаж."""
        return self.alive
        
    def get_level(self):
        """Возвращает уровень персонажа."""
        return self.level
        
    def calculate_exp_for_next_level(self):
        """Рассчитывает количество опыта, необходимого для следующего уровня."""
        self.exp_to_next_level = int(20 * (self.level ** 1.5))
        
    def add_exp(self, exp_amount):
        """Добавляет опыт персонажу и проверяет на повышение уровня."""
        if not hasattr(self, 'exp'):
            self.exp = 0
            
        self.exp += exp_amount
        level_up_messages = []
        
        # Проверяем, достаточно ли опыта для повышения уровня
        while self.exp >= self.exp_to_next_level:
            level_up_message = self.level_up()
            level_up_messages.append(level_up_message)
            
        return level_up_messages
        
    def level_up(self):
        """Повышает уровень персонажа и улучшает его характеристики."""
        old_level = self.level
        old_dexterity = self.stats.dexterity
        old_constitution = self.stats.constitution
        old_strength = self.stats.strength
        old_intelligence = self.stats.intelligence
        
        self.level += 1
        
        if hasattr(self, 'BASE_STATS') and hasattr(self, 'GROWTH_RATES'):
            scaled_stats = Character.scale_stats(self.BASE_STATS, self.level, self.GROWTH_RATES)
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
        elements = [
            (self.name, 2),           # зеленый цвет для имени
            (" получает уровень ", 0),
            (str(old_level), 3),      # желтый цвет для старого уровня
            (" ➤ ", 0),
            (str(self.level), 3),     # желтый цвет для нового уровня
            (". (", 0)
        ]
        
        # Добавляем ТОЛЬКО основные измененные характеристики
        stats_changed = []
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
        template = "".join([f"%{i+1}" for i in range(len(elements))])
        message = battle_logger.create_log_message(template, elements)
        
        return message
        
    def get_exp_progress(self):
        """Возвращает прогресс до следующего уровня в процентах."""
        if self.exp_to_next_level <= 0:
            return 100
        return int((self.exp / self.exp_to_next_level) * 100)

    def get_level_info(self):
        """Возвращает информацию о текущем уровне и опыте."""
        return {
            'level': self.level,
            'current_exp': self.exp,
            'exp_to_next': self.exp_to_next_level,
            'exp_progress': self.get_exp_progress()
        }
        
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