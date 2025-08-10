# display.py - Логика отображения и обновления экрана

import curses
from Battle.battle_logger import battle_logger
from Config.curses_config import *
from Config.game_config import NAME_COLUMN_WIDTH, HP_BAR_WIDTH, ENERGY_BAR_WIDTH
from Characters.char_utils import draw_character_name
from Utils.progress_bar import draw_progress_bar, draw_energy_bar
from Inventory.inventory import get_inventory

def create_screen_observer(stdscr, command_handler):
    """Создает наблюдателя для автоматического обновления экрана"""
    def screen_observer(message):
        update_display(stdscr, command_handler)
        stdscr.refresh()
    return screen_observer

def update_display(stdscr, command_handler):
    """Обновляет отображение экрана"""
    try:
        height, width = stdscr.getmaxyx()
        input_str = command_handler.get_input()
        
        # Очищаем экран
        stdscr.clear()
        stdscr.bkgd(' ', get_color_pair(COLOR_WHITE))
        
        # === ВЕРХНЯЯ ОБЛАСТЬ ===
        stdscr.addstr(0, width//2-10, "🛡️ ПРИМИТИВНАЯ ИГРА", get_color_pair(COLOR_CYAN) | curses.A_BOLD)
        inventory = get_inventory()
        stdscr.addstr(1, 2, f"Золото: {inventory.get_gold()}", get_color_pair(COLOR_GRAY))
        stdscr.addstr(2, 0, "─" * (width-1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
        
        # === ОБЛАСТЬ ПЕРСОНАЖЕЙ ===
        display_characters(stdscr, command_handler.players, command_handler.enemies, width, height)

        # === ОБЛАСТЬ ЛОГА ===
        log_start_y = 9
        stdscr.addstr(log_start_y, 0, "─" * (width-1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
        stdscr.addstr(log_start_y + 1, 2, "📜 ЛОГ БОЯ:", get_color_pair(COLOR_WHITE) | curses.A_BOLD)
        
        display_log(stdscr, width, height, log_start_y)
        
        # === ОБЛАСТЬ ВВОДА ===
        input_y = height - 2
        stdscr.addstr(input_y, 0, "─" * (width-1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
        stdscr.addstr(input_y + 1, 0, f"❱ {input_str}", get_color_pair(COLOR_WHITE) | curses.A_BOLD)
        
    except curses.error:
        pass

def display_characters(stdscr, players, enemies, width, height):
    """Отображает персонажей на экране"""
    
    # Левая часть - игроки
    mid_x = width // 2
    stdscr.addstr(4, 2, "🧍 Команда приключенцев:", curses.A_BOLD)

    for i, char in enumerate(players):
        draw_character_info(stdscr, char, 5 + i, 4, is_player=True)
    
    # === Враги ===
    stdscr.addstr(4, mid_x + 2, "👹 Враги:", curses.A_BOLD)
    for i, char in enumerate(enemies):
        draw_character_info(stdscr, char, 6 + i, mid_x + 4, is_player=False)

def draw_character_info(stdscr, character, y, x, is_player=True):
    """
    Универсальная функция отрисовки информации о персонаже
    
    Args:
        stdscr: Экран curses
        character: Объект персонажа
        y, x: Координаты для отрисовки
        is_player: True для игроков, False для монстров
    """
    # Имя персонажа
    draw_character_name(stdscr, y, x, character)
    
    # Рисуем HP-бар
    bar_x = x + NAME_COLUMN_WIDTH + 1
    draw_progress_bar(
        stdscr=stdscr,
        y=y,
        x=bar_x,
        current_value=character.hp,
        max_value=character.derived_stats.max_hp,
        bar_width=HP_BAR_WIDTH
    )
    
    # Рисуем энергетический бар
    energy_bar_x = bar_x + HP_BAR_WIDTH + 2
    draw_energy_bar(
        stdscr=stdscr,
        y=y,
        x=energy_bar_x,
        current_energy=character.energy,
        max_energy=character.derived_stats.max_energy,
        bar_width=ENERGY_BAR_WIDTH
    )

def display_log(stdscr, width, height, log_start_y) -> None:
    """Отображает лог боя"""
    # Отображаем лог - занимаем большую часть экрана
    log_height = height - log_start_y - 5
    log_lines = battle_logger.get_lines()
    if log_lines:
        visible_log_lines = log_lines[-log_height:] if len(log_lines) > log_height else log_lines
        for i, line in enumerate(visible_log_lines):
            if log_start_y + 2 + i < height - 3:
                display_line = line[:width-4]

                if isinstance(display_line, list):
                    current_x = 2
                    for text, color_pair in display_line:
                        if color_pair == 0:
                            stdscr.addstr(log_start_y + 2 + i, current_x, text)
                        else:
                            stdscr.addstr(log_start_y + 2 + i, current_x, text, curses.color_pair(color_pair))
                        current_x += len(text)
                else:
                    stdscr.addstr(log_start_y + 2 + i, 2, display_line, get_color_pair(COLOR_WHITE))

def display_inventory_screen(stdscr, players):
    """Отображает экран инвентаря на весь экран"""
    inventory = get_inventory()
    
    while True:
        try:
            height, width = stdscr.getmaxyx()
            stdscr.clear()
            
            # Заголовок инвентаря
            stdscr.addstr(0, width//2-8, "🎒 ИНВЕНТАРЬ", 
                         get_color_pair(COLOR_CYAN) | curses.A_BOLD)
            stdscr.addstr(1, 0, "─" * (width-1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
            
            # === БЛОК 1: ХАРАКТЕРИСТИКИ ГЕРОЕВ (2 в ряд) ===
            stdscr.addstr(2, 2, "👥 ГЕРОИ", 
                         get_color_pair(COLOR_YELLOW) | curses.A_BOLD)
            stdscr.addstr(3, 0, "─" * (width-1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
            
            # Отображаем героев по 2 в ряд
            heroes_per_row = 2
            hero_width = width // heroes_per_row - 2
            
            max_hero_rows = 0
            for i, player in enumerate(players):
                row = i // heroes_per_row  # Номер строки
                col = i % heroes_per_row   # Номер колонки
                
                hero_x = col * hero_width + 2
                hero_y = 4 + row * 6  # 6 строк на каждого героя
                
                max_hero_rows = max(max_hero_rows, row + 1)
                
                if hero_y + 5 < height - 4:  # Проверяем, помещается ли
                    display_hero_stats_in_inventory(stdscr, player, hero_y, hero_x, hero_width)
            
            # === БЛОК 2: ИНВЕНТАРЬ С ПРЕДМЕТАМИ (сразу после героев) ===
            inventory_start_y = 4 + max_hero_rows * 6
            if len(players) == 0:
                inventory_start_y = 4
            
            stdscr.addstr(inventory_start_y, 2, "🧳 ИНВЕНТАРЬ", 
                         get_color_pair(COLOR_MAGENTA) | curses.A_BOLD)
            stdscr.addstr(inventory_start_y + 1, 0, "─" * (width-1), 
                         get_color_pair(COLOR_GRAY) | curses.A_DIM)
            
            # Отображаем предметы из инвентаря
            item_objects = inventory.get_all_items() if hasattr(inventory, 'get_all_items') else {}
            if item_objects:
                item_y = inventory_start_y + 3
                item_index = 0
                
                # item_objects теперь содержит {item_object: quantity}
                for item_object, quantity in item_objects.items():
                    if item_y + item_index < height - 3:  # Проверяем границы экрана
                        try:
                            # Используем новую систему отображения предметов
                            template, elements = item_object.get_detailed_display_template()
                            
                            # Создаем строку с количеством
                            quantity_text = f" х{quantity}" if quantity > 1 else ""
                            
                            # Отображаем предмет с правильной расцветкой
                            current_x = 4
                            stdscr.addstr(item_y + item_index, current_x, "◦ ", get_color_pair(COLOR_WHITE))
                            current_x += 2
                            
                            # Отображаем каждый элемент шаблона с соответствующими цветами
                            for text, color in elements:
                                if current_x < width - 4:
                                    stdscr.addstr(item_y + item_index, current_x, text, curses.color_pair(color))
                                    current_x += len(text)
                            
                            # Добавляем количество
                            if quantity_text:
                                if current_x < width - 4:
                                    stdscr.addstr(item_y + item_index, current_x, quantity_text, get_color_pair(COLOR_GRAY))
                                    current_x += len(quantity_text)
                            
                            # Добавляем свойства предмета, если они есть
                            properties = item_object.get_all_properties()
                            if properties:
                                prop_text = " ["
                                prop_parts = []
                                
                                # Формируем список свойств для отображения
                                for prop_name, prop_value in properties.items():
                                    if prop_value > 0:  # Отображаем только положительные значения
                                        # Преобразуем названия свойств в читаемый формат
                                        readable_name = prop_name.replace('_bonus', '').replace('_', ' ').title()
                                        prop_parts.append(f"{readable_name}: {prop_value}")
                                
                                if prop_parts:
                                    prop_text += ", ".join(prop_parts)
                                    prop_text += "]"
                                    
                                    # Отображаем свойства серым цветом
                                    if current_x < width - 4 and len(prop_text) < (width - current_x - 4):
                                        stdscr.addstr(item_y + item_index, current_x, prop_text, get_color_pair(COLOR_GRAY))
                            
                            item_index += 1
                        except Exception as e:
                            # На случай если у предмета нет метода get_detailed_display_template
                            item_name = getattr(item_object, 'name', str(item_object))
                            stdscr.addstr(item_y + item_index, 4, f"◦ {item_name}: {quantity}", 
                                         get_color_pair(COLOR_WHITE))
                            item_index += 1
            else:
                stdscr.addstr(inventory_start_y + 3, 4, "Инвентарь пуст", 
                             get_color_pair(COLOR_GRAY))
            
            # Подсказка по выходу
            stdscr.addstr(height - 2, 0, "─" * (width-1), 
                         get_color_pair(COLOR_GRAY) | curses.A_DIM)
            stdscr.addstr(height - 1, 2, "Введите 'exit', 'quit' или 'q' для выхода", 
                         get_color_pair(COLOR_GRAY) | curses.A_DIM)
            
            stdscr.refresh()
            
            # Обработка ввода
            key = stdscr.getch()
            if key == 27:  # ESC
                break
            elif key == curses.KEY_RESIZE:
                continue
            elif key != -1:
                # Обработка текстового ввода для команд выхода
                try:
                    char = chr(key).lower()
                    if char in ['q', 'e']:  # q, exit
                        break
                except:
                    pass
                if key in [10, 13]:  # Enter
                    # Можно добавить обработку команд здесь
                    pass
                    
        except curses.error:
            pass

def display_hero_stats_in_inventory(stdscr, player, y, x, max_width):
    """Отображает характеристики героя в инвентаре в 2 колонки"""
    try:
        # Имя героя с HP и энергией в одной строке (имя зеленым)
        name = player.name[:20] if len(player.name) > 20 else player.name
        hp_text = f"HP: {player.hp}/{player.derived_stats.max_hp}"
        energy_text = f"Энергия: {player.energy}/{player.derived_stats.max_energy}"
        
        # Первая строка: Имя (зеленый) HP и Энергия (стандартные цвета)
        stdscr.addstr(y, x, name, get_color_pair(COLOR_GREEN) | curses.A_BOLD)
        stdscr.addstr(y, x + len(name), f" {hp_text}  {energy_text}", 
                     get_color_pair(COLOR_CYAN) | curses.A_BOLD)
        
        # Левая колонка - уровень, опыт, атака, защита
        left_x = x
        level_text = f"Уровень: {getattr(player, 'level', 'N/A')}" if hasattr(player, 'level') else "Уровень: N/A"
        stdscr.addstr(y+1, left_x, level_text)
        
        # Опыт с прогрессом до следующего уровня
        if hasattr(player, 'exp') and hasattr(player, 'exp_to_next_level'):
            exp_text = f"Опыт: {player.exp}/{player.exp_to_next_level}"
        elif hasattr(player, 'exp'):
            exp_text = f"Опыт: {player.exp}"
        else:
            exp_text = "Опыт: N/A"
        stdscr.addstr(y+2, left_x, exp_text)
        
        attack_text = f"Атака: {getattr(player.derived_stats, 'attack', 'N/A')}" if hasattr(player, 'derived_stats') else "⚔️ Атака: N/A"
        stdscr.addstr(y+3, left_x, attack_text)
        
        defense_text = f"Защита: {getattr(player.derived_stats, 'defense', 'N/A')}" if hasattr(player, 'derived_stats') else "🛡️ Защита: N/A"
        stdscr.addstr(y+4, left_x, defense_text)
        
        # Правая колонка - базовые характеристики
        right_x = x + max_width // 2
        if hasattr(player, 'stats'):
            if hasattr(player.stats, 'strength'):
                stdscr.addstr(y+1, right_x, f"Сила: {player.stats.strength}")
            if hasattr(player.stats, 'dexterity'):
                stdscr.addstr(y+2, right_x, f"Ловкость: {player.stats.dexterity}")
            if hasattr(player.stats, 'intelligence'):
                stdscr.addstr(y+3, right_x, f"Интеллект: {player.stats.intelligence}")
            if hasattr(player.stats, 'constitution'):
                stdscr.addstr(y+4, right_x, f"Выносливость: {player.stats.constitution}")
        
        # Разделитель между колонками
        if y + 5 < stdscr.getmaxyx()[0]:
            stdscr.addstr(y+5, x, "─" * min(max_width-4, stdscr.getmaxyx()[1]-x-1), 
                         get_color_pair(COLOR_GRAY) | curses.A_DIM)
        
    except curses.error:
        pass