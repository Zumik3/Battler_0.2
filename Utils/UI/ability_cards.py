# Utils/ability_cards.py - Система отрисовки карточек умений с навигацией

import curses
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from Config.curses_config import get_color_pair, COLOR_WHITE, COLOR_YELLOW, COLOR_GRAY, COLOR_CYAN, COLOR_GREEN, COLOR_BLUE, COLOR_RED

# === КОНСТАНТЫ ===
# Размеры карточек
DEFAULT_CARD_WIDTH = 45
CARD_HEIGHT = 5  # Высота содержимого карточки (без рамки)
CARD_VERTICAL_SPACING = 6  # Вертикальный отступ между карточками
CARD_HORIZONTAL_SPACING = 2  # Горизонтальный отступ между карточками
CARDS_PER_ROW = 3  # Количество карточек в ряду

# Символы рамок
# Неактивные карточки
INACTIVE_TOP_LEFT_CORNER = "┌"
INACTIVE_TOP_RIGHT_CORNER = "┐"
INACTIVE_BOTTOM_LEFT_CORNER = "└"
INACTIVE_BOTTOM_RIGHT_CORNER = "┘"
INACTIVE_HORIZONTAL_LINE = "─"
INACTIVE_VERTICAL_LINE = "│"

# Активные карточки
ACTIVE_TOP_LEFT_CORNER = "╔"
ACTIVE_TOP_RIGHT_CORNER = "╗"
ACTIVE_BOTTOM_LEFT_CORNER = "╚"
ACTIVE_BOTTOM_RIGHT_CORNER = "╝"
ACTIVE_HORIZONTAL_LINE = "═"
ACTIVE_VERTICAL_LINE = "║"
ACTIVE_DOUBLE_HORIZONTAL_SEGMENT = "══"

# Позиции элементов в карточке
NAME_Y_OFFSET = 0
DESCRIPTION_Y_OFFSET = 1
ADDITIONAL_INFO_Y_OFFSET = 2
LEVEL_BAR_Y_OFFSET = 3

# Границы экрана
MIN_SCREEN_MARGIN = 3
SCREEN_BOTTOM_MARGIN = 3

class AbilityCard(ABC):
    """Базовый класс для отрисовки карточки умения"""
    
    def __init__(self) -> None:
        self.default_card_width: int = DEFAULT_CARD_WIDTH
        self._colors_initialized: bool = False
        self._white_color = None
        self._yellow_color = None
        self._gray_color = None
        self._cyan_color = None
        self._green_color = None
        self._blue_color = None
        self._red_color = None
        self._active_color = None
    
    def _initialize_colors(self) -> None:
        """Ленивая инициализация цветов"""
        if not self._colors_initialized:
            self._white_color = get_color_pair(COLOR_WHITE) | curses.A_BOLD
            self._yellow_color = get_color_pair(COLOR_YELLOW)
            self._gray_color = get_color_pair(COLOR_GRAY)
            self._cyan_color = get_color_pair(COLOR_CYAN)
            self._green_color = get_color_pair(COLOR_GREEN)
            self._blue_color = get_color_pair(COLOR_BLUE)
            self._red_color = get_color_pair(COLOR_RED) | curses.A_BOLD
            self._active_color = get_color_pair(COLOR_BLUE) | curses.A_BOLD
            self._colors_initialized = True
    
    @property
    def white_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._white_color
    
    @property
    def yellow_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._yellow_color
    
    @property
    def gray_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._gray_color
    
    @property
    def cyan_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._cyan_color
    
    @property
    def green_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._green_color
    
    @property
    def blue_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._blue_color
    
    @property
    def red_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._red_color
    
    @property
    def active_color(self):
        if not self._colors_initialized:
            self._initialize_colors()
        return self._active_color
    
    def calculate_card_width(self, max_width: int, screen_width: int, x: int) -> int:
        """
        Вычисляет ширину карточки
        """
        card_width = min(max_width - 4, self.default_card_width)
        if x + card_width >= screen_width:
            card_width = screen_width - x - 2
        return max(card_width, 10)
    
    def display_centered_level_bar(self, stdscr: curses.window, current_level: int, max_level: int, y: int, x: int, card_width: int, is_active: bool = False) -> None:
        """
        Отображает центрированную шкалу уровней
        """
        try:
            # Создаем строку уровней
            level_bar = ""
            for i in range(1, max_level + 1):
                if i <= current_level:
                    level_bar += "[■]"
                else:
                    level_bar += "[□]"
            
            # Вычисляем позицию для центрирования
            bar_width = len(level_bar)
            center_x = x + (card_width - bar_width) // 2
            
            # Корректируем, если выходит за границы
            if center_x < x:
                center_x = x
            elif center_x + bar_width > x + card_width:
                center_x = x + card_width - bar_width
            
            # Всегда используем желтый цвет
            stdscr.addstr(y, max(center_x, x), level_bar, self.yellow_color)
        except curses.error:
            pass
    
    @abstractmethod
    def display_additional_info(self, stdscr: curses.window, ability: Dict[str, Any], y: int, x: int, card_width: int, is_active: bool = False) -> None:
        """
        Отображает дополнительную информацию умения
        """
        pass
    
    def display_ability_card(self, stdscr: curses.window, ability: Dict[str, Any], y: int, x: int, max_width: int, is_active: bool = False) -> None:
        """
        Отображает карточку умения с полной рамкой
        """
        try:
            height, width = stdscr.getmaxyx()
            
            # Проверка границ
            if y >= height - MIN_SCREEN_MARGIN or x >= width - MIN_SCREEN_MARGIN:
                return
            
            # Вычисляем ширину карточки
            card_width = self.calculate_card_width(max_width, width, x)
            
            if is_active:
                # Активная карточка - двойная рамка красного цвета
                active_color = self.red_color
                
                # Верхняя граница с двойными углами
                if y - 1 >= 0:
                    horizontal_fill = ACTIVE_DOUBLE_HORIZONTAL_SEGMENT * ((card_width - 2) // 2)
                    if (card_width - 2) % 2:
                        horizontal_fill += ACTIVE_HORIZONTAL_LINE
                    stdscr.addstr(y - 1, x, ACTIVE_TOP_LEFT_CORNER + horizontal_fill + ACTIVE_TOP_RIGHT_CORNER, active_color)
                
                # Боковые границы
                if y < height:
                    stdscr.addstr(y, x, ACTIVE_VERTICAL_LINE, active_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y, x + card_width - 1, ACTIVE_VERTICAL_LINE, active_color)
                if y + 1 < height:
                    stdscr.addstr(y + 1, x, ACTIVE_VERTICAL_LINE, active_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y + 1, x + card_width - 1, ACTIVE_VERTICAL_LINE, active_color)
                if y + 2 < height:
                    stdscr.addstr(y + 2, x, ACTIVE_VERTICAL_LINE, active_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y + 2, x + card_width - 1, ACTIVE_VERTICAL_LINE, active_color)
                if y + 3 < height:
                    stdscr.addstr(y + 3, x, ACTIVE_VERTICAL_LINE, active_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y + 3, x + card_width - 1, ACTIVE_VERTICAL_LINE, active_color)
                
                # Нижняя граница с двойными углами
                if y + 4 < height:
                    horizontal_fill = ACTIVE_DOUBLE_HORIZONTAL_SEGMENT * ((card_width - 2) // 2)
                    if (card_width - 2) % 2:
                        horizontal_fill += ACTIVE_HORIZONTAL_LINE
                    stdscr.addstr(y + 4, x, ACTIVE_BOTTOM_LEFT_CORNER + horizontal_fill + ACTIVE_BOTTOM_RIGHT_CORNER, active_color)
            else:
                # Неактивная карточка - одинарная серая рамка
                border_color = self.gray_color
                
                # Верхняя граница
                if y - 1 >= 0:
                    stdscr.addstr(y - 1, x, INACTIVE_TOP_LEFT_CORNER + INACTIVE_HORIZONTAL_LINE * (card_width - 2) + INACTIVE_TOP_RIGHT_CORNER, border_color)
                
                # Боковые границы
                if y < height:
                    stdscr.addstr(y, x, INACTIVE_VERTICAL_LINE, border_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y, x + card_width - 1, INACTIVE_VERTICAL_LINE, border_color)
                if y + 1 < height:
                    stdscr.addstr(y + 1, x, INACTIVE_VERTICAL_LINE, border_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y + 1, x + card_width - 1, INACTIVE_VERTICAL_LINE, border_color)
                if y + 2 < height:
                    stdscr.addstr(y + 2, x, INACTIVE_VERTICAL_LINE, border_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y + 2, x + card_width - 1, INACTIVE_VERTICAL_LINE, border_color)
                if y + 3 < height:
                    stdscr.addstr(y + 3, x, INACTIVE_VERTICAL_LINE, border_color)
                    if x + card_width - 1 < width:
                        stdscr.addstr(y + 3, x + card_width - 1, INACTIVE_VERTICAL_LINE, border_color)
                
                # Нижняя граница
                if y + 4 < height:
                    stdscr.addstr(y + 4, x, INACTIVE_BOTTOM_LEFT_CORNER + INACTIVE_HORIZONTAL_LINE * (card_width - 2) + INACTIVE_BOTTOM_RIGHT_CORNER, border_color)
            
            # Имя умения (всегда белый с жирным)
            name_text = ability["name"][:card_width-2] if len(ability["name"]) > card_width-2 else ability["name"]
            stdscr.addstr(y + NAME_Y_OFFSET, x + 1, name_text, self.white_color)
            
            # Описание (всегда серый)
            desc_text = ability["description"][:card_width-2] if len(ability["description"]) > card_width-2 else ability["description"]
            stdscr.addstr(y + DESCRIPTION_Y_OFFSET, x + 1, desc_text, self.gray_color)
            
            # Дополнительная информация (сохраняем оригинальные цвета)
            if y + ADDITIONAL_INFO_Y_OFFSET < height - SCREEN_BOTTOM_MARGIN:
                self.display_additional_info(stdscr, ability, y + ADDITIONAL_INFO_Y_OFFSET, x + 1, card_width - 2, is_active)
            
            # Шкала уровней (всегда желтая)
            current_level = ability.get("level", 1)
            max_level = ability.get("max_level", 5)
            self.display_centered_level_bar(stdscr, current_level, max_level, y + LEVEL_BAR_Y_OFFSET, x + 1, card_width - 2, is_active)
                
        except curses.error:
            pass


class ActiveAbilityCard(AbilityCard):
    """Класс для отрисовки активных умений"""
    
    def display_additional_info(self, stdscr: curses.window, ability: Dict[str, Any], y: int, x: int, card_width: int, is_active: bool = False) -> None:
        """
        Отображает кулдаун и энергию для активных умений
        """
        cost_text = ""
        if "energy" in ability:
            cost_text += f"⚡ {ability['energy']} "
        if "cooldown" in ability and ability["cooldown"] > 0:
            cost_text += f"⏱️  {ability['cooldown']}"
        
        # Всегда используем голубой цвет
        if cost_text:
            stdscr.addstr(y, x, cost_text, self.cyan_color)


class PassiveAbilityCard(AbilityCard):
    """Класс для отрисовки пассивных умений"""
    
    def display_additional_info(self, stdscr: curses.window, ability: Dict[str, Any], y: int, x: int, card_width: int, is_active: bool = False) -> None:
        """
        Отображает индикатор пассивности
        """
        # Всегда используем зеленый цвет
        stdscr.addstr(y, x, "Пассивное", self.green_color)


class AbilityCardNavigator:
    """Класс для навигации между карточками умений"""
    
    def __init__(self, abilities: List[Dict[str, Any]]) -> None:
        self.abilities = abilities
        self.current_index = 0
        self.active_card_renderer = ActiveAbilityCard()
        self.passive_card_renderer = PassiveAbilityCard()
    
    def next_ability(self) -> None:
        """Перейти к следующему умению"""
        if self.abilities:
            self.current_index = (self.current_index + 1) % len(self.abilities)
    
    def prev_ability(self) -> None:
        """Перейти к предыдущему умению"""
        if self.abilities:
            self.current_index = (self.current_index - 1) % len(self.abilities)
    
    def get_current_ability(self) -> Dict[str, Any]:
        """Получить текущее выбранное умение"""
        if self.abilities:
            return self.abilities[self.current_index]
        return {}
    
    def get_current_index(self) -> int:
        """Получить индекс текущего умения"""
        return self.current_index
    
    def display_abilities_grid(self, stdscr: curses.window, start_y: int, start_x: int, max_width: int = 30) -> None:
        """
        Отображает сетку умений с выделением активного
        
        Args:
            stdscr: Окно curses
            start_y: Начальная позиция Y
            start_x: Начальная позиция X
            max_width: Максимальная ширина для отображения
        """
        if not self.abilities:
            return
        
        try:
            height, width = stdscr.getmaxyx()
            
            # Вычисляем количество умений в ряду
            abilities_per_row = CARDS_PER_ROW
            ability_width = min((max_width - 10) // abilities_per_row, DEFAULT_CARD_WIDTH)
            
            # Отображаем все умения
            for i, ability in enumerate(self.abilities):
                row = i // abilities_per_row
                col = i % abilities_per_row
                
                # Позиция карточки
                ability_x = start_x + col * (ability_width + CARD_HORIZONTAL_SPACING)
                ability_y = start_y + row * CARD_VERTICAL_SPACING
                
                # Проверяем, помещается ли карточка на экран
                if ability_y + CARD_HEIGHT < height - SCREEN_BOTTOM_MARGIN:
                    is_active = (i == self.current_index)
                    
                    # Выбираем рендерер в зависимости от типа умения
                    if ability.get("type", "active") == "active" or "cooldown" in ability or "energy" in ability:
                        self.active_card_renderer.display_ability_card(stdscr, ability, ability_y, ability_x, ability_width, is_active)
                    else:
                        self.passive_card_renderer.display_ability_card(stdscr, ability, ability_y, ability_x, ability_width, is_active)
                        
        except curses.error:
            pass


# Глобальные экземпляры для удобного использования
ACTIVE_ABILITY_CARD: ActiveAbilityCard = ActiveAbilityCard()
PASSIVE_ABILITY_CARD: PassiveAbilityCard = PassiveAbilityCard()