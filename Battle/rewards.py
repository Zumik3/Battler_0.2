# rewards.py - Система наград в игре

from typing import List, Dict, Any
import random
from Config.game_config import EXP_BASE, GOLD_BASE, EXP_VARIANCE, GOLD_VARIANCE
from Inventory.inventory import get_inventory
from Battle.battle_logger import battle_logger
from Items.item_generator import ItemGenerator


class Reward:
    """Базовый класс для наград."""
    
    def __init__(self, amount: int):
        self.amount = amount
        self.type = "base"
        self.icon = "🎁"
    
    def apply_reward(self, character=None):
        """Применяет награду."""
        raise NotImplementedError("Метод apply_reward должен быть реализован")


class GoldReward(Reward):
    """Награда в виде золотых монет."""
    
    def __init__(self, amount: int):
        super().__init__(amount)
        self.type = "gold"
        self.icon = "💰"
    
    def apply_reward(self, character=None):
        """Добавляет золото в общий инвентарь."""
        inventory = get_inventory()
        inventory.add_gold(self.amount)
        
        # Создаем сообщение
        template = "%1 Получено %2 золотых монет!"
        elements = [(self.icon, 0), (str(self.amount), 6)]  # голубой цвет для количества
        
        self.message = battle_logger.create_log_message(template, elements)
        return self


class ExperienceReward(Reward):
    """Награда в виде опыта."""
    
    def __init__(self, amount: int):
        super().__init__(amount)
        self.type = "exp"
        self.icon = "⭐"
        self.exp_distribution = {}  # Распределение опыта по персонажам
        self.level_up_messages = []  # Сообщения о повышении уровня
    
    def _distribute_exp_evenly(self, characters: List, total_exp: int) -> Dict[str, int]:
        """
        Равномерно распределяет опыт между персонажами с небольшими вариациями.
        
        :param characters: Список персонажей
        :param total_exp: Общее количество опыта
        :return: Словарь {имя_персонажа: количество_опыта}
        """
        if not characters:
            return {}
        
        num_characters = len(characters)
        base_exp = total_exp // num_characters
        remaining_exp = total_exp % num_characters
        
        distribution = {}
        
        # Распределяем базовый опыт
        for character in characters:
            distribution[character.name] = base_exp
        
        # Распределяем остаток случайным образом
        characters_list = list(characters)
        for i in range(remaining_exp):
            # Добавляем 1 очко опыта случайному персонажу
            random_character = random.choice(characters_list)
            distribution[random_character.name] += 1
        
        # Добавляем небольшие вариации (±5-10%)
        for character in characters:
            current_exp = distribution[character.name]
            # Вариация от -10% до +10%
            variation = int(current_exp * random.uniform(-0.1, 0.1))
            # Убеждаемся, что опыт не станет отрицательным
            variation = max(variation, -current_exp + 1) if current_exp > 1 else 0
            distribution[character.name] += variation
        
        # Корректируем общую сумму, если она изменилась из-за вариаций
        actual_total = sum(distribution.values())
        diff = total_exp - actual_total
        
        if diff != 0:
            # Распределяем разницу случайным образом
            adjustment_characters = list(characters)
            random.shuffle(adjustment_characters)
            
            for i in range(abs(diff)):
                if i < len(adjustment_characters):
                    char_name = adjustment_characters[i].name
                    if diff > 0:
                        distribution[char_name] += 1
                    else:
                        # Убеждаемся, что опыт не станет <= 0
                        if distribution[char_name] > 1:
                            distribution[char_name] -= 1
        
        return distribution
    
    def apply_reward(self, characters: List = None):
        """
        Применяет опыт ко всем персонажам и формирует общее сообщение.
        
        :param characters: Список персонажей для получения опыта
        """
        if not characters:
            # Создаем сообщение об отсутствии персонажей
            template = "%1 Нет персонажей для получения опыта!"
            elements = [(self.icon, 0)]
            self.message = battle_logger.create_log_message(template, elements)
            return self
        
        # Равномерно распределяем опыт с вариациями
        self.exp_distribution = self._distribute_exp_evenly(characters, self.amount)
        
        # Очищаем предыдущие данные
        self.level_up_messages = []
        
        # Применяем опыт каждому персонажу
        for character in characters:
            if character.name in self.exp_distribution:
                actual_exp = self.exp_distribution[character.name]
                if actual_exp > 0 and hasattr(character, 'add_exp'):
                    level_up_msgs = character.add_exp(actual_exp)
                    self.level_up_messages.extend(level_up_msgs)
        
        # Формируем общее сообщение
        if self.exp_distribution:
            # Создаем цветные элементы для каждого персонажа
            elements = [(self.icon, 0), (" Получено опыта: ", 0), (str(self.amount), 3), (" (", 0)]
            
            # Добавляем имена (зеленые) и опыт (желтый) каждого персонажа
            items_list = list(self.exp_distribution.items())
            for i, (name, exp) in enumerate(items_list):
                elements.extend([(name, 2), (": ", 0), (str(exp), 3)])
                if i < len(items_list) - 1:
                    elements.append((", ", 0))
            
            elements.append((")", 0))
            # Создаем сообщение из всех элементов
            template = "".join([f"%{i+1}" for i in range(len(elements))])
            self.message = battle_logger.create_log_message(template, elements)
        else:
            template = "%1 Опыт не был распределен!"
            elements = [(self.icon, 0)]
            self.message = battle_logger.create_log_message(template, elements)
        
        return self


