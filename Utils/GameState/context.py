# GameState/context.py
"""
Контекст игры, управляющий текущим состоянием.
"""

import curses
from typing import List, Optional, Any
from Utils.GameState.states import GameState, MenuState

class GameContext:
    """Контекст игры, хранящий текущее состояние и общие данные."""

    def __init__(self, stdscr: curses.window, players: List[Any], enemies: List[Any]):
        self.stdscr = stdscr
        self.players = players
        self.enemies = enemies
        self.current_state: Optional[GameState] = None
        self._should_exit = False
        
        # Инициализируем начальное состояние
        self.set_state(MenuState())

    def set_state(self, state: GameState):
        """Переключается в новое состояние."""
        if self.current_state:
            self.current_state.exit_state()
        
        self.current_state = state
        self.current_state.set_context(self) # Передаем ссылку на контекст
        self.current_state.enter_state()

    def set_exit_flag(self, flag: bool):
        """Устанавливает флаг выхода из игры."""
        self._should_exit = flag

    def should_exit(self) -> bool:
        """Возвращает флаг выхода из игры."""
        return self._should_exit

    def handle_input(self, key: int):
        """Передает ввод текущему состоянию."""
        if self.current_state:
            self.current_state.handle_input(key)

    def update(self):
        """Обновляет логику текущего состояния."""
        if self.current_state:
            self.current_state.update()

    def render(self):
        """Отрисовывает текущее состояние."""
        if self.current_state:
            self.current_state.render(self.stdscr)