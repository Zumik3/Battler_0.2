# Utils/UI/window.py
"""
Базовый абстрактный класс для создания окон в интерфейсе curses.

Этот модуль предоставляет каркас для всех окон приложения, обеспечивая
единообразие в отображении (заголовок, тело, футер) и обработке ввода.
"""

import curses
from abc import ABC, abstractmethod
from typing import Optional, Any


class Window(ABC):
    """
    Абстрактный класс для управления окном с базовой структурой.

    Предоставляет основной цикл отображения и обработки ввода, а также
    абстрактные методы, которые должны быть реализованы в подклассах.
    """

    # -------------------------------------------------------------------------
    # Инициализация
    # -------------------------------------------------------------------------

    def __init__(self, stdscr: curses.window) -> None:
        """
        Инициализирует базовое окно.

        Args:
            stdscr: Основное окно curses, предоставленное wrapper'ом.
        """
        self.stdscr: curses.window = stdscr
        self.height: int = 0
        self.width: int = 0
        self.hint_class: Optional[Any] = None # Ожидается класс типа KeyHints

    # -------------------------------------------------------------------------
    # Основной цикл окна
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """
        Основной цикл окна.

        Выполняет обновление размеров, очистку экрана, отрисовку всех частей
        окна и обработку пользовательского ввода до тех пор, пока
        `_handle_input` не вернёт True (сигнал для выхода).
        """
        while True:
            try:
                self.height, self.width = self.stdscr.getmaxyx()
                self.stdscr.clear()

                # Отображение базовой структуры окна
                self._display_header()
                self._display_body()
                self._display_footer()

                self.stdscr.refresh()

                # Обработка ввода
                key: int = self.stdscr.getch()
                if self._handle_input(key):
                    break

            except curses.error:
                # Игнорируем ошибки отрисовки, например, при ресайзе окна
                pass
            except Exception:
                # Игнорируем другие неожиданные ошибки в цикле
                pass

    # -------------------------------------------------------------------------
    # Отрисовка: Заголовок
    # -------------------------------------------------------------------------

    def _display_header(self) -> None:
        """Отображение заголовка окна."""
        header_text: str = self.get_header_text()
        if header_text and self.height > 1:
            try:
                centered_x: int = max(0, self.width // 2 - len(header_text) // 2)
                self.stdscr.addstr(0, centered_x, header_text, self.get_header_style())
                self.stdscr.addstr(1, 0, "─" * (self.width - 1), self.get_separator_style())
            except curses.error:
                # Игнорируем ошибки отрисовки
                pass

    @abstractmethod
    def get_header_text(self) -> str:
        """
        Возвращает текст заголовка окна.

        Должен быть реализован в подклассе.

        Returns:
            str: Текст, отображаемый в заголовке окна.
        """
        pass

    def get_header_style(self) -> int:
        """
        Возвращает стиль заголовка.

        Returns:
            int: Стиль curses для заголовка (по умолчанию curses.A_BOLD).
        """
        return curses.A_BOLD

    # -------------------------------------------------------------------------
    # Отрисовка: Основное содержимое
    # -------------------------------------------------------------------------

    @abstractmethod
    def _display_body(self) -> None:
        """
        Отображение основного содержимого окна.

        Должен быть реализован в подклассе.
        """
        pass

    # -------------------------------------------------------------------------
    # Отрисовка: Футер (подсказки)
    # -------------------------------------------------------------------------

    def _display_footer(self) -> None:
        """Отображение подсказки по клавишам."""
        if self.hint_class and hasattr(self.hint_class, 'display_hints'):
            try:
                self.hint_class.display_hints(self.stdscr)
            except curses.error:
                # Игнорируем ошибки отрисовки подсказок
                pass

    def get_separator_style(self) -> int:
        """
        Возвращает стиль разделителей.

        Returns:
            int: Стиль curses для разделителей (по умолчанию curses.A_DIM).
        """
        return curses.A_DIM

    # -------------------------------------------------------------------------
    # Обработка ввода
    # -------------------------------------------------------------------------

    @abstractmethod
    def _handle_input(self, key: int) -> bool:
        """
        Обработка пользовательского ввода.

        Должен быть реализован в подклассе.

        Args:
            key (int): Код нажатой клавиши.

        Returns:
            bool: True, если окно должно закрыться, иначе False.
        """
        pass