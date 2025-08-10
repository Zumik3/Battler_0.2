# progress_bar.py - Универсальная система прогресс-баров

import curses
from Config.game_config import PROGRESS_BORDER_CHARS, PROGRESS_BAR_CHARS, HP_BAR_WIDTH, BASE_ENERGY_COST
from Config.curses_config import *

def draw_progress_bar(stdscr, y, x, current_value, max_value, bar_width, 
                     bar_color=None, show_percent=False, show_values=False,
                     border_chars=PROGRESS_BORDER_CHARS, bar_chars=PROGRESS_BAR_CHARS):
    """
    Универсальная функция для отрисовки прогресс-бара.
    
    :param stdscr: Окно curses для отрисовки
    :param y: Координата Y
    :param x: Координата X
    :param current_value: Текущее значение
    :param max_value: Максимальное значение
    :param bar_width: Ширина бара в символах
    :param bar_color: Цвет бара (если None, используется цвет по умолчанию)
    :param show_percent: Показывать ли проценты
    :param show_values: Показывать ли значения (current/max)
    :param border_chars: Символы для границ (левая/правая)
    :param bar_chars: Символы для заполненного/пустого бара
    """
    
    # Проверка корректности значений
    if max_value <= 0:
        ratio = 0
    else:
        ratio = max(0, min(1, current_value / max_value))
    
    # Рассчитываем заполненную часть
    filled_width = int(ratio * bar_width)
    
    # Гарантируем хотя бы один квадратик, если значение > 0
    if current_value > 0 and filled_width == 0 and bar_width > 0:
        filled_width = 1
    
    filled_width = max(0, min(filled_width, bar_width))
    
    # Создаем строку бара
    filled_char = bar_chars[0]
    empty_char = bar_chars[1]
    
    bar = filled_char * filled_width + empty_char * (bar_width - filled_width)
    
    # Определяем цвет бара
    if bar_color is None:
        # Автоматический выбор цвета по проценту
        if current_value <= 0:
            bar_color = curses.color_pair(COLOR_RED)  # Красный
        elif ratio > 0.75:
            bar_color = curses.color_pair(COLOR_GREEN)  # Зелёный
        elif ratio > 0.25:
            bar_color = curses.color_pair(COLOR_YELLOW)
        else:
            bar_color = curses.color_pair(1)  # Красный
    elif isinstance(bar_color, int):
        # Если передан номер цветовой пары
        bar_color = curses.color_pair(bar_color)
    
    # Рисуем границы и бар
    left_border = border_chars[0]
    right_border = border_chars[1]
    
    try:
        # Левая граница
        stdscr.addstr(y, x, left_border, curses.color_pair(COLOR_GRAY))
        # Бар
        stdscr.addstr(y, x + 1, bar, bar_color)
        # Правая граница
        stdscr.addstr(y, x + 1 + bar_width, right_border, curses.color_pair(COLOR_GRAY))
        
        # Добавляем текстовую информацию
        text_parts = []
        if show_percent:
            percent = int(ratio * 100)
            text_parts.append(f"{percent}%")
        if show_values:
            text_parts.append(f"{current_value}/{max_value}")
        
        if text_parts:
            text = " " + " ".join(text_parts)
            stdscr.addstr(y, x + 1 + bar_width + 1, text, COLOR_GRAY)
            
    except curses.error:
        # Игнорируем ошибки отрисовки
        pass

def draw_energy_bar(stdscr, y, x, current_energy, max_energy, bar_width=None):
    """
    Функция для отрисовки энергетического бара.
    Если энергии меньше 10, показывает пустой бар.
    
    :param stdscr: Окно curses для отрисовки
    :param y: Координата Y
    :param x: Координата X
    :param current_energy: Текущая энергия
    :param max_energy: Максимальная энергия
    :param bar_width: Ширина бара (если None, берется из Config)
    """
    if bar_width is None:
        bar_width = HP_BAR_WIDTH
    
    # Если энергии меньше 10, показываем пустой бар
    if current_energy < BASE_ENERGY_COST:
        current_energy = 0
    
    energy_color = curses.color_pair(4)

    draw_progress_bar(
        stdscr=stdscr,
        y=y,
        x=x,
        current_value=current_energy,
        max_value=max_energy,
        bar_width=bar_width,
        bar_color=energy_color,
        show_percent=False,
        show_values=False
    )