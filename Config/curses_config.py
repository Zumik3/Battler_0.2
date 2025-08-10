# Config/curses_config.py - Простые настройки curses

import curses

# Цветовые константы
COLOR_RED = 1
COLOR_GREEN = 2
COLOR_YELLOW = 3
COLOR_BLUE = 4
COLOR_MAGENTA = 5
COLOR_CYAN = 6
COLOR_WHITE = 7
COLOR_GRAY = 8

# Настройки задержек
BATTLE_DELAY = 0.4  # Задержка между действиями в бою (секунды)
SCREEN_REFRESH_DELAY = 0.01  # Задержка при обновлении экрана (секунды)

def setup_colors():
    """Инициализация цветов для игры"""
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        
        curses.init_pair(1, curses.COLOR_RED, -1)     # Красный текст
        curses.init_pair(2, curses.COLOR_GREEN, -1)   # Зеленый текст
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Желтый текст
        curses.init_pair(4, curses.COLOR_BLUE, -1)    # Синий текст
        curses.init_pair(5, curses.COLOR_MAGENTA, -1) # Пурпурный текст
        curses.init_pair(6, curses.COLOR_CYAN, -1)    # Голубой текст
        curses.init_pair(7, curses.COLOR_WHITE, -1)   # Белый текст
        curses.init_pair(8, 8, -1)                    # Серый текст

        # Инициализация цветовых пар
        #curses.init_pair(COLOR_TITLE, 1, -1)      # Заголовок (синий)
        #curses.init_pair(COLOR_PLAYER, 2, -1)     # Игроки (зеленый)
        #curses.init_pair(COLOR_ENEMY, 3, -1)      # Враги (красный)
        #curses.init_pair(COLOR_LOG, 7, -1)        # Лог (белый)
        #curses.init_pair(COLOR_INPUT, 15, -1)     # Ввод (ярко-белый)
        #curses.init_pair(COLOR_HIGHLIGHT, 6, -1)  # Выделенный текст (желтый)
        #curses.init_pair(COLOR_BORDER, 8, -1)     # Для границ (серый)
        
        return True
    return False

def setup_screen(stdscr):
    """Базовая настройка экрана"""
    curses.curs_set(0)  # Скрыть курсор
    setup_colors()
    stdscr.clear()
    stdscr.bkgd(' ', curses.color_pair(COLOR_WHITE))
    stdscr.refresh()

def get_color_pair(color_id):
    """Получение цветовой пары по ID"""
    return curses.color_pair(color_id)