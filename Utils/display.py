# display.py - Логика отображения и обновления экрана

import curses
from Battle.battle_logger import battle_logger
from Config.curses_config import (
    get_color_pair,
    COLOR_CYAN,
    COLOR_GRAY,
    COLOR_WHITE,
    COLOR_MAGENTA,
    COLOR_GREEN,
    COLOR_YELLOW
)
from Inventory.inventory import get_inventory
from Utils.UI.draw_character import DrawCharacter
from Utils.UI.key_hints import INVENTORY_HINTS, MAIN_HINTS


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

        # Очищаем экран
        stdscr.clear()
        stdscr.bkgd(' ', get_color_pair(COLOR_WHITE))

        # === ВЕРХНЯЯ ОБЛАСТЬ ===
        stdscr.addstr(0, width // 2 - 10, "YET ANOTHER AUTOBATTLER", get_color_pair(COLOR_CYAN) | curses.A_BOLD)
        inventory = get_inventory()
        stdscr.addstr(1, 2, f"Золото: {inventory.get_gold()}", get_color_pair(COLOR_GRAY))
        stdscr.addstr(2, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

        # === ОБЛАСТЬ ПЕРСОНАЖЕЙ ===
        display_characters(stdscr, command_handler.players, command_handler.enemies, width)

        # === ОБЛАСТЬ ЛОГА ===
        log_start_y = 9
        stdscr.addstr(log_start_y, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
        stdscr.addstr(log_start_y + 1, 2, "📜 ЛОГ БОЯ:", get_color_pair(COLOR_WHITE) | curses.A_BOLD)
        display_log(stdscr, width, height, log_start_y)

        # === ПОДСКАЗКИ В НИЖНЕЙ ЧАСТИ ===
        MAIN_HINTS.display_hints(stdscr)

    except curses.error:
        pass  # Игнорируем ошибки отрисовки (например, при ресайзе)


def display_characters(stdscr, players, enemies, width):
    """Отображает персонажей на экране с помощью DrawCharacter"""
    
    # Определения позиций и заголовков
    CHARACTER_START_X = 4
    CHARACTER_START_Y = 4
    CHARACTER_HEADER_Y = 3
    CHARACTER_HEADER_X = 2

    PLAYERS_HEADER_TEXT = "🧍 Герои:"
    ENEMIES_HEADER_TEXT = "🎲 Событие: (схватка)" #TODO: доработать систему событий
    
    mid_x = width // 2

    # Заголовок игроков
    stdscr.addstr(CHARACTER_HEADER_Y, CHARACTER_HEADER_X, PLAYERS_HEADER_TEXT, curses.A_BOLD)

    # Отрисовка игроков
    for i, char in enumerate(players):
        y = CHARACTER_START_Y + i
        x = CHARACTER_START_X
        DrawCharacter.draw_character_row(stdscr, char, y, x, is_player=True)

    # Заголовок врагов
    stdscr.addstr(CHARACTER_HEADER_Y, mid_x + CHARACTER_HEADER_X, ENEMIES_HEADER_TEXT, curses.A_BOLD)

    # Отрисовка врагов
    for i, char in enumerate(enemies):
        y = CHARACTER_START_Y + i
        x = mid_x + CHARACTER_START_X
        DrawCharacter.draw_character_row(stdscr, char, y, x, is_player=False)


def display_log(stdscr, width, height, log_start_y):
    """Отображает лог боя"""
    log_height = height - log_start_y - 10  # Увеличиваем отступ для подсказок
    log_lines = battle_logger.get_lines()

    if log_lines:
        visible_log_lines = log_lines[-log_height:] if len(log_lines) > log_height else log_lines
        for i, line in enumerate(visible_log_lines):
            if log_start_y + 2 + i >= height - 7:  # Учитываем подсказки
                break

            display_line = line[:width - 4]

            try:
                if isinstance(display_line, list):
                    current_x = 2
                    for text, color_pair in display_line:
                        if color_pair == 0:
                            stdscr.addstr(log_start_y + 2 + i, current_x, text)
                        else:
                            stdscr.addstr(log_start_y + 2 + i, current_x, text, get_color_pair(color_pair))
                        current_x += len(text)
                else:
                    stdscr.addstr(log_start_y + 2 + i, 2, display_line, get_color_pair(COLOR_WHITE))
            except curses.error:
                pass  # Игнорируем выход за границы экрана


def display_inventory_screen(stdscr, players):
    """Отображает экран инвентаря на весь экран с вкладками персонажей"""
    inventory = get_inventory()
    
    if not players:
        return

    current_tab = 0

    while True:
        try:
            height, width = stdscr.getmaxyx()
            stdscr.clear()

            # Заголовок инвентаря
            stdscr.addstr(0, width // 2 - 8, "🎒 ИНВЕНТАРЬ",
                         get_color_pair(COLOR_CYAN) | curses.A_BOLD)
            stdscr.addstr(1, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # Вкладки с именами персонажей
            tab_x = 2
            for i, player in enumerate(players):
                if i == current_tab:
                    # Активная вкладка
                    stdscr.attron(get_color_pair(COLOR_CYAN) | curses.A_BOLD)
                    stdscr.addstr(2, tab_x, f" [{player.name}] ")
                    stdscr.attroff(get_color_pair(COLOR_CYAN) | curses.A_BOLD)
                else:
                    # Неактивная вкладка
                    stdscr.attron(get_color_pair(COLOR_WHITE))
                    stdscr.addstr(2, tab_x, f" {player.name} ")
                    stdscr.attroff(get_color_pair(COLOR_WHITE))
                tab_x += len(player.name) + 4

            stdscr.addstr(3, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # Отображение характеристик текущего персонажа
            current_player = players[current_tab]
            
            # === БЛОК 1: ХАРАКТЕРИСТИКИ ТЕКУЩЕГО ГЕРОЯ ===
            display_hero_stats_in_inventory(stdscr, current_player, 4, 2, width - 4)

            # === БЛОК 2: ИНВЕНТАРЬ ===
            inventory_start_y = 11

            stdscr.addstr(inventory_start_y, 2, "🧳 ИНВЕНТАРЬ",
                         get_color_pair(COLOR_MAGENTA) | curses.A_BOLD)
            stdscr.addstr(inventory_start_y + 1, 0, "─" * (width - 1),
                         get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # Отображение предметов
            item_objects = inventory.get_all_items() if hasattr(inventory, 'get_all_items') else {}
            item_y = inventory_start_y + 3
            item_index = 0

            for item_object, quantity in item_objects.items():
                if item_y + item_index >= height - 3:
                    break

                try:
                    template, elements = item_object.get_detailed_display_template()
                    quantity_text = f" х{quantity}" if quantity > 1 else ""

                    current_x = 4
                    stdscr.addstr(item_y + item_index, current_x, "◦ ", get_color_pair(COLOR_WHITE))
                    current_x += 2

                    for text, color in elements:
                        if current_x < width - 4:
                            stdscr.addstr(item_y + item_index, current_x, text, get_color_pair(color))
                            current_x += len(text)

                    if quantity_text and current_x < width - 4:
                        stdscr.addstr(item_y + item_index, current_x, quantity_text, get_color_pair(COLOR_GRAY))
                        current_x += len(quantity_text)

                    properties = item_object.get_all_properties()
                    if properties:
                        prop_parts = []
                        for prop_name, prop_value in properties.items():
                            if prop_value > 0:
                                readable_name = prop_name.replace('_bonus', '').replace('_', ' ').title()
                                prop_parts.append(f"{readable_name}: {prop_value}")

                        if prop_parts:
                            prop_text = " [" + ", ".join(prop_parts) + "]"
                            if current_x < width - 4 and len(prop_text) <= width - current_x - 4:
                                stdscr.addstr(item_y + item_index, current_x, prop_text, get_color_pair(COLOR_GRAY))

                    item_index += 1
                except Exception:
                    item_name = getattr(item_object, 'name', str(item_object))
                    stdscr.addstr(item_y + item_index, 4, f"◦ {item_name}: {quantity}",
                                 get_color_pair(COLOR_WHITE))
                    item_index += 1

            if item_index == 0:
                stdscr.addstr(inventory_start_y + 3, 4, "Инвентарь пуст", get_color_pair(COLOR_GRAY))

            # Подсказка по клавишам внизу
            INVENTORY_HINTS.display_hints(stdscr)

            stdscr.refresh()

            # Обработка ввода
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_LEFT:
                current_tab = (current_tab - 1) % len(players)
            elif key == curses.KEY_RIGHT:
                current_tab = (current_tab + 1) % len(players)
            elif key == curses.KEY_RESIZE:
                continue
            elif key != -1:
                try:
                    char = chr(key).lower()
                    if char in ['q', 'e']:  # q, exit
                        break
                except:
                    pass
                if key in [10, 13]:  # Enter
                    pass

        except curses.error:
            pass  # Защита от ошибок curses при ресайзе или переполнении


def display_hero_stats_in_inventory(stdscr, player, y, x, max_width):
    """Отображает характеристики героя в инвентаре (без баров, только текст)"""
    try:
        height, width = stdscr.getmaxyx()

        hp_text = f"HP: {player.hp}/{player.derived_stats.max_hp}"
        energy_text = f"Энергия: {player.energy}/{player.derived_stats.max_energy}"

        # Заголовок с HP и Энергией
        stdscr.addstr(y, x, "👥 ХАРАКТЕРИСТИКИ ГЕРОЯ", get_color_pair(COLOR_YELLOW) | curses.A_BOLD)
        stdscr.addstr(y, x + 30, f"{hp_text}  {energy_text}", get_color_pair(COLOR_CYAN) | curses.A_BOLD)

        # Фиксированные позиции для колонок (увеличенные отступы)
        label_col_x = x          # Колонка меток
        value_col_x = x + 18     # Колонка значений (увеличено с 15 до 18)
        stat_label_col_x = x + 28 # Колонка меток доп. характеристик (увеличено с 25 до 28)
        stat_value_col_x = x + 42 # Колонка значений доп. характеристик (увеличено с 35 до 42)
        equip_col_x = x + 55     # Колонка экипировки (увеличено с 50 до 55)

        # === Основные характеристики ===
        # Уровень
        stdscr.addstr(y + 1, label_col_x, "Уровень:", get_color_pair(COLOR_WHITE))
        level_value = str(getattr(player, 'level', 'N/A'))
        stdscr.addstr(y + 1, value_col_x, level_value, get_color_pair(COLOR_YELLOW))

        # Опыт
        stdscr.addstr(y + 2, label_col_x, "Опыт:", get_color_pair(COLOR_WHITE))
        if hasattr(player, 'exp'):
            exp_value = str(player.exp)
            if hasattr(player, 'exp_to_next_level'):
                exp_value += f"/{player.exp_to_next_level}"
        else:
            exp_value = 'N/A'
        stdscr.addstr(y + 2, value_col_x, exp_value, get_color_pair(COLOR_YELLOW))

        # Атака
        stdscr.addstr(y + 3, label_col_x, "Атака:", get_color_pair(COLOR_WHITE))
        attack_value = str(getattr(player.derived_stats, 'attack', 'N/A'))
        stdscr.addstr(y + 3, value_col_x, attack_value, get_color_pair(COLOR_YELLOW))

        # Защита
        stdscr.addstr(y + 4, label_col_x, "Защита:", get_color_pair(COLOR_WHITE))
        defense_value = str(getattr(player.derived_stats, 'defense', 'N/A'))
        stdscr.addstr(y + 4, value_col_x, defense_value, get_color_pair(COLOR_YELLOW))

        # === Дополнительные характеристики ===
        stats = getattr(player, 'stats', None)
        
        # Сила
        stdscr.addstr(y + 1, stat_label_col_x, "Сила:", get_color_pair(COLOR_WHITE))
        strength_value = str(getattr(stats, 'strength', 'N/A')) if stats else 'N/A'
        stdscr.addstr(y + 1, stat_value_col_x, strength_value, get_color_pair(COLOR_YELLOW))

        # Ловкость
        stdscr.addstr(y + 2, stat_label_col_x, "Ловкость:", get_color_pair(COLOR_WHITE))
        dexterity_value = str(getattr(stats, 'dexterity', 'N/A')) if stats else 'N/A'
        stdscr.addstr(y + 2, stat_value_col_x, dexterity_value, get_color_pair(COLOR_YELLOW))

        # Интеллект
        stdscr.addstr(y + 3, stat_label_col_x, "Интеллект:", get_color_pair(COLOR_WHITE))
        intelligence_value = str(getattr(stats, 'intelligence', 'N/A')) if stats else 'N/A'
        stdscr.addstr(y + 3, stat_value_col_x, intelligence_value, get_color_pair(COLOR_YELLOW))

        # Выносливость
        stdscr.addstr(y + 4, stat_label_col_x, "Выносливость:", get_color_pair(COLOR_WHITE))
        constitution_value = str(getattr(stats, 'constitution', 'N/A')) if stats else 'N/A'
        stdscr.addstr(y + 4, stat_value_col_x, constitution_value, get_color_pair(COLOR_YELLOW))

        # === Экипировка ===
        stdscr.addstr(y + 1, equip_col_x, "Оружие: ---", get_color_pair(COLOR_GRAY))
        stdscr.addstr(y + 2, equip_col_x, "Броня: ---", get_color_pair(COLOR_GRAY))
        stdscr.addstr(y + 3, equip_col_x, "Аксессуар: ---", get_color_pair(COLOR_GRAY))
        stdscr.addstr(y + 4, equip_col_x, "Расходник: ---", get_color_pair(COLOR_GRAY))

        # Разделитель
        if y + 5 < height:
            separator_length = min(max_width - 4, width - x - 1)
            stdscr.addstr(y + 5, x, "─" * separator_length, get_color_pair(COLOR_GRAY) | curses.A_DIM)

    except curses.error:
        pass  # Игнорируем ошибки отрисовки