class LootReward(Reward):
    """Награда в виде лута (предметов)."""
    
    def __init__(self, items: List = None):
        super().__init__(len(items) if items else 0)
        self.type = "loot"
        self.icon = "🧳"
        self.items = items if items else []
        self.messages = []
    
    def apply_reward(self, character=None):
        """Добавляет предметы в инвентарь."""
        inventory = get_inventory()
        
        if not self.items:
            template = "%1 Лут пуст!"
            elements = [(self.icon, 0)]
            self.message = battle_logger.create_log_message(template, elements)
            return self
        
        # Добавляем каждый предмет в инвентарь
        for item in self.items:
            inventory.add_item(item, 1)
        
        # Создаем сообщение о получении лута
        if len(self.items) == 1:
            item_name = self.items[0].name
            template = "%1 Получен предмет: %2!"
            elements = [(self.icon, 0), (item_name, 2)]  # зеленый цвет для имени предмета
        else:
            template = "%1 Получено %2 предметов!"
            elements = [(self.icon, 0), (str(len(self.items)), 3)]  # желтый цвет для количества
        
        self.message = battle_logger.create_log_message(template, elements)
        
        # Добавляем детальные сообщения для каждого предмета
        self.messages = []
        for item in self.items:
            detail_template = "  ◦ %1 (%2, Ур.%3)"
            detail_elements = [
                (item.name, 2),  # зеленый цвет для имени
                (item.get_rarity_name(), item.get_rarity_color()),  # цвет редкости
                (str(item.level), 3)  # желтый цвет для уровня
            ]
            detail_message = battle_logger.create_log_message(detail_template, detail_elements)
            self.messages.append(detail_message)
        
        return self


