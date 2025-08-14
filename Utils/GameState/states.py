# GameState/states.py
"""
Модуль, определяющий состояния игры и их поведение.
Использует паттерн State для управления различными режимами (меню, бой, инвентарь и т.д.).
"""

from abc import ABC, abstractmethod
import curses
from typing import TYPE_CHECKING, Optional, Any

# Используем TYPE_CHECKING, чтобы избежать циклического импорта
# при аннотировании типов
if TYPE_CHECKING:
    from Utils.GameState.context import GameContext
    from Characters.character import Player

class GameState(ABC):
    """Абстрактный базовый класс для состояний игры."""

    def __init__(self):
        self.context: Optional['GameContext'] = None

    def set_context(self, context: 'GameContext'):
        """Устанавливает ссылку на контекст игры."""
        self.context = context

    @abstractmethod
    def enter_state(self):
        """Вызывается при входе в это состояние."""
        pass

    @abstractmethod
    def exit_state(self):
        """Вызывается при выходе из этого состояния."""
        pass

    @abstractmethod
    def handle_input(self, key: int):
        """
        Обрабатывает пользовательский ввод в этом состоянии.
        Может изменить состояние через self.context.set_state().
        """
        pass

    @abstractmethod
    def update(self):
        """Обновляет логику состояния (если требуется)."""
        pass

    @abstractmethod
    def render(self, stdscr: curses.window):
        """Отрисовывает содержимое, соответствующее этому состоянию."""
        pass


# --- Конкретные состояния ---

class MenuState(GameState):
    """Состояние главного меню."""

    def enter_state(self):
        # Можно инициализировать данные, специфичные для меню
        pass

    def exit_state(self):
        # Можно освободить ресурсы, специфичные для меню
        pass

    def handle_input(self, key: int):
        if key == ord('q') or key == ord('Q'):
            # Передаем сигнал выхода в контекст
            self.context.set_exit_flag(True)
        elif key == ord('\n'): # Enter
            # Пример: начать бой
            from Utils.GameState.states import BattleState # Импорт внутри функции для избежания циклов
            self.context.set_state(BattleState())
        elif key == ord('i') or key == ord('I'):
            # Пример: открыть инвентарь
            from GameState.states import InventoryState
            self.context.set_state(InventoryState())
        elif key == ord('s') or key == ord('S'):
            # Пример: открыть умения
            from GameState.states import AbilitiesState
            self.context.set_state(AbilitiesState())
        # ... другие клавиши для меню ...

    def update(self):
        # Логика обновления меню (если нужна)
        pass

    def render(self, stdscr: curses.window):
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        try:
            title = "Главное меню"
            stdscr.addstr(0, max(0, width // 2 - len(title) // 2), title, curses.A_BOLD)
            
            # Пример отображения статуса
            if self.context and self.context.players:
                player_name = self.context.players[0].name if self.context.players else "Герой"
                stdscr.addstr(2, 2, f"Герой: {player_name}")
            
            # Пример пунктов меню
            menu_items = [
                "Enter - Начать бой",
                "I - Инвентарь",
                "S - Умения",
                "Q - Выход"
            ]
            for i, item in enumerate(menu_items):
                stdscr.addstr(4 + i, 2, item)
            
            # Здесь можно вызвать отображение подсказок из KeyHints
            # (пока просто текст)
            stdscr.addstr(height - 2, 0, "Нажмите клавишу...")
        except curses.error:
            pass


class BattleState(GameState):
    """Состояние боя."""

    def __init__(self):
        super().__init__()
        # Инициализируем логику боя, если нужно
        self.battle_active = True
        self.battle_log = [] # Упрощенный лог для примера

    def enter_state(self):
        # Инициализация боя, создание врагов и т.д.
        self.battle_log.append("Бой начался!")
        # Здесь будет логика из BattleManager
        pass

    def exit_state(self):
        # Очистка после боя
        self.battle_active = False
        pass

    def handle_input(self, key: int):
        # Обработка ввода во время боя
        # Это может быть сложнее, например, выбор действий
        if key == ord('q') or key == ord('Q'):
            # Вернуться в меню после боя
            from GameState.states import MenuState
            self.context.set_state(MenuState())
        elif key == ord(' '): # Пробел - следующий ход
            self.battle_log.append("Ход выполнен...")
            # Здесь будет логика одного раунда боя

    def update(self):
        # Логика обновления боя (если нужна)
        pass

    def render(self, stdscr: curses.window):
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        try:
            stdscr.addstr(0, 2, "=== Бой ===", curses.A_BOLD)
            
            # Отображение лога боя (простой пример)
            for i, log_entry in enumerate(self.battle_log[-(height-4):]): # Показываем последние записи
                 stdscr.addstr(2 + i, 2, log_entry[:width-4])
            
            stdscr.addstr(height - 2, 0, "Пробел - следующий ход, Q - выйти из боя")
        except curses.error:
            pass


class InventoryState(GameState):
    """Состояние инвентаря."""

    def enter_state(self):
        # Инициализация данных инвентаря, если нужно
        pass

    def exit_state(self):
        # Сохранение изменений, если нужно
        pass

    def handle_input(self, key: int):
        # Обработка ввода в инвентаре
        if key == ord('q') or key == ord('Q'):
            from GameState.states import MenuState
            self.context.set_state(MenuState())
        # ... логика навигации по инвентарю ...

    def update(self):
        pass

    def render(self, stdscr: curses.window):
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        try:
            stdscr.addstr(0, 2, "=== Инвентарь ===", curses.A_BOLD)
            
            # Здесь будет логика отображения инвентаря
            # Например, из функции display_inventory или класса InventoryWindow
            stdscr.addstr(2, 2, "Содержимое инвентаря...")
            
            stdscr.addstr(height - 2, 0, "Q - Назад в меню")
        except curses.error:
            pass


class AbilitiesState(GameState):
    """Состояние экрана умений."""

    def enter_state(self):
        pass

    def exit_state(self):
        pass

    def handle_input(self, key: int):
        if key == ord('q') or key == ord('Q'):
            from GameState.states import MenuState
            self.context.set_state(MenuState())
        # ... логика навигации по умениям ...

    def update(self):
        pass

    def render(self, stdscr: curses.window):
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        try:
            stdscr.addstr(0, 2, "=== Умения ===", curses.A_BOLD)
            
            # Здесь будет логика отображения умений
            # Например, из функции display_abilities_screen или класса AbilitiesScreenWindow
            stdscr.addstr(2, 2, "Список умений...")
            
            stdscr.addstr(height - 2, 0, "Q - Назад в меню")
        except curses.error:
            pass

# Добавить другие состояния по аналогии: StatisticsState, ShopState и т.д.