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
    COLOR_YELLOW  # Добавлен для использования в заголовке "ГЕРОИ"
)
from Inventory.inventory import get_inventory
from Utils.UI.draw_character import DrawCharacter  # Импортируем наш новый класс


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
        stdscr.addstr(0, width // 2 - 10, "YET ANOTHER AUTOBATTLER", get_color_pair(COLOR_CYAN) | curses.A_BOLD)
        inventory = get_inventory()
        stdscr.addstr(1, 2, f"Золото: {inventory.get_gold()}", get_color_pair(COLOR_GRAY))
        stdscr.addstr(2, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

        # === ОБЛАСТЬ ПЕРСОНАЖЕЙ ===
        display_characters(stdscr, command_handler.players, command_handler.enemies, width, height)

        # === ОБЛАСТЬ ЛОГА ===
        log_start_y = 9
        stdscr.addstr(log_start_y, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
        stdscr.addstr(log_start_y + 1, 2, "📜 ЛОГ БОЯ:", get_color_pair(COLOR_WHITE) | curses.A_BOLD)
        display_log(stdscr, width, height, log_start_y)

        # === ОБЛАСТЬ ВВОДА ===
        input_y = height - 2
        stdscr.addstr(input_y, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
        stdscr.addstr(input_y + 1, 0, f"❱ {input_str}", get_color_pair(COLOR_WHITE) | curses.A_BOLD)

    except curses.error:
        pass  # Игнорируем ошибки отрисовки (например, при ресайзе)


def display_characters(stdscr, players, enemies, width, height):
    """Отображает персонажей на экране с помощью DrawCharacter"""
    mid_x = width // 2

    # Заголовок игроков
    stdscr.addstr(4, 2, "🧍 Герои:", curses.A_BOLD)

    # Отрисовка игроков
    for i, char in enumerate(players):
        y = 5 + i
        x = 4
        DrawCharacter.draw_character_row(stdscr, char, y, x, is_player=True)

    # Заголовок врагов
    stdscr.addstr(4, mid_x + 2, "🎲 Событие:", curses.A_BOLD)

    # Отрисовка врагов
    for i, char in enumerate(enemies):
        y = 6 + i
        x = mid_x + 4
        DrawCharacter.draw_character_row(stdscr, char, y, x, is_player=False)


def display_log(stdscr, width, height, log_start_y):
    """Отображает лог боя"""
    log_height = height - log_start_y - 5
    log_lines = battle_logger.get_lines()

    if log_lines:
        visible_log_lines = log_lines[-log_height:] if len(log_lines) > log_height else log_lines
        for i, line in enumerate(visible_log_lines):
            if log_start_y + 2 + i >= height - 3:
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
    """Отображает экран инвентаря на весь экран"""
    inventory = get_inventory()

    while True:
        try:
            height, width = stdscr.getmaxyx()
            stdscr.clear()

            # Заголовок инвентаря
            stdscr.addstr(0, width // 2 - 8, "🎒 ИНВЕНТАРЬ",
                         get_color_pair(COLOR_CYAN) | curses.A_BOLD)
            stdscr.addstr(1, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # === БЛОК 1: ХАРАКТЕРИСТИКИ ГЕРОЕВ (2 в ряд) ===
            stdscr.addstr(2, 2, "👥 ГЕРОИ",
                         get_color_pair(COLOR_YELLOW) | curses.A_BOLD)  # Теперь COLOR_YELLOW доступен
            stdscr.addstr(3, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            heroes_per_row = 2
            hero_width = width // heroes_per_row - 2
            max_hero_rows = 0

            for i, player in enumerate(players):
                row = i // heroes_per_row
                col = i % heroes_per_row

                hero_x = col * hero_width + 2
                hero_y = 4 + row * 6
                max_hero_rows = max(max_hero_rows, row + 1)

                if hero_y + 5 < height - 4:
                    display_hero_stats_in_inventory(stdscr, player, hero_y, hero_x, hero_width)

            # === БЛОК 2: ИНВЕНТАРЬ ===
            inventory_start_y = 4 + max_hero_rows * 6
            if len(players) == 0:
                inventory_start_y = 4

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

            # Подсказка выхода
            stdscr.addstr(height - 2, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
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
        height, width = stdscr.getmaxyx()  # ✅ Теперь переменные определены

        name = player.name[:20] if len(player.name) > 20 else player.name
        hp_text = f"HP: {player.hp}/{player.derived_stats.max_hp}"
        energy_text = f"Энергия: {player.energy}/{player.derived_stats.max_energy}"

        # Первая строка: имя + HP + Energy
        stdscr.addstr(y, x, name, get_color_pair(COLOR_GREEN) | curses.A_BOLD)
        stdscr.addstr(y, x + len(name), f" {hp_text}  {energy_text}", get_color_pair(COLOR_CYAN) | curses.A_BOLD)

        # Левая колонка
        left_x = x
        level_text = f"Уровень: {getattr(player, 'level', 'N/A')}"
        stdscr.addstr(y + 1, left_x, level_text)

        if hasattr(player, 'exp'):
            exp_text = f"Опыт: {player.exp}"
            if hasattr(player, 'exp_to_next_level'):
                exp_text += f"/{player.exp_to_next_level}"
            stdscr.addstr(y + 2, left_x, exp_text)

        attack_text = f"Атака: {getattr(player.derived_stats, 'attack', 'N/A')}"
        stdscr.addstr(y + 3, left_x, attack_text)

        defense_text = f"Защита: {getattr(player.derived_stats, 'defense', 'N/A')}"
        stdscr.addstr(y + 4, left_x, defense_text)

        # Правая колонка
        right_x = x + max_width // 2
        stats = getattr(player, 'stats', None)
        if stats:
            if hasattr(stats, 'strength'):
                stdscr.addstr(y + 1, right_x, f"Сила: {stats.strength}")
            if hasattr(stats, 'dexterity'):
                stdscr.addstr(y + 2, right_x, f"Ловкость: {stats.dexterity}")
            if hasattr(stats, 'intelligence'):
                stdscr.addstr(y + 3, right_x, f"Интеллект: {stats.intelligence}")
            if hasattr(stats, 'constitution'):
                stdscr.addstr(y + 4, right_x, f"Выносливость: {stats.constitution}")

        # Разделитель
        if y + 5 < height:
            separator_length = min(max_width - 4, width - x - 1)
            stdscr.addstr(y + 5, x, "─" * separator_length, get_color_pair(COLOR_GRAY) | curses.A_DIM)

    except curses.error:
        pass  # Игнорируем ошибки отрисовки