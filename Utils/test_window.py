# Utils/test_window.py - Тестовое окно с кнопками

import curses
from Battle.battle_logger import battle_logger

def show_test_button_window(stdscr):
    """
    Открывает тестовое окно с кнопками.
    При клике на кнопку сообщение "test" выводится в область сообщений.
    Окно закрывается по кнопке "Закрыть".
    """
    if not stdscr:
        battle_logger.log_system_message("❌ Невозможно открыть тестовое окно")
        return False
    
    try:
        # Создаем новое окно
        height, width = 15, 50
        start_y, start_x = 5, 10
        win = curses.newwin(height, width, start_y, start_x)
        
        # Включаем поддержку мыши - минимально
        curses.mousemask(curses.BUTTON1_CLICKED)
        
        # Определяем позиции кнопок
        button1_y, button1_x = 5, 5
        button2_y, button2_x = 8, 5
        close_button_y, close_button_x = 3, 35
        button1_text = "Кнопка 1"
        button2_text = "Кнопка 2"
        close_button_text = "Закрыть"
        
        # Список сообщений
        messages = []
        max_messages = 5  # Максимум сообщений для отображения
        
        # Флаг для закрытия окна
        should_close = False
        
        while not should_close:
            # Очищаем окно
            win.clear()
            
            # Рисуем рамку
            win.border()
            win.addstr(1, 2, "Тестовое окно с кнопками", curses.A_BOLD)
            win.addstr(2, 2, "Кликните на кнопки мышкой", curses.A_DIM)
            
            # Рисуем кнопки
            win.addstr(button1_y, button1_x, button1_text, curses.A_REVERSE)
            win.addstr(button2_y, button2_x, button2_text, curses.A_REVERSE)
            win.addstr(close_button_y, close_button_x, close_button_text, curses.A_REVERSE)
            
            # Рисуем область для сообщений
            win.addstr(11, 2, "Сообщения:", curses.A_BOLD)
            win.hline(12, 1, curses.ACS_HLINE, width - 2)  # Горизонтальная линия
            
            # Отображаем сообщения
            msg_start_y = 13
            for i, msg in enumerate(messages[-max_messages:]):  # Показываем последние сообщения
                if msg_start_y + i < height - 1:  # Не выходим за границы окна
                    win.addstr(msg_start_y + i, 2, msg)
            
            win.refresh()
            
            # Ждем ввод
            key = win.getch()
            
            if key == curses.KEY_MOUSE:
                # Обрабатываем событие мыши очень осторожно
                try:
                    # Получаем событие мыши
                    mouse_event = curses.getmouse()
                    if mouse_event:
                        mouse_id, mouse_x, mouse_y, mouse_z, mouse_state = mouse_event
                        
                        # Проверяем, что это клик левой кнопкой
                        if mouse_state & curses.BUTTON1_CLICKED:
                            # Преобразуем координаты в локальные
                            local_y = mouse_y - start_y
                            local_x = mouse_x - start_x
                            
                            # Проверка клика по первой кнопке
                            if (local_y == button1_y and 
                                button1_x <= local_x < button1_x + len(button1_text)):
                                messages.append("test")
                            
                            # Проверка клика по второй кнопке
                            elif (local_y == button2_y and 
                                  button2_x <= local_x < button2_x + len(button2_text)):
                                messages.append("test")
                            
                            # Проверка клика по кнопке закрытия
                            elif (local_y == close_button_y and 
                                  close_button_x <= local_x < close_button_x + len(close_button_text)):
                                should_close = True
                                
                except Exception:
                    # Любые ошибки при обработке мыши - игнорируем
                    pass
            # Все остальное игнорируем - окно не закрывается
            
    except Exception as e:
        battle_logger.log_system_message(f"❌ Ошибка в тестовом окне: {str(e)}")
        return False
    finally:
        # Отключаем мышь
        curses.mousemask(0)
        # Обновляем основной экран
        stdscr.refresh()
        
    return True