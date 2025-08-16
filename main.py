# main.py
"""Главная точка входа в игру. Инициализирует curses и запускает игровой цикл."""
import curses
import sys
import os

# - Импорты проекта -
from Config.curses_config import setup_screen
# from Utils.display import create_screen_observer # УДАЛЯЕМ, если не используется напрямую в main
from Characters.char_utils import create_player_team
from Battle.battle_logger import battle_logger
from Utils.GameState.context import GameContext # Импортируем новый GameContext

# Импортируем обработчик команд
from Utils.command_handler import CommandHandler, command_handler # Импортируем CommandHandler и его глобальную переменную

def main(stdscr: curses.window) -> None:
    """Основная функция, запускаемая curses.wrapper.
    Инициализирует игру и запускает основной цикл через GameContext.
    """
    try:
        # 1. Инициализация curses
        setup_screen(stdscr)

        # 2. Создание начальных данных игры
        players = create_player_team()
        if not players:
            battle_logger.log_system_message("❌ Ошибка: Не удалось создать команду игроков!")
            return
        enemies = [] # Враги создаются в EventState

        # 3. Инициализация глобального CommandHandler
        # Это необходимо для совместимости с screen_observer или других частей кода,
        # которые полагаются на глобальный экземпляр.
        global command_handler
        command_handler = CommandHandler(players, enemies, stdscr)

        # 4. Создание и настройка наблюдателя экрана (если используется)
        # ВАЖНО: Убедитесь, что screen_observer совместим с новой системой
        # или отключите его, если он мешает.
        # screen_observer = create_screen_observer(stdscr, command_handler)
        # battle_logger.add_observer(screen_observer)

        # 5. Создание и запуск контекста игры
        game_context = GameContext(stdscr, players, enemies)
        game_context.run()

        # - Финализация -
        # Удаление наблюдателя (если был добавлен)
        # try:
        #     battle_logger.remove_observer(screen_observer)
        # except Exception:
        #     pass

    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_msg = f"💥 Критическая ошибка в main: {e}"
        try:
            battle_logger.log_system_message(error_msg)
        except:
            print(error_msg, file=sys.stderr)
    finally:
        # Финализация (если требуется)
        # try:
        #     battle_logger.remove_observer(screen_observer) # Если observer добавлялся глобально
        # except Exception:
        #     pass
        pass

if __name__ == "__main__":
    curses.wrapper(main)