class BattleRewards:
    """Награды за победу в битве."""
    
    @classmethod
    def calculate_for_enemy(cls, enemy) -> Dict[str, int]:
        """Рассчитывает награды за одного врага."""
        level = getattr(enemy, 'level', 1)
        
        exp = level * EXP_BASE + random.randint(0, level * EXP_VARIANCE)
        gold = level * GOLD_BASE + random.randint(0, level * GOLD_VARIANCE)
        
        return {"exp": exp, "gold": gold}
    
    @classmethod
    def calculate_loot_chance(cls, defeated_enemies: List) -> int:
        """
        Рассчитывает количество предметов в луте на основе врагов.
        
        :param defeated_enemies: Список побежденных врагов
        :return: Количество предметов в луте
        """
        if not defeated_enemies:
            return 0
        
        # Базовое количество предметов - 1
        base_items = 1
        
        # Добавляем предметы за каждого врага (чем выше уровень, тем больше шанс)
        total_level = sum(getattr(enemy, 'level', 1) for enemy in defeated_enemies)
        enemy_count = len(defeated_enemies)
        
        # Шанс получить дополнительные предметы
        additional_items = 0
        for enemy in defeated_enemies:
            enemy_level = getattr(enemy, 'level', 1)
            # Шанс получить предмет зависит от уровня врага
            if random.random() < (enemy_level * 0.1):  # 10% шанс на уровень
                additional_items += 1
        
        # Бонус за количество врагов
        group_bonus = enemy_count // 3  # 1 бонусный предмет за каждых 3 врагов
        
        total_items = base_items + additional_items + group_bonus
        
        # Ограничиваем максимальное количество предметов
        max_items = min(5, enemy_count + 2)  # максимум 5 предметов или количество врагов+2
        total_items = min(total_items, max_items)
        
        return max(1, total_items)  # Минимум 1 предмет
    
    @classmethod
    def generate_loot(cls, defeated_enemies: List) -> List:
        """
        Генерирует лут на основе побежденных врагов.
        
        :param defeated_enemies: Список побежденных врагов
        :return: Список сгенерированных предметов
        """
        if not defeated_enemies:
            return []
        
        # Определяем максимальный уровень среди врагов
        max_level = max(getattr(enemy, 'level', 1) for enemy in defeated_enemies)
        min_level = max(1, max_level - 2)  # Минимальный уровень на 2 ниже максимального
        
        # Определяем количество предметов
        num_items = cls.calculate_loot_chance(defeated_enemies)
        
        # Генерируем лут
        items = []
        for _ in range(num_items):
            # Генерируем предмет с уровнем от min_level до max_level+1
            item_level = random.randint(min_level, max_level + 1)
            
            # Генерируем предмет (с небольшим шансом получить редкий)
            rarity_weights = [0.6, 0.25, 0.1, 0.04, 0.01]  # Больше шанс на обычные предметы
            item = ItemGenerator.generate_random_item(
                min_level=item_level,
                max_level=item_level + 1,
                rarity_weights=rarity_weights
            )
            items.append(item)
        
        return items
    
    @classmethod
    def generate_rewards(cls, defeated_enemies: List) -> List[Reward]:
        """Генерирует награды за список побежденных врагов."""
        total_exp = 0
        total_gold = 0
        
        # Суммируем награды за всех врагов
        for enemy in defeated_enemies:
            rewards = cls.calculate_for_enemy(enemy)
            total_exp += rewards["exp"]
            total_gold += rewards["gold"]
        
        # Создаем объекты наград
        rewards_list = []
        if total_exp > 0:
            rewards_list.append(ExperienceReward(total_exp))
        if total_gold > 0:
            rewards_list.append(GoldReward(total_gold))
        
        # Генерируем лут
        loot_items = cls.generate_loot(defeated_enemies)
        if loot_items:
            rewards_list.append(LootReward(loot_items))
        
        return rewards_list
    
    @classmethod
    def distribute_rewards(cls, defeated_enemies: List, player_characters: List) -> Dict[str, Any]:
        """
        Распределяет награды между персонажами.
        
        :param defeated_enemies: Список побежденных врагов
        :param player_characters: Список живых персонажей игроков
        :return: Словарь с результатами наград
        """
        if not defeated_enemies or not player_characters:
            return {
                'exp_reward': None,
                'gold_reward': None,
                'loot_reward': None,
                'messages': [],
                'level_up_messages': []
            }
        
        # Генерируем награды
        rewards = cls.generate_rewards(defeated_enemies)
        
        results = {
            'exp_reward': None,
            'gold_reward': None,
            'loot_reward': None,
            'messages': [],
            'level_up_messages': []
        }
        
        # Применяем награды
        for reward in rewards:
            if isinstance(reward, ExperienceReward):
                # Применяем опыт ко всем персонажам
                result = reward.apply_reward(player_characters)
                results['exp_reward'] = result
                results['messages'].append(result.message)
                results['level_up_messages'].extend(result.level_up_messages)
                
            elif isinstance(reward, GoldReward):
                # Применяем золото (добавляется в общий инвентарь)
                result = reward.apply_reward()
                results['gold_reward'] = result
                results['messages'].append(result.message)
                
            elif isinstance(reward, LootReward):
                # Применяем лут (добавляется в общий инвентарь)
                result = reward.apply_reward()
                results['loot_reward'] = result
                results['messages'].append(result.message)
                results['messages'].extend(result.messages)
        
        return results