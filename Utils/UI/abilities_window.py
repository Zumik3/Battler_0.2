# Utils/UI/abilities_window.py
"""
Окно отображения умений персонажей, реализующее паттерн Window.
"""

import curses
from typing import List, Dict, Any, TYPE_CHECKING

# Предотвращаем циклический импорт для типов
# Player импортируем напрямую, так как он используется в get_player_abilities
from Characters.player_classes import Player, Warrior, Mage, Healer, Rogue, Archer, Tank

from Utils.UI.window import Window # Используем новое имя
from Utils.UI.ability_cards import AbilityCardNavigator
from Config.curses_config import get_color_pair, COLOR_CYAN, COLOR_GRAY, COLOR_WHITE, COLOR_MAGENTA, COLOR_YELLOW

# Импортируем стандартные подсказки
from Utils.UI.key_hints import AbilitiesHints # <-- Изменение 1: Импорт

# === КОНСТАНТЫ (обновлены для соответствия реальным умениям) ===
TAB_SPACING = 4
HEADER_HEIGHT = 4
ABILITIES_START_Y = 6
ABILITIES_START_X = 2
BOTTOM_MARGIN = 2

# Убираем CLASS_ABILITIES, так как будем получать данные напрямую
# DEFAULT_ABILITIES также не нужны, так как все игроки должны иметь способности

def get_player_abilities(player: Player) -> List[Dict[str, Any]]:
    """
    Получает список умений игрока в формате, пригодном для отображения.
    Получает данные напрямую из AbilityManager игрока.
    Args:
        player: Объект игрока.
    Returns:
        List[Dict[str, Any]]: Список умений игрока в формате для карточек.
    """
    abilities_list = []
    
    # Сначала добавляем активные способности (кроме Attack и Rest)
    for name, ability_instance in player.ability_manager.active_abilities.items():
        # Исключаем базовые непрокачиваемые способности
        if name in ["Attack", "Rest"]:
            continue
        # Формируем данные для карточки
        ability_data = {
            "name": ability_instance.name,
            "description": ability_instance.description,
            "level": getattr(ability_instance, 'level', 0),
            "max_level": getattr(ability_instance, 'max_level', 5), # Умолчание, если нет max_level
            "energy": getattr(ability_instance, 'energy_cost', 0),
            "cooldown": getattr(ability_instance, 'cooldown', 0),
            # Можно добавить иконку, если она есть у способности
            # "icon": getattr(ability_instance, 'icon', "")
        }
        abilities_list.append(ability_data)
        
    # Затем добавляем пассивные способности
    for name, ability_instance in player.ability_manager.passive_abilities.items():
        # Формируем данные для карточки
        ability_data = {
            "name": ability_instance.name,
            "description": ability_instance.description,
            "level": getattr(ability_instance, 'level', 0),
            "max_level": getattr(ability_instance, 'max_level', 5), # Умолчание, если нет max_level
            # Пассивные способности обычно не требуют энергии и не имеют кулдауна
            "energy": 0,
            "cooldown": 0,
            # "icon": getattr(ability_instance, 'icon', "")
        }
        abilities_list.append(ability_data)
        
    return abilities_list


class AbilitiesScreenWindow(Window):
    """
    Окно для отображения и навигации по умениям игроков.
    Использует AbilityCardNavigator для отрисовки карточек.
    """

    def __init__(self, stdscr: curses.window, players: List[Player]) -> None:
        """
        Инициализирует окно умений.

        Args:
            stdscr: Основное окно curses.
            players: Список объектов игроков.
        """
        super().__init__(stdscr)
        self.players: List[Player] = players
        self.current_tab: int = 0 # Индекс активной вкладки (игрока)
        # Инициализируем навигатор, начальные данные возьмем для первого игрока
        if self.players:
            initial_abilities = get_player_abilities(self.players[0])
            self.navigator = AbilityCardNavigator(initial_abilities)
        else:
            self.navigator = AbilityCardNavigator([])
        
        # <-- Изменение 2: Устанавливаем стандартные подсказки -->
        self.hint_class = AbilitiesHints()

    def get_header_text(self) -> str:
        """Возвращает текст заголовка окна."""
        return "⚔️ УМЕНИЯ ГЕРОЕВ"

    def _display_body(self) -> None:
        """Отображение основного содержимого окна - умений игроков."""
        if not self.players:
            try:
                self.stdscr.addstr(2, 2, "Нет игроков для отображения умений.")
            except curses.error:
                pass
            return

        height, width = self.stdscr.getmaxyx()
        
        try:
            # 1. Отображение вкладок игроков
            tab_x = 2
            for i, player in enumerate(self.players):
                if i == self.current_tab:
                    self.stdscr.attron(get_color_pair(COLOR_CYAN) | curses.A_BOLD)
                    self.stdscr.addstr(2, tab_x, f"[{player.name}]")
                    self.stdscr.attroff(get_color_pair(COLOR_CYAN) | curses.A_BOLD)
                else:
                    self.stdscr.attron(get_color_pair(COLOR_WHITE))
                    self.stdscr.addstr(2, tab_x, f" {player.name} ")
                    self.stdscr.attroff(get_color_pair(COLOR_WHITE))
                tab_x += len(player.name) + TAB_SPACING

            self.stdscr.addstr(3, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # 2. Получаем данные для текущего игрока
            current_player = self.players[self.current_tab]
            # Обновляем навигатор данными для текущего игрока
            current_abilities = get_player_abilities(current_player)
            self.navigator.abilities = current_abilities
            # Убеждаемся, что индекс не вышел за границы
            if self.navigator.current_index >= len(current_abilities) and current_abilities:
                self.navigator.current_index = 0
            elif not current_abilities:
                 self.navigator.current_index = 0

            # 3. Отображение карточек умений
            self.navigator.display_abilities_grid(
                self.stdscr,
                start_y=ABILITIES_START_Y,
                start_x=ABILITIES_START_X,
                max_width=width - 4 # Учитываем поля
            )

        except curses.error:
            # Игнорируем ошибки отрисовки, например, при маленьком окне
            pass
        except Exception as e:
            # Можно добавить логирование ошибок
            try:
                self.stdscr.addstr(2, 2, f"Ошибка отображения: {e}")
            except curses.error:
                pass

    def _handle_input(self, key: int) -> bool:
        """
        Обработка пользовательского ввода.

        Args:
            key: Код нажатой клавиши.

        Returns:
            bool: True, если окно должно закрыться (например, по 'q'), иначе False.
        """
        # Обработка переключения вкладок
        if key == 9: # Tab
            if len(self.players) > 1:
                self.current_tab = (self.current_tab + 1) % len(self.players)
                # Сбрасываем индекс навигатора при смене вкладки
                self.navigator.current_index = 0
                return False # Продолжить работу
        
        # Обработка навигации по умениям
        if key == curses.KEY_RIGHT:
            self.navigator.next_ability()
            return False
        if key == curses.KEY_LEFT:
            self.navigator.prev_ability()
            return False

        # Обработка выхода
        if key == ord('q') or key == ord('Q'):
            return True # Сигнал для выхода из окна

        # Игнорировать другие клавиши
        return False
