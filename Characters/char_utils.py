import curses
import random
import Config.game_config as Config
from Characters.namer import EnemyNamer
from Characters.monster_classes import Goblin, Orc, Skeleton, Wizard, Troll  # Импортируем классы монстров


def draw_character_name(stdscr, y, x, char, base_color):
    """
    Отображает имя персонажа с правильной расцветкой.
    Иконка смерти включена в строку, длина поля保持 постоянной.
    
    :param stdscr: Окно curses для отрисовки
    :param y: Координата Y
    :param x: Координата X
    :param char: Персонаж
    :param base_color: Базовый цвет из Config.COLORS
    """
    name_width = Config.NAME_COLUMN_WIDTH
    base_name = f"{char.name} [{char.level}]"
    
    # Если персонаж мёртв — добавляем иконку смерти
    if char.hp <= 0:
        # Используем ASCII символ вместо эмодзи для стабильной ширины
        display_name = f"† {base_name}"  # Крест вместо эмодзи
        name_color = curses.color_pair(8) if curses.COLORS >= 9 else curses.A_DIM
    else:
        display_name = base_name
        name_color = curses.color_pair(base_color)
    
    # Обрезаем или дополняем до нужной длины
    if len(display_name) > name_width:
        # Обрезаем до name_width - 3 и добавляем "..."
        display_name = display_name[:name_width-3] + "..."
    else:
        # Дополняем пробелами до нужной длины
        display_name = display_name.ljust(name_width)
    
    # Выводим имя
    try:
        stdscr.addstr(y, x, display_name, name_color)
    except curses.error:
        pass

# === Функции создания команд ===

def create_player_team():
    """
    Создает стандартную команду игрока.
    Возвращает список объектов Character.
    """
    from Characters.player_classes import Tank, Archer, Healer, Rogue  # Локальный импорт для избежания циклических импортов
    
    # Пока используем старую систему для совместимости
    # В будущем можно будет выбирать классы
    return [
        Tank("Танк", level=1),
        Rogue("Разбойник", level=1),
        Archer("Лучник", level=1),
        Healer("Лекарь", level=1),
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