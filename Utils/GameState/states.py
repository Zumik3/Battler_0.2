# Utils/GameState/states.py
"""Модуль, определяющий состояния игры и их поведение.
Использует паттерн State для управления различными режимами (меню, события и т.д.)."""

from abc import ABC, abstractmethod
import curses
from typing import TYPE_CHECKING, Optional, Any

# Импорты внутри метода, чтобы избежать циклических импортов
# from Utils.UI.main_window import MainWindow
# from Utils.UI.event_window import EventWindow

if TYPE_CHECKING:
    from Utils.GameState.context import GameContext


class GameState(ABC):
    """Абстрактный базовый класс для состояний игры."""

    def __init__(self) -> None:
        self.context: Optional['GameContext'] = None

    def set_context(self, context: 'GameContext') -> None:
        """Устанавливает ссылку на контекст игры."""
        self.context = context

    @abstractmethod
    def enter_state(self) -> None:
        """Вызывается при входе в состояние."""
        pass

    @abstractmethod
    def exit_state(self) -> None:
        """Вызывается при выходе из состояния."""
        pass

    @abstractmethod
    def handle_input(self, key: int) -> bool:  # Возвращаем bool для сигнала выхода
        """Обрабатывает ввод пользователя.

        Args:
            key: Код нажатой клавиши.

        Returns:
            bool: True, если игра должна завершиться, иначе False.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """Обновляет логику состояния."""
        pass

    @abstractmethod
    def render(self, stdscr: curses.window) -> None:
        """Отрисовывает состояние на экране."""
        pass


class MenuState(GameState):
    """Состояние главного меню."""

    def __init__(self) -> None:
        super().__init__()
        self.main_window: Optional[Any] = None  # Будет инициализирован в enter_state

    def enter_state(self) -> None:
        """Инициализация при входе в меню."""
        if self.context:
            from Utils.UI.main_window import MainWindow  # Импорт внутри метода
            self.main_window = MainWindow(self.context.stdscr, self.context.players)
            # main_window.run() не вызываем напрямую, управление через context

    def exit_state(self) -> None:
        """Очистка при выходе из меню."""
        self.main_window = None

    def handle_input(self, key: int) -> bool:
        """Обработка ввода в меню."""
        # Делегируем обработку ввода существующему MainWindow
        if self.main_window:
            # process_input теперь возвращает сигналы вместо запуска окон
            action = self.main_window.command_handler.process_input(key)
            # Интерпретируем сигналы и выполняем соответствующие переходы
            from Utils.GameState.states import (
                EventState,
                InventoryState,
                AbilitiesState,
                StatisticsState,
                ShopState
            )  # Импорты внутри метода, чтобы избежать циклических импортов

            if action == "exit":
                return True  # Сигнал на выход из всей игры
            elif action == "start_battle":
                if self.context:
                    self.context.set_state(EventState())
            elif action == "open_inventory":
                if self.context:
                    self.context.set_state(InventoryState())
            elif action == "open_abilities":
                if self.context:
                    self.context.set_state(AbilitiesState())
            elif action == "open_statistics":
                if self.context:
                    self.context.set_state(StatisticsState())
            elif action == "open_shop":
                if self.context:
                    self.context.set_state(ShopState())
            # Добавить другие состояния по аналогии: AbilitiesState, StatisticsState и т.д.

        # Проверяем стандартные команды выхода
        if key in [ord('q'), ord('Q'), 27]:  # ESC, Q
            return True  # Сигнал на выход из всей игры

        return False  # Продолжить работу

    def update(self) -> None:
        """Обновление логики меню."""
        # Пока не требуется
        pass

    def render(self, stdscr: curses.window) -> None:
        """Отрисовка меню."""
        if self.main_window:
            self.main_window.render()  # Вызываем render у MainWindow


class EventState(GameState):
    """Состояние игрового события/боя."""

    def __init__(self) -> None:
        super().__init__()
        self.event_window: Optional[Any] = None
        # Убираем event_finished, так как теперь состояние боя отслеживается в EventWindow
        # и завершение определяется по содержимому лога или флагу контекста

    def enter_state(self) -> None:
        """Инициализация при входе в событие."""
        if self.context:
            from Utils.UI.event_window import EventWindow  # Импорт внутри метода
            # Передаем игроков. Враги создаются внутри EventWindow.
            self.event_window = EventWindow(self.context.stdscr, self.context.players)
            # Бой запускается автоматически внутри run EventWindow

    def exit_state(self) -> None:
        """Очистка при выходе из события."""
        self.event_window = None

    def handle_input(self, key: int) -> bool:
        """Обработка ввода во время/после события."""
        # Делегируем обработку ввода EventWindow
        # EventWindow._handle_input теперь обрабатывает только 'q' и возвращает True для выхода
        if self.event_window:
            # _handle_input в EventWindow возвращает True только если нужно выйти ('q')
            should_exit_event_window = self.event_window._handle_input(key)
            if should_exit_event_window:
                # Переключаемся в меню
                from Utils.GameState.states import MenuState
                if self.context:
                    # Сбрасываем флаг выхода, если он был установлен
                    self.context.set_exit_flag(False)
                    self.context.set_state(MenuState())
                return False  # Не выходить из игры, просто переключиться
        return False  # Продолжить работу

    def update(self) -> None:
        """Обновление логики события."""
        # Пока не требуется, так как логика в основном по вводу или в run EventWindow
        pass

    def render(self, stdscr: curses.window) -> None:
        """Отрисовка события."""
        if self.event_window:
            # render EventWindow должен отображать текущий лог боя
            self.event_window.render()  # Вызываем render у EventWindow


# Заглушка для InventoryState
class InventoryState(GameState):
    def enter_state(self) -> None:
        if self.context:
            from Battle.battle_logger import battle_logger
            battle_logger.log_system_message("📦 Инвентарь (временно недоступен)")
            # TODO: Реализовать логику открытия инвентаря
            # Например, создать InventoryWindow и делегировать ему управление

    def exit_state(self) -> None:
        pass

    def handle_input(self, key: int) -> bool:
        # Пока просто сразу возвращаемся в меню
        from Utils.GameState.states import MenuState
        if self.context:
            self.context.set_state(MenuState())
        return False  # Не выходить из игры

    def update(self) -> None:
        pass

    def render(self, stdscr: curses.window) -> None:
        if self.context:
            try:
                stdscr.addstr(2, 2, "Инвентарь (временно недоступен). Нажмите любую клавишу для возврата в меню.")
            except curses.error:
                pass


# Заглушка для AbilitiesState
class AbilitiesState(GameState):
    def enter_state(self) -> None:
        if self.context:
            from Battle.battle_logger import battle_logger
            battle_logger.log_system_message("⚔️ Умения (временно недоступен)")
            from Utils.GameState.states import MenuState
            if self.context:
                self.context.set_state(MenuState())

    def exit_state(self) -> None:
        pass

    def handle_input(self, key: int) -> bool:
        from Utils.GameState.states import MenuState
        if self.context:
            self.context.set_state(MenuState())
        return False

    def update(self) -> None:
        pass

    def render(self, stdscr: curses.window) -> None:
        if self.context:
            try:
                stdscr.addstr(2, 2, "Умения (временно недоступен). Нажмите любую клавишу для возврата в меню.")
            except curses.error:
                pass


# Заглушка для StatisticsState
class StatisticsState(GameState):
    def enter_state(self) -> None:
        if self.context:
            from Battle.battle_logger import battle_logger
            battle_logger.log_system_message("📈 Статистика (временно недоступна)")
            from Utils.GameState.states import MenuState
            if self.context:
                self.context.set_state(MenuState())

    def exit_state(self) -> None:
        pass

    def handle_input(self, key: int) -> bool:
        from Utils.GameState.states import MenuState
        if self.context:
            self.context.set_state(MenuState())
        return False

    def update(self) -> None:
        pass

    def render(self, stdscr: curses.window) -> None:
        if self.context:
            try:
                stdscr.addstr(2, 2, "Статистика (временно недоступна). Нажмите любую клавишу для возврата в меню.")
            except curses.error:
                pass

# Заглушка для ShopState
class ShopState(GameState):
    def enter_state(self) -> None:
        if self.context:
            from Battle.battle_logger import battle_logger
            battle_logger.log_system_message("🏪 Магазин (временно недоступен)")
            from Utils.GameState.states import MenuState
            if self.context:
                self.context.set_state(MenuState())

    def exit_state(self) -> None:
        pass

    def handle_input(self, key: int) -> bool:
        from Utils.GameState.states import MenuState
        if self.context:
            self.context.set_state(MenuState())
        return False

    def update(self) -> None:
        pass

    def render(self, stdscr: curses.window) -> None:
        if self.context:
            try:
                stdscr.addstr(2, 2, "Магазин (временно недоступен). Нажмите любую клавишу для возврата в меню.")
            except curses.error:
                pass
