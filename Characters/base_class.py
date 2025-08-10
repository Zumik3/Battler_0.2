from Characters.abilities import AbilityManager
from Config.game_config import BASE_ENERGY_COST
from Battle.battle_logger import battle_logger

class Character:
    """Базовый класс, представляющий персонажа в игре."""
    def __init__(self, name, role, hp=0, max_hp=0, attack=0, defense=0, 
        level=1, is_player=False, ability=None, dexterity=10, constitution=10, strength=10, intelligence=10):
        
        self.name = name
        self.role = role
        self.is_player = is_player
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.level = level  # Добавляем уровень
        self.dexterity = dexterity # Добавляем ловкость
        self.constitution = constitution # Добавляем телосложение
        self.strength = strength # Добавляем силу
        self.intelligence = intelligence # Добавляем интеллект
        self.alive = True
        self.exp = 0  # Добавляем очки опыта
        self.exp_to_next_level = 0  # Опыт до следующего уровня
        # Добавляем энергию
        self.energy = 100
        self.max_energy = 100
        self.can_heal = False
        self.ability_manager = AbilityManager()  # Добавляем менеджер способностей
        self.calculate_derived_attributes()
        
    # В базовом классе Character
    DEFENSE_MULTIPLIERS = {
        "tank": 1.0,
        "warrior": 0.66,
        "healer": 0.6,
        "archer": 0.44,
        "rogue": 0.375,
        "mage": 0.285
    }
    
    @staticmethod
    def scale_stats(base_stats, level, growth_rates):
        """Масштабирует характеристики в зависимости от уровня."""
        scaled_stats = {}
        for stat, base_value in base_stats.items():
            growth_rate = growth_rates.get(stat, 0.05)  # значение по умолчанию
            scaled_stats[stat] = int(base_value * (1 + (level - 1) * growth_rate))
        return scaled_stats
    
    def calculate_defense_from_constitution(self):
        """Рассчитывает защиту на основе телосложения и роли."""
        base_defense = int(self.constitution * 1.0) # Базовая формула
        multiplier = self.DEFENSE_MULTIPLIERS.get(self.role, 0.5) # Множитель по роли
        return int(base_defense * multiplier)
        
    def calculate_attack_from_primary_stat(self):
        """Рассчитывает атаку на основе основной характеристики роли."""
        # Словарь для определения основной характеристики атаки по роли
        primary_stat_multipliers = {
            "tank": 0.8,      # Танки используют силу
            "warrior": 1.0,   # Воины используют силу
            "rogue": 1.2,     # Разбойники используют ловкость
            "archer": 1.1,    # Лучники используют ловкость
            "mage": 1.3,      # Маги используют интеллект
            "healer": 0.6     # Лекари используют интеллект (низкая атака)
        }
        
        # Определяем основную характеристику для атаки по роли
        if self.role in ["tank", "warrior"]:
            primary_stat = self.strength
        elif self.role in ["rogue", "archer"]:
            primary_stat = self.dexterity
        elif self.role in ["mage", "healer"]:
            primary_stat = self.intelligence
        else:
            primary_stat = self.strength  # По умолчанию
            
        multiplier = primary_stat_multipliers.get(self.role, 0.8)
        return int(primary_stat * multiplier)
    
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
        blocked = int((1 - (1 / (1 + self.defense * 0.1))) * damage)
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
        return int(20 * (self.level ** 1.5))  # 20 * level^1.5
        
    def add_exp(self, exp_amount):
        """Добавляет опыт персонажу и проверяет на повышение уровня."""
        if not hasattr(self, 'exp'):
            self.exp = 0
            
        self.exp += exp_amount
        level_up_messages = []
        
        # Проверяем, достаточно ли опыта для повышения уровня
        while self.exp >= self.calculate_exp_for_next_level():
            level_up_message = self.level_up()
            level_up_messages.append(level_up_message)
            
        return level_up_messages
        
    def level_up(self):
        """Повышает уровень персонажа и улучшает его характеристики."""
        old_level = self.level
        old_dexterity = self.dexterity
        old_constitution = self.constitution
        old_strength = self.strength
        old_intelligence = self.intelligence
        old_max_hp = self.max_hp
        old_max_energy = self.max_energy
        old_attack = self.attack
        old_defense = self.defense
        
        self.level += 1
        icon = "🌟"
        
        if hasattr(self, 'BASE_STATS') and hasattr(self, 'GROWTH_RATES'):
            scaled_stats = Character.scale_stats(self.BASE_STATS, self.level, self.GROWTH_RATES)

            # Улучшаем характеристики при повышении уровня, используя scaled_stats
            self.constitution = scaled_stats.get('constitution', self.constitution)
            self.strength = scaled_stats.get('strength', self.strength)
            self.dexterity = scaled_stats.get('dexterity', self.dexterity)
            self.intelligence = scaled_stats.get('intelligence', self.intelligence)
        
        # Пересчитываем производные атрибуты
        self.max_hp = self.calculate_max_hp()  # Пересчитываем максимальное HP
        self.hp = self.max_hp
        
        self.attack = self.calculate_attack_from_primary_stat()  # Пересчитываем атаку
        self.defense = self.calculate_defense_from_constitution()  # Пересчитываем защиту
        
        # Пересчитываем максимальную энергию
        self.max_energy = self.calculate_max_energy()
        self.energy = self.max_energy
        
        # Пересчитываем опыт для следующего уровня
        self.exp_to_next_level = self.calculate_exp_for_next_level()
        
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
        
        # Добавляем измененные характеристики
        stats_changed = []
        if self.dexterity != old_dexterity:
            stats_changed.append((f"dex:{old_dexterity} ➤ {self.dexterity}", 6))  # бирюзовый
        if self.constitution != old_constitution:
            stats_changed.append((f"con:{old_constitution} ➤ {self.constitution}", 6))  # бирюзовый
        if self.strength != old_strength:
            stats_changed.append((f"str:{old_strength} ➤ {self.strength}", 6))  # бирюзовый
        if self.intelligence != old_intelligence:
            stats_changed.append((f"int:{old_intelligence} ➤ {self.intelligence}", 6))  # бирюзовый
        
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
        next_level_exp = self.calculate_exp_for_next_level()
        if next_level_exp <= 0:
            return 100
        return int((self.exp / next_level_exp) * 100)

    def get_level_info(self):
        """Возвращает информацию о текущем уровне и опыте."""
        return {
            'level': self.level,
            'current_exp': self.exp,
            'exp_to_next': self.calculate_exp_for_next_level(),
            'exp_progress': self.get_exp_progress()
        }
        
    def calculate_max_hp(self):
        """Рассчитывает максимальное количество HP персонажа на основе телосложения."""
        return int(self.constitution * 10 + self.level * 5) # Базовая формула HP
        
    def calculate_max_energy(self):
        """Рассчитывает максимальное количество энергии персонажа."""
        return 50 + int(self.dexterity * 7 + self.constitution * 2) # Формула энергии
        
    def restore_energy(self, amount=None, percentage=None):
        """
        Восстанавливает энергию персонажа.
        :param amount: конкретное количество энергии для восстановления
        :param percentage: процент от максимальной энергии для восстановления
        """
        if percentage is not None:
            # Восстанавливаем указанный процент от максимальной энергии
            restore_amount = int(self.max_energy * (percentage / 100))
            self.energy = min(self.max_energy, self.energy + restore_amount)
        elif amount is not None:
            # Восстанавливаем конкретное количество энергии
            self.energy = min(self.max_energy, self.energy + amount)
        else:
            # Полное восстановление
            self.energy = self.max_energy
            
    def spend_energy(self, amount=BASE_ENERGY_COST):
        self.energy -= amount
        
    def calculate_derived_attributes(self):
        self.max_hp = self.calculate_max_hp()
        self.hp = self.max_hp
        self.max_energy = self.calculate_max_energy()
        self.energy = self.max_energy
        self.exp_to_next_level = self.calculate_exp_for_next_level()
        self.defense = self.calculate_defense_from_constitution()
        self.attack = self.calculate_attack_from_primary_stat()