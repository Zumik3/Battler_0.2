# Utils/UI/window.py

import abc
import curses
from typing import Optional

class AbstractWindow(abc.ABC):
    """Абстрактный класс для управления окном с базовой структурой"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height = 0
        self.width = 0
        self.hint_class = None
    
    def run(self):
        """Основной цикл окна"""
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
                key = self.stdscr.getch()
                if self._handle_input(key):
                    break
                    
            except curses.error:
                pass
            except Exception:
                pass
    
    def _display_header(self):
        """Отображение заголовка окна"""
        header_text = self.get_header_text()
        if header_text and self.height > 1:
            try:
                self.stdscr.addstr(0, max(0, self.width // 2 - len(header_text) // 2), 
                                 header_text, self.get_header_style())
                self.stdscr.addstr(1, 0, "─" * (self.width - 1), 
                                 self.get_separator_style())
            except curses.error:
                pass
    
    def _display_footer(self):
        """Отображение подсказки по клавишам"""
        if self.hint_class and hasattr(self.hint_class, 'display_hints'):
            self.hint_class.display_hints(self.stdscr)

    @abc.abstractmethod
    def get_header_text(self) -> str:
        """Возвращает текст заголовка окна"""
        pass
    
    @abc.abstractmethod
    def _display_body(self):
        """Отображение основного содержимого окна"""
        pass
    
    @abc.abstractmethod
    def _handle_input(self, key: int) -> bool:
        """Обработка пользовательского ввода. Возвращает True для выхода"""
        pass
    
    def get_header_style(self):
        """Возвращает стиль заголовка"""
        return curses.A_BOLD
    
    def get_separator_style(self):
        """Возвращает стиль разделителей"""
        return curses.A_DIM
