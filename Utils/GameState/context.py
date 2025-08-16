# Utils/GameState/context.py
"""Контекст игры, управляющий текущим состоянием."""

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

    def set_state(self, state: GameState) -> None:
        """Переключается в новое состояние."""
        if self.current_state:
            self.current_state.exit_state()

        self.current_state = state
        self.current_state.set_context(self) # Передаем ссылку на контекст

        self.current_state.enter_state()

    def set_exit_flag(self, flag: bool) -> None:
        """Устанавливает флаг выхода из игры."""
        self._should_exit = flag

    def should_exit(self) -> bool:
        """Возвращает флаг выхода из игры."""
        return self._should_exit

    # --- Исправленные методы ---
    
    def handle_input(self, key: int) -> bool: # <-- Возвращаем bool
        """Обрабатывает пользовательский ввод."""
        if self.current_state:
            # Возвращаем результат обработки ввода состоянием
            return self.current_state.handle_input(key) # <-- Возвращаем значение
        return False # По умолчанию не выходить

    def update(self) -> None:
        """Обновляет логику текущего состояния."""
        if self.current_state:
            self.current_state.update()

    def render(self) -> None:
        """Отрисовывает текущее состояние."""
        if self.current_state:
            self.current_state.render(self.stdscr)

    # --- Основной цикл ---
    
    def run(self) -> None:
        """Основной цикл игры."""
        while not self._should_exit and self.current_state:
            try:
                # 1. Очистка экрана
                self.stdscr.clear()

                # 2. Обновление логики текущего состояния
                self.update()

                # 3. Отрисовка текущего состояния
                self.render()

                # 4. Обновление экрана
                self.stdscr.refresh()

                # 5. Получение и обработка ввода
                key = self.stdscr.getch()
                # Передаем управление текущему состоянию
                # Если handle_input возвращает True, это сигнал на выход из всей игры
                # --- Исправлено: теперь правильно используем возвращаемое значение ---
                self._should_exit = self.handle_input(key) 

            except curses.error:
                # Игнорируем ошибки отрисовки, например, при ресайзе окна
                # TODO: Добавить более сложную логику обработки ошибок curses
                pass
            except Exception as e:
                # Можно добавить логирование критических ошибок
                # print(f"Критическая ошибка: {e}") # Лучше использовать логгер
                # TODO: Залогировать ошибку через battle_logger
                self._should_exit = True # Принудительный выход при критической ошибке

        # Финализация при выходе...