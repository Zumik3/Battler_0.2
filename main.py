# main.py
import curses
from Battle.battle_logger import battle_logger
from Utils.commands import CommandHandler
from Utils.display import update_display, create_screen_observer
from Config.curses_config import setup_screen
from Characters.char_utils import create_player_team
from Inventory.inventory import get_inventory

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
    

    # Инициализационные сообщения
    battle_logger.log_system_message("🎮 Добро пожаловать в автобаттлер!")
    battle_logger.log_system_message("Введите 'help' для списка команд")
    
    try:
        # Основной цикл
        while True:
            # Обновляем экран для отображения ввода
            update_display(stdscr, command_handler)
            
            # Обработка ввода
            try:
                key = stdscr.get_wch()
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