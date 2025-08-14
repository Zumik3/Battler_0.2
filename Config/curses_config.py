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

# Стили текста - инициализируются как None
BOLD_RED = None
BOLD_GREEN = None
BOLD_YELLOW = None
BOLD_BLUE = None
BOLD_MAGENTA = None
BOLD_CYAN = None
BOLD_WHITE = None
BOLD_GRAY = None

BOLD = None
UNDERLINE = None
NORMAL = None

# Настройки задержек
BATTLE_DELAY = 0.4  # Задержка между действиями в бою (секунды)
SCREEN_REFRESH_DELAY = 0.01  # Задержка при обновлении экрана (секунды)

def setup_colors():
    """Инициализация цветов для игры"""
    global BOLD_RED, BOLD_GREEN, BOLD_YELLOW, BOLD_BLUE, BOLD_MAGENTA, BOLD_CYAN, BOLD_WHITE, BOLD_GRAY
    global BOLD, UNDERLINE, NORMAL
    
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        
        # Инициализация цветовых пар
        curses.init_pair(1, curses.COLOR_RED, -1)     # Красный текст
        curses.init_pair(2, curses.COLOR_GREEN, -1)   # Зеленый текст
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Желтый текст
        curses.init_pair(4, curses.COLOR_BLUE, -1)    # Синий текст
        curses.init_pair(5, curses.COLOR_MAGENTA, -1) # Пурпурный текст
        curses.init_pair(6, curses.COLOR_CYAN, -1)    # Голубой текст
        curses.init_pair(7, curses.COLOR_WHITE, -1)   # Белый текст
        curses.init_pair(8, 8, -1)                    # Серый текст
        
        # Инициализация стилей
        BOLD_RED = curses.color_pair(1) | curses.A_BOLD
        BOLD_GREEN = curses.color_pair(2) | curses.A_BOLD
        BOLD_YELLOW = curses.color_pair(3) | curses.A_BOLD
        BOLD_BLUE = curses.color_pair(4) | curses.A_BOLD
        BOLD_MAGENTA = curses.color_pair(5) | curses.A_BOLD
        BOLD_CYAN = curses.color_pair(6) | curses.A_BOLD
        BOLD_WHITE = curses.color_pair(7) | curses.A_BOLD
        BOLD_GRAY = curses.color_pair(8) | curses.A_BOLD
        
        BOLD = curses.A_BOLD
        UNDERLINE = curses.A_UNDERLINE
        NORMAL = curses.A_NORMAL
       
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