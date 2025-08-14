# main.py
import curses
# Импортируем новый класс точки входа
from Utils.UI.main_window import MainWindow
# Импорты для инициализации
from Config.curses_config import setup_screen
from Characters.char_utils import create_player_team
from Inventory.inventory import get_inventory

def main(stdscr):
    # Базовая настройка экрана
    setup_screen(stdscr)

    # Данные для отображения
    players = create_player_team()
    # enemies инициализируются внутри EventWindow/CommandHandler

    inventory = get_inventory()

    # Создаем и запускаем главное окно
    # Оно само выполнит всю необходимую инициализацию и запустит EventWindow
    main_window = MainWindow(stdscr, players)
    main_window.run()

    # Очистка ресурсов происходит внутри EventWindow.run()

if __name__ == "__main__":
    curses.wrapper(main)


'''
def main(stdscr):
    # Базовая настройка экрана
    setup_screen(stdscr)
    
    # Данные для отображения
    players = create_player_team()
    enemies = []

    # Добавление золота
    inventory = get_inventory()
    inventory.add_gold(100)

    # Создаем обработчик команд
    command_handler = CommandHandler(players, enemies, stdscr)
    
    # Создаем и регистрируем наблюдателя
    screen_observer = create_screen_observer(stdscr, command_handler)
    battle_logger.add_observer(screen_observer)
    
    # Включаем режим получения одиночных нажатий клавиш
    stdscr.nodelay(False)  # Блокирующий режим
    stdscr.keypad(True)    # Включаем поддержку специальных клавиш

    # Инициализационные сообщения
    battle_logger.log_system_message("🎮 Добро пожаловать в автобаттлер!")
    battle_logger.log_system_message("Нажмите 'H' для помощи или 'Enter' для начала боя")
    
    try:
        # Основной цикл
        while True:
            # Обновляем экран для отображения
            update_display(stdscr, command_handler)
            stdscr.refresh()
            
            # Обработка ввода
            try:
                key = stdscr.getch()  # Используем getch() вместо get_wch() для лучшей совместимости
                result = command_handler.process_input(key)
                if result is True:  # Нужно выйти
                    break
            except:
                continue
                
    finally:
        # Удаляем наблюдателя при выходе
        battle_logger.remove_observer(screen_observer)

if __name__ == "__main__":
    curses.wrapper(main)
'''