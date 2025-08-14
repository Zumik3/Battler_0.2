# Utils/UI/main_window.py
"""
Точка входа в приложение. Немедленно запускает основное игровое окно.
"""

import curses
from typing import List
from Characters.player_classes import Player

from Utils.UI.window import Window
# Импортируем новое основное игровое окно
from Utils.UI.event_window import EventWindow

class MainWindow(Window):
    """
    Главное окно игры - точка входа.
    Сразу запускает EventWindow.
    """

    def __init__(self, stdscr: curses.window, players: List[Player]) -> None:
        """
        Инициализирует главное окно.

        Args:
            stdscr: Основное окно curses.
            players: Список объектов игроков.
        """
        super().__init__(stdscr)
        self.players: List[Player] = players
        # MainWindow не отображается и не обрабатывает ввод сам по себе

    def get_header_text(self) -> str:
        """Заголовок не отображается."""
        return ""

    def _display_body(self) -> None:
        """Ничего не отображаем."""
        pass

    def _handle_input(self, key: int) -> bool:
        """
        Ввод не обрабатывается в этом окне.
        """
        # MainWindow не живет долго, run() просто запустит EventWindow
        return True 

    def run(self) -> None:
        """
        Переопределяем run для немедленного запуска EventWindow.
        """
        # Создаем и запускаем основное игровое окно
        # Это блокирующий вызов, пока EventWindow не закроется
        event_window = EventWindow(self.stdscr, self.players)
        event_window.run()
        
        # После закрытия EventWindow, MainWindow.run тоже завершается
        # и управление возвращается в main.py
