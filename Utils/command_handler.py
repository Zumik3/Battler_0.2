# Utils/command_handler.py
"""Обработчик команд пользователя.
Анализирует ввод (клавиши) и выполняет соответствующие действия или возвращает сигналы для управления состоянием игры.
"""
import curses
from typing import List, Union
# Импортируем Player напрямую, так как он используется в аннотациях типов
from Characters.player_classes import Player
# Импортируем battle_logger для логирования сообщений
from Battle.battle_logger import battle_logger
# Импортируем battle_simulator для запуска боя
from Battle.battle_simulator import BattleSimulator
# Импортируем inventory для работы с инвентарем
from Inventory.inventory import get_inventory

# === КОНСТАНТЫ ДЛЯ СИГНАЛОВ ===
# Эти константы определяют возможные результаты обработки команд
CMD_ACTION_NONE: str = "none"
CMD_ACTION_EXIT: str = "exit"
CMD_ACTION_START_BATTLE: str = "start_battle"
CMD_ACTION_OPEN_INVENTORY: str = "open_inventory"
CMD_ACTION_OPEN_SKILLS: str = "open_skills"
CMD_ACTION_OPEN_SHOP: str = "open_shop" # Добавлен сигнал для магазина
CMD_ACTION_SHOW_STATS: str = "open_stats" # Используем существующую константу для статистики
CMD_ACTION_SHOW_HELP: str = "show_help"
CMD_ACTION_CLEAR_LOG: str = "clear_log"

# Тип для возвращаемого значения process_input
# Может возвращать сигнал (строку) или True/False (булево) для совместимости
CommandResult = Union[str, bool]

class CommandHandler:
    """Обработчик команд. Адаптирован для работы с GameContext/GameState.
    Вместо прямого запуска окон, теперь возвращает сигналы о необходимых действиях.
    """
    def __init__(self, players: List[Player], enemies: List, stdscr: curses.window) -> None:
        """
        Инициализирует обработчик команд.
        Args:
            players: Список игроков.
            enemies: Список врагов.
            stdscr: Стандартное окно curses.
        """
        self.players: List[Player] = players
        self.enemies: List = enemies # TODO: Уточнить тип enemies, если станет известен
        self.stdscr: curses.window = stdscr
        # Убираем прямые ссылки на запуск окон из предыдущих версий
        # self.commands = {...} - этот словарь больше не нужен для прямого маппинга команд

    def process_input(self, key: int) -> str:
        """Обрабатывает ввод пользователя - теперь через одиночные клавиши.
        Возвращает сигнал действия, который интерпретируется в соответствующем состоянии.
        """
        # Обработка одиночных клавиш
        if key == ord('\n'): # Enter
            return self.start_battle() # Возвращаем сигнал
        elif key in [ord('i'), ord('I')]:
            return self.open_inventory() # Возвращаем сигнал
        elif key in [ord('s'), ord('S')]:
            return self.open_skills() # Возвращаем сигнал
        elif key in [ord('r'), ord('R')]:
             return self.open_shop() # Возвращаем сигнал
        elif key == curses.KEY_F12: # F12
            return self.open_statistics() # Возвращаем сигнал
        elif key in [ord('h'), ord('H')]:
            self.show_help() # Показываем помощь напрямую
            return CMD_ACTION_NONE # Нет перехода
        elif key in [ord('c'), ord('C')]:
            self.clear_log() # Очищаем лог напрямую
            return CMD_ACTION_NONE # Нет перехода
        elif key in [ord('q'), ord('Q'), 27]: # ESC
            return self.exit_game() # Возвращаем сигнал выхода
        else:
            # Неизвестная команда
            return CMD_ACTION_NONE # Игнорируем

    # - Методы, которые больше не запускают окна напрямую -
    def start_battle(self) -> str:
        """Сигнализирует о необходимости начать бой."""
        # Вся логика запуска боя теперь в EventState
        # Здесь просто возвращаем сигнал
        battle_logger.log_system_message("⚔️ Подготовка к бою...")
        # TODO: Добавить логику подготовки к бою, если нужно
        return CMD_ACTION_START_BATTLE

    def show_help(self) -> None:
        """Показывает помощь."""
        # Отображаем помощь напрямую в текущем состоянии
        battle_logger.log_system_message("ℹ️ Помощь: Используйте клавиши для навигации.")

    def clear_log(self) -> None:
        """Очищает лог."""
        battle_logger.clear_log()
        battle_logger.log_system_message("🗑️ Лог очищен")
        # Не возвращаем сигнал перехода

    def exit_game(self) -> str:
        """Сигнализирует о необходимости выйти из игры."""
        battle_logger.log_system_message("👋 До новых встреч!")
        return CMD_ACTION_EXIT

    # - Методы, которые больше не запускают окна -
    # Они теперь просто возвращают сигналы
    def open_inventory(self) -> str:
        """Сигнализирует о необходимости открыть инвентарь."""
        # TODO: Добавить логику подготовки к открытию инвентаря, если нужно
        return CMD_ACTION_OPEN_INVENTORY

    def open_skills(self) -> str:
        """Сигнализирует о необходимости открыть умения."""
        # TODO: Добавить логику подготовки к открытию умений, если нужно
        return CMD_ACTION_OPEN_SKILLS

    def open_shop(self) -> str:
        """Сигнализирует о необходимости открыть магазин."""
        # TODO: Добавить логику подготовки к открытию магазина, если нужно
        battle_logger.log_system_message("🛍️ Магазин (временно недоступен)")
        return CMD_ACTION_OPEN_SHOP # Возвращаем сигнал

    def open_statistics(self) -> str:
        """Сигнализирует о необходимости показать статистику."""
        # TODO: Добавить логику подготовки к показу статистики, если нужно
        return CMD_ACTION_SHOW_STATS

    # - Вспомогательные методы (оставшиеся от старой системы) -
    def get_input(self) -> str:
        """Возвращает текущую строку ввода (пустая для новой системы)."""
        return ""

    def get_available_commands(self) -> List[str]:
        """Возвращает список доступных команд."""
        # TODO: Актуализировать список команд
        return ['go', 'start', 'fight', 'help', 'h', 'clear', 'cls', 'exit', 'quit', 'q',
                'inventory', 'inv', 'i', 'skills', 'abilities', 'abil', 'stat']

# Глобальный обработчик команд (будет инициализирован в main)
# TODO: Рассмотреть возможность полного отказа от глобального command_handler
# в пользу локальных экземпляров в каждом состоянии или передачи через контекст.
command_handler = None # Инициализируется как None, затем в main.py
