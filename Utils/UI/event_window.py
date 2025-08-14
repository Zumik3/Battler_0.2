# Utils/UI/event_window.py
"""
Основное игровое окно. Отображает состояние игры и обрабатывает команды.
"""

import curses
from typing import List
from Characters.player_classes import Player
from Battle.battle_logger import battle_logger
from Utils.commands import CommandHandler
from Utils.display import create_screen_observer, update_display
# Импортируем create_enemies для создания врагов при старте боя
from Characters.char_utils import create_enemies

from Utils.UI.window import Window
# Импортируем подсказки для основного окна
from Utils.UI.key_hints import MainWindowHints

class EventWindow(Window):
    """
    Основное игровое окно.
    Отображает список игроков, лог и обрабатывает пользовательский ввод.
    """

    def __init__(self, stdscr: curses.window, players: List[Player]) -> None:
        """
        Инициализирует основное окно игры.

        Args:
            stdscr: Основное окно curses.
            players: Список объектов игроков.
        """
        super().__init__(stdscr)
        self.players: List[Player] = players
        
        # === ИНИЦИАЛИЗАЦИЯ ИНФРАСТРУКТУРЫ ===
        # 1. Создаем список врагов (пока пустой)
        self.enemies: List = []
        
        # 2. Создаем обработчик команд
        self.command_handler = CommandHandler(self.players, self.enemies, self.stdscr)
        
        # 3. Создаем и регистрируем наблюдателя
        # ВАЖНО: Проверить, не конфликтует ли это с другими observer'ами
        # Если MainWindow создавал свой observer, его нужно удалить
        self.screen_observer = create_screen_observer(self.stdscr, self.command_handler)
        battle_logger.add_observer(self.screen_observer)
        
        # 4. Настройки экрана (могут дублировать setup_screen, но для гарантии)
        self.stdscr.nodelay(False)  # Блокирующий режим
        self.stdscr.keypad(True)    # Включаем поддержку специальных клавиш
        
        # 5. Устанавливаем подсказки
        self.hint_class = MainWindowHints()
        
        # 6. Инициализационные сообщения
        battle_logger.log_system_message("🎮 Добро пожаловать в автобаттлер!")
        battle_logger.log_system_message("Нажмите 'H' для помощи")

    def get_header_text(self) -> str:
        """Заголовок."""
        return "🏰 ГЛАВНОЕ МЕНЮ"

    def _display_body(self) -> None:
        """Отображение основного содержимого окна."""
        # Используем существующую функцию update_display для совместимости
        try:
            update_display(self.stdscr, self.command_handler)
        except curses.error:
            pass

    def _handle_input(self, key: int) -> bool:
        """
        Обработка пользовательского ввода через CommandHandler.

        Args:
            key: Код нажатой клавиши.

        Returns:
            bool: True, если игра должна завершиться (команда 'q').
        """
        try:
            # Передаем ввод обработчику команд
            # process_input возвращает True, если нужно выйти из игры
            should_exit = self.command_handler.process_input(key)
            return should_exit
            
        except Exception as e:
            # Логируем возможные ошибки обработки ввода
            battle_logger.log_system_message(f"❌ Ошибка обработки ввода: {e}")
            
        return False # Продолжить работу по умолчанию

    def run(self) -> None:
        """
        Запускает основной цикл окна.
        Переопределяем, чтобы добавить очистку ресурсов при выходе.
        """
        try:
            # Запускаем стандартный цикл Window
            super().run()
        finally:
            # При выходе из run, очищаем ресурсы
            try:
                battle_logger.remove_observer(self.screen_observer)
            except Exception as e:
                # Игнорируем ошибки при удалении observer'а, но можно залогировать
                # battle_logger.log_system_message(f"Предупреждение при закрытии: {e}")
                pass
