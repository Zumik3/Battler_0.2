# Utils/UI/main_window.py
"""Главное окно игры. Отображает начальное меню."""
import curses
from typing import List, Optional, Any
from Characters.player_classes import Player
from Battle.battle_logger import battle_logger
from Utils.UI.window import Window
from Utils.UI.key_hints import MainWindowHints # Импортируем КЛАСС MainWindowHints
# Импортируем CommandHandler
from Utils.command_handler import CommandHandler

class MainWindow(Window):
    """Главное окно игры - точка входа.
    Отображает меню и обрабатывает команды.
    """
    def __init__(self, stdscr: curses.window, players: List[Player]) -> None:
        """Инициализирует главное окно.
        Args:
            stdscr: Основное окно curses.
            players: Список объектов игроков.
        """
        super().__init__(stdscr)
        self.players: List[Player] = players
        # ИСПРАВЛЕНИЕ 1: Создаем ЭКЗЕМПЛЯР класса MainWindowHints
        self.hint_class: Optional[Any] = MainWindowHints() # <-- Создаем экземпляр!
        
        # ИСПРАВЛЕНИЕ 2: Создаем CommandHandler для MainWindow
        # Передаем ему необходимые зависимости
        # enemies будет пустым списком, так как враги создаются в EventState/EventWindow
        self.command_handler: CommandHandler = CommandHandler(
            players=self.players,
            enemies=[], # Враги будут созданы позже в EventWindow
            stdscr=self.stdscr
        )

    def get_header_text(self) -> str:
        """Возвращает текст заголовка окна."""
        return "🏰 ГЛАВНОЕ МЕНЮ"

    def _display_body(self) -> None:
        """Отображение основного содержимого окна - меню."""
        height, width = self.stdscr.getmaxyx()
        menu_items = [
            "1. Начать бой (Enter)",
            "2. Инвентарь (I)",
            "3. Умения (S)",
            "4. Магазин (R)",
            "5. Статистика (F12)",
            "6. Помощь (H)",
            "7. Очистить лог (C)",
            "8. Выход (Q)"
        ]
        start_y = 4
        for i, item in enumerate(menu_items):
            if start_y + i < height - 2: # Проверка на выход за границы
                try:
                    self.stdscr.addstr(start_y + i, 4, item)
                except curses.error:
                    pass # Игнорируем ошибки отрисовки

    def _handle_input(self, key: int) -> bool:
        """
        Обработка пользовательского ввода.
        Args:
            key: Код нажатой клавиши.
        Returns:
            bool: True, если окно должно закрыться (например, по 'q'), иначе False.
        """
        # В данном упрощенном варианте обработка клавиш для выхода
        if key in [ord('q'), ord('Q'), 27]: # ESC, Q
            return True # Сигнал для выхода из всей игры
        # Другие клавиши можно обрабатывать здесь или делегировать command_handler
        # Пока просто возвращаем False для продолжения работы
        return False

    # === Метод render без аргументов ===
    def render(self) -> None:
        """
        Отрисовывает содержимое главного меню.
        Использует внутренний self.stdscr, как и другие окна (например, EventWindow).
        Этот метод необходим для совместимости с GameContext/GameState.
        """
        try:
            # Очищаем окно перед отрисовкой
            self.stdscr.clear()

            # Вызываем стандартные методы отрисовки из Window
            self._display_header() # Отрисовка заголовка
            self._display_body()   # Отрисовка тела (меню)
            self._display_footer() # Отрисовка подсказок

            # Обновляем экран
            self.stdscr.refresh()

        except curses.error:
            # Игнорируем ошибки отрисовки curses
            pass
        except Exception as e:
            # Можно добавить логирование других ошибок
            # battle_logger.log_system_message(f"❌ Ошибка отрисовки MainWindow: {e}")
            pass

    # === Удаляем или закомментируем старый run, который сразу запускал EventWindow ===
    # def run(self) -> None:
    #     """Переопределяем run для немедленного запуска EventWindow."""
    #     # Создаем и запускаем основное игровое окно
    #     # Это блокирующий вызов, пока EventWindow не закроется
    #     event_window = EventWindow(self.stdscr, self.players)
    #     event_window.run()
    #     # После закрытия EventWindow, MainWindow.run тоже завершается
