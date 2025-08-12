# Utils/test_window.py - Тестовое окно с вкладками

import curses
from Battle.battle_logger import battle_logger

def show_test_button_window(stdscr):
    """
    Открывает тестовое окно с вкладками.
    Переключение вкладок стрелками влево/вправо.
    Окно закрывается по кнопке "Закрыть" или клавише Q.
    """
    if not stdscr:
        battle_logger.log_system_message("❌ Невозможно открыть тестовое окно")
        return False
    
    try:
        # Создаем новое окно
        height, width = 20, 60
        start_y, start_x = 3, 10
        win = curses.newwin(height, width, start_y, start_x)
        
        # Включаем поддержку функциональных клавиш (включая стрелки)
        win.keypad(True)
        
        # Инициализация цветов
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Активная вкладка
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Неактивная вкладка
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Содержимое
        
        # Данные вкладок
        tabs = ["Главная", "Настройки", "Информация"]
        current_tab = 0
        
        # Содержимое для каждой вкладки
        tab_content = {
            0: [
                "Добро пожаловать в тестовое окно!",
                "",
                "Это главная вкладка.",
                "Используйте стрелки ← → для переключения вкладок",
                "Нажмите Q или кнопку 'Закрыть' для выхода",
                "",
                "Вкладки позволяют организовать информацию",
                "по различным категориям."
            ],
            1: [
                "Настройки приложения",
                "",
                "• Тема интерфейса: Светлая",
                "• Размер шрифта: Средний", 
                "• Автосохранение: Включено",
                "• Уведомления: Включены",
                "",
                "Настройки можно изменять в этом разделе.",
                "Все изменения применяются сразу."
            ],
            2: [
                "Информация о приложении",
                "",
                "Версия: 1.0.0",
                "Разработчик: Тестовый проект",
                "Лицензия: MIT",
                "",
                "Это демонстрационное приложение",
                "для тестирования интерфейса curses.",
                "",
                "Поддерживаемые функции:",
                "• Вкладки с навигацией",
                "• Цветное оформление",
                "• Адаптивный интерфейс"
            ]
        }
        
        # Флаг для закрытия окна
        should_close = False
        
        while not should_close:
            # Очищаем окно
            win.clear()
            
            # Рисуем рамку
            win.border()
            win.addstr(1, 2, "Тестовое окно с вкладками", curses.A_BOLD)
            
            # Отображение вкладок
            x_pos = 2
            for i, tab_name in enumerate(tabs):
                if i == current_tab:
                    # Активная вкладка
                    win.attron(curses.color_pair(1))
                    win.addstr(2, x_pos, f" [{tab_name}] ")
                    win.attroff(curses.color_pair(1))
                else:
                    # Неактивная вкладка
                    win.attron(curses.color_pair(2))
                    win.addstr(2, x_pos, f" [{tab_name}] ")
                    win.attroff(curses.color_pair(2))
                x_pos += len(tab_name) + 4
            
            # Отображение содержимого текущей вкладки
            win.attron(curses.color_pair(3))
            content = tab_content[current_tab]
            for i, line in enumerate(content):
                if 4 + i < height - 3:  # Проверка на выход за границы экрана
                    win.addstr(4 + i, 2, line)
            
            # Кнопка закрытия
            win.addstr(height - 2, width - 12, "[ Закрыть ]", curses.A_REVERSE)
            win.attroff(curses.color_pair(3))
            
            # Инструкции
            win.addstr(height - 2, 2, "← → : вкладки")
            win.addstr(height - 1, 2, "Q : выход")
            
            win.refresh()
            
            # Ждем ввод
            key = win.getch()
            
            if key == ord('q') or key == ord('Q'):
                should_close = True
            elif key == curses.KEY_LEFT:
                current_tab = (current_tab - 1) % len(tabs)
            elif key == curses.KEY_RIGHT:
                current_tab = (current_tab + 1) % len(tabs)
            elif key == ord(' '):  # Пробел на кнопке закрытия
                # Проверяем клик по кнопке закрытия (упрощенная проверка)
                should_close = True
                
    except Exception as e:
        battle_logger.log_system_message(f"❌ Ошибка в тестовом окне: {str(e)}")
        return False
    finally:
        # Отключаем keypad
        win.keypad(False)
        # Обновляем основной экран
        stdscr.refresh()
        
    return True