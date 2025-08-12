# Utils/key_hints.py - Система подсказок для клавиш

import curses
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
from Config.curses_config import get_color_pair, COLOR_GRAY

class KeyHints(ABC):
    """Базовый класс для подсказок клавиш"""
    
    def __init__(self) -> None:
        self.pair_separator: str = " : "      # Разделитель внутри пары (клавиша : описание)
        self.group_separator: str = " │ "     # Разделитель между парами
        self._hint_color = None
    
    @property
    def hint_color(self):
        """Ленивая инициализация цвета после инициализации curses"""
        if self._hint_color is None:
            self._hint_color = get_color_pair(COLOR_GRAY) | curses.A_DIM
        return self._hint_color
    
    @abstractmethod
    def get_hints(self) -> List[Tuple[str, int]]:
        """
        Возвращает список подсказок в формате (текст, цвет)
        Должен возвращать пары: клавиша, описание, клавиша, описание...
        
        Returns:
            List[Tuple[str, int]]: Список кортежей (текст подсказки, цвет curses)
        """
        pass
    
    def display_hints(self, stdscr: curses.window, start_y: Optional[int] = None) -> None:
        """
        Отображает подсказки в нижней части экрана (2 строки)
        Если start_y не указан, автоматически определяет позицию
        
        Args:
            stdscr: Окно curses для отрисовки
            start_y: Начальная позиция по Y (по умолчанию None - автоматически)
        """
        try:
            height, width = stdscr.getmaxyx()
            
            # Если start_y не указан, используем последние 2 строки
            if start_y is None:
                start_y = height - 2
            
            # Рисуем разделительную линию
            if start_y < height:
                stdscr.addstr(start_y, 0, "─" * (width - 1), self.hint_color)
            
            # Отображаем подсказки на следующей строке
            hints_y = start_y + 1
            if hints_y < height:
                self._draw_hints_line(stdscr, hints_y, 2, width - 4)
                
        except curses.error:
            pass  # Игнорируем ошибки отрисовки
    
    def _draw_hints_line(self, stdscr: curses.window, y: int, x: int, max_width: int) -> None:
        """
        Отрисовывает строку подсказок
        
        Args:
            stdscr: Окно curses для отрисовки
            y: Позиция по вертикали
            x: Позиция по горизонтали
            max_width: Максимальная ширина строки
        """
        try:
            hints_data: List[Tuple[str, int]] = self.get_hints()
            if not hints_data:
                return
            
            current_x: int = x
            max_x: int = x + max_width - 2
            
            # Обрабатываем подсказки парами (клавиша + описание)
            for i in range(0, len(hints_data), 2):
                # Добавляем разделитель между группами, кроме первой
                if i > 0:
                    if current_x + len(self.group_separator) < max_x:
                        stdscr.addstr(y, current_x, self.group_separator, self.hint_color)
                        current_x += len(self.group_separator)
                    else:
                        break
                
                # Добавляем клавишу
                key_text, key_color = hints_data[i]
                if current_x + len(key_text) < max_x:
                    stdscr.addstr(y, current_x, key_text, key_color)
                    current_x += len(key_text)
                else:
                    break
                
                # Добавляем разделитель внутри пары
                if current_x + len(self.pair_separator) < max_x:
                    stdscr.addstr(y, current_x, self.pair_separator, self.hint_color)
                    current_x += len(self.pair_separator)
                else:
                    break
                
                # Добавляем описание
                if i + 1 < len(hints_data):
                    desc_text, desc_color = hints_data[i + 1]
                    if current_x + len(desc_text) < max_x:
                        stdscr.addstr(y, current_x, desc_text, desc_color)
                        current_x += len(desc_text)
                    else:
                        # Пытаемся добавить многоточие
                        if current_x + 3 < max_x:
                            stdscr.addstr(y, current_x, "...", self.hint_color)
                        break
                else:
                    break
                    
        except curses.error:
            pass  # Игнорируем ошибки отрисовки


class MainWindowHints(KeyHints):
    """Подсказки для основного окна игры"""
    
    def get_hints(self) -> List[Tuple[str, int]]:
        
        hints_dict = {
            "Enter": "Начать бой",
            "I": "Инвентарь", 
            "S": "Умения",
            "R": "Магазин",
            "F12": "Статистика",
            "H": "Помощь",
            "C": "Очистить лог",
            "Q": "Выход"
        }
        
        return [
            item 
            for key, desc in hints_dict.items() 
            for item in [(key, self.hint_color), (desc, self.hint_color)]
        ]


class InventoryHints(KeyHints):
    """Подсказки для окна инвентаря"""
    
    def get_hints(self) -> List[Tuple[str, int]]:
        return [
            ("← →", self.hint_color),
            ("Переключение героев", self.hint_color),
            ("Q", self.hint_color),
            ("Назад", self.hint_color)
        ]


class AbilitiesHints(KeyHints):
    """Подсказки для окна умений"""
    
    def get_hints(self) -> List[Tuple[str, int]]:
        return [
            ("← →", self.hint_color),
            ("Переключение героев", self.hint_color),
            ("↑/↓", self.hint_color),
            ("навигация по умениям", self.hint_color),
            ("Q", self.hint_color),
            ("Назад", self.hint_color)
        ]


class ShopHints(KeyHints):
    """Подсказки для окна магазина"""
    
    def get_hints(self) -> List[Tuple[str, int]]:
        return [
            ("← →", self.hint_color),
            ("Навигация", self.hint_color),
            ("Enter", self.hint_color),
            ("Купить", self.hint_color),
            ("Q", self.hint_color),
            ("Назад", self.hint_color)
        ]


class BattleHints(KeyHints):
    """Подсказки для окна боя"""
    
    def get_hints(self) -> List[Tuple[str, int]]:
        return [
            ("Пробел", self.hint_color),
            ("Следующий ход", self.hint_color),
            ("Q", self.hint_color),
            ("Завершить бой", self.hint_color)
        ]


class StatisticHints(KeyHints):
    """Подсказки для окон статистики"""
    
    def get_hints(self) -> List[Tuple[str, int]]:
        return [
            ("↑↓", self.hint_color),
            ("Навигация", self.hint_color),
            ("Enter", self.hint_color),
            ("Выбрать", self.hint_color),
            ("Q", self.hint_color),
            ("Назад", self.hint_color)
        ]


# Глобальные экземпляры для удобного использования
MAIN_HINTS: MainWindowHints = MainWindowHints()
INVENTORY_HINTS: InventoryHints = InventoryHints()
ABILITIES_HINTS: AbilitiesHints = AbilitiesHints()
SHOP_HINTS: ShopHints = ShopHints()
BATTLE_HINTS: BattleHints = BattleHints()
STATISTICS_HINTS: StatisticHints = StatisticHints()