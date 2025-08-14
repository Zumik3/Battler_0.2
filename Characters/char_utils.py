import curses
import random
from Characters.player_classes import Healer, Mage, Rogue, Warrior
import Config.game_config as Config
from Characters.namer import EnemyNamer
from Characters.monster_classes import Goblin, Orc, Skeleton, Wizard, Troll  # Импортируем классы монстров


# === Функции создания команд ===

def create_player_team():
    """
    Создает стандартную команду игрока.
    Возвращает список объектов Character.
    """
    # Пока используем старую систему для совместимости
    # В будущем можно будет выбирать классы
    return [
        Warrior("Роланд", level=2),
        Rogue("Стайлс", level=2),
        Mage("Морган", level=2),
        Healer("Дамиан", level=2),
    ]

def get_enemy_count_for_level_group(level_group):
    """
    Определяет количество врагов в зависимости от уровня группы.
    :param level_group: Уровень группы (1-5)
    :return: Количество врагов
    """
    # Формула: базовое количество + вариативность
    # Уровень 1: 2 врага
    # Уровень 2: 2-3 врага  
    # Уровень 3: 3-4 врага
    # Уровень 4: 3-5 врагов
    # Уровень 5: 4-5 врагов
    
    if level_group == 1:
        return 2  # Фиксированное количество
    elif level_group == 2:
        return random.randint(2, 3)
    elif level_group == 3:
        return random.randint(3, 4)
    elif level_group == 4:
        return random.randint(3, 5)
    elif level_group == 5:
        return random.randint(4, 5)
    else:
        # На случай некорректных значений
        return random.randint(2, 3)

def create_enemies(players):
    """
    Создает случайную группу врагов с общим уровнем, близким к target_level.
    :param target_level: Целевой уровень группы врагов (1-5)
    :return: Список объектов Character.
    """

    total_player_level = sum(p.level for p in players)
    avg_level = total_player_level // len(players)

    # Ограничиваем target_level в пределах 1-5
    target_level = max(1, min(5, avg_level))
    
    # Список возможных типов врагов
    enemy_types = [Goblin, Orc, Skeleton, Wizard, Troll]
    
    # Определяем количество врагов на основе уровня группы
    num_enemies = get_enemy_count_for_level_group(target_level)
    
    # Рассчитываем общий целевой уровень группы
    total_target_level = target_level * num_enemies
    
    # Добавляем вариативность (-1 до +2 от целевого для более легких уровней, -1 до +3 для сложных)
    variance = random.randint(-1, 2) if target_level <= 3 else random.randint(-1, 3)
    total_target_level += variance
    total_target_level = max(num_enemies, total_target_level)  # Минимум по 1 уровню на врага
    
    enemies = []
    used_names = set() # Чтобы избежать повторяющихся имен
    
    # Распределяем уровни между врагами
    remaining_level = total_target_level
    for i in range(num_enemies):
        # Для последнего врага используем оставшийся уровень
        if i == num_enemies - 1:
            enemy_level = remaining_level
        else:
            # Распределяем уровень между оставшимися врагами
            max_level_for_this_enemy = remaining_level - (num_enemies - i - 1)  # Минимум 1 уровень на оставшихся
            min_level_for_this_enemy = 1
            if max_level_for_this_enemy >= min_level_for_this_enemy:
                enemy_level = random.randint(min_level_for_this_enemy, max_level_for_this_enemy)
            else:
                enemy_level = min_level_for_this_enemy
        
        # Ограничиваем уровень в пределах разумного (1-10)
        enemy_level = max(1, min(10, enemy_level))
        remaining_level -= enemy_level
        
        # Выбираем случайный тип врага
        enemy_class = random.choice(enemy_types)
        
        # Генерируем уникальное имя
        name = EnemyNamer.generate_name()
        attempts = 0
        while name in used_names and attempts < 10: # Ограничение на попытки
            name = EnemyNamer.generate_name()
            attempts += 1
        used_names.add(name)
        
        # Создаем врага с уровнем
        enemy = enemy_class(name, level=enemy_level)
        enemies.append(enemy)
        
        # Убеждаемся, что оставшийся уровень не отрицательный
        remaining_level = max(0, remaining_level)
    
    return enemies