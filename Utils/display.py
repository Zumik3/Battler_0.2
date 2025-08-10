# display.py - Логика отображения и обновления экрана

import curses
from Battle.battle_logger import battle_logger
from Config.curses_config import *
from Config.game_config import NAME_COLUMN_WIDTH, HP_BAR_WIDTH, ENERGY_BAR_WIDTH
from Characters.char_utils import draw_character_name
from Utils.progress_bar import draw_progress_bar, draw_energy_bar
from Inventory.inventory import get_inventory


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
        
        #stdscr.refresh()
        
    except curses.error:
        pass

def create_screen_observer(stdscr, command_handler):
    """Создает наблюдателя для автоматического обновления экрана"""
    def screen_observer(message):
        update_display(stdscr, command_handler)  # Пустая строка для ввода во время боя
        stdscr.refresh()
    return screen_observer

def display_characters(stdscr, players, enemies, width, height):
    # Левая часть - игроки
    mid_x = width // 2
    #top_height = min(Config.MIN_TOP_HEIGHT, height // 3)
    #log_y = top_height + 2
    stdscr.addstr(4, 2, "🧍 Команда приключенцев:", curses.A_BOLD)
    #stdscr.addstr(5, 2, "─" * (mid_x - 4), curses.A_DIM)
    for i, char in enumerate(players):
        color = COLOR_GREEN if char.alive else COLOR_RED
        draw_character_name(stdscr, 5 + i, 4, char, color)
        # Рисуем HP-бар
        bar_x = 4 + NAME_COLUMN_WIDTH + 1
        draw_progress_bar(
            stdscr=stdscr,
            y=5 + i,
            x=bar_x,
            current_value=char.hp,
            max_value=char.max_hp,
            bar_width=HP_BAR_WIDTH
        )
        # Рисуем энергетический бар (только для игроков)
        energy_bar_x = bar_x + HP_BAR_WIDTH + 2
        draw_energy_bar(
            stdscr=stdscr,
            y=5 + i,
            x=energy_bar_x,
            current_energy=char.energy,
            max_energy=char.max_energy,
            bar_width=ENERGY_BAR_WIDTH
        )
    
    # === Враги ===
    stdscr.addstr(4, mid_x + 2, "👹 Враги:", curses.A_BOLD)
    for i, char in enumerate(enemies):
        color = COLOR_BLUE if char.alive else COLOR_RED
        draw_character_name(stdscr, 6 + i, mid_x + 4, char, color)
        # Рисуем HP-бар
        bar_x = mid_x + 4 + NAME_COLUMN_WIDTH + 1
        draw_progress_bar(
            stdscr=stdscr,
            y=6 + i,
            x=bar_x,
            current_value=char.hp,
            max_value=char.max_hp,
            bar_width=HP_BAR_WIDTH,
        )

def display_log(stdscr, width, height, log_start_y) -> None:
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

# Экспорт функций для удобства использования
#__all__ = ['update_display', 'create_screen_observer']