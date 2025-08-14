# Utils/UI/inventory_window.py
"""
Окно отображения инвентаря, реализующее паттерн Window.
"""

import curses
from typing import List, Dict, Any, TYPE_CHECKING

# Предотвращаем циклический импорт для типов
if TYPE_CHECKING:
    from Characters.player_classes import Player # Предполагаемый тип для players
    # Item - это Protocol, импортируем из inventory
    from Inventory.inventory import Item 

from Utils.UI.window import Window # Используем новое имя
from Inventory.inventory import get_inventory, Item
from Utils.UI.key_hints import InventoryHints
from Config.curses_config import get_color_pair, COLOR_CYAN, COLOR_GRAY, COLOR_WHITE, COLOR_MAGENTA, COLOR_YELLOW

# Константы для размещения элементов
TAB_SPACING = 4
HEADER_HEIGHT = 4
HERO_STATS_START_Y = 4
INVENTORY_START_Y = 11
BOTTOM_MARGIN = 2

# Определим подсказки для инвентаря, если они еще не определены в key_hints.py
# (Предполагаем, что они там есть как InventoryHints, если нет - раскомментируй ниже)
# INVENTORY_HINTS_DATA = [
#     ("← →", "Переключение героев"),
#     ("Q", "Назад")
# ]
# class InventoryHints(KeyHints):
#     def get_hints(self):
#         return [(hint[0], self.hint_color) for hint in INVENTORY_HINTS_DATA] + \
#                [(hint[1], self.hint_color) for hint in INVENTORY_HINTS_DATA]

# Предполагаем, что INVENTORY_HINTS уже определен в key_hints.py



def _display_hero_stats_in_inventory(stdscr: curses.window, player: Any, y: int, x: int, max_width: int) -> None:
    """
    Отображает характеристики героя в инвентаре (без баров, только текст).
    Скопирована и адаптирована из display_hero_stats_in_inventory из output.txt.
    """
    try:
        height, width = stdscr.getmaxyx()
        
        # Имя героя
        stdscr.addstr(y, x, player.name, get_color_pair(COLOR_CYAN) | curses.A_BOLD)
        
        # Уровень и класс
        level_class_text = f"[Ур.{player.level} {player.role.capitalize()}]"
        stdscr.addstr(y, x + len(player.name) + 1, level_class_text, get_color_pair(COLOR_WHITE))
        
        # HP и Энергия
        hp_text = f"HP: {player.hp}/{player.derived_stats.max_hp}"
        energy_text = f"Энергия: {player.energy}/{player.derived_stats.max_energy}"
        stdscr.addstr(y + 1, x, hp_text, get_color_pair(COLOR_WHITE))
        stdscr.addstr(y + 1, x + len(hp_text) + 2, energy_text, get_color_pair(COLOR_WHITE))
        
        # Основные характеристики
        stats_text = f"Сила: {player.stats.strength}  Ловк: {player.stats.dexterity}  Тело: {player.stats.constitution}  Инт: {player.stats.intelligence}"
        stdscr.addstr(y + 2, x, stats_text, get_color_pair(COLOR_WHITE))
        
        # Экипировка
        equip_col_x = x + max_width // 2 # Правая колонка для экипировки
        if hasattr(player, 'equipment_slots'):
            weapon_name = getattr(player.equipped_weapon, 'name', '-') if hasattr(player, 'equipped_weapon') else '-'
            armor_name = getattr(player.equipped_armor, 'name', '-') if hasattr(player, 'equipped_armor') else '-'
            accessory_name = getattr(player.equipped_accessory, 'name', '-') if hasattr(player, 'equipped_accessory') else '-'
            
            stdscr.addstr(y + 1, equip_col_x, f"Оружие: {weapon_name}", get_color_pair(COLOR_WHITE))
            stdscr.addstr(y + 2, equip_col_x, f"Броня: {armor_name}", get_color_pair(COLOR_WHITE))
            stdscr.addstr(y + 3, equip_col_x, f"Аксессуар: {accessory_name}", get_color_pair(COLOR_WHITE))
        else:
            stdscr.addstr(y + 1, equip_col_x, "Оружие: -", get_color_pair(COLOR_GRAY))
            stdscr.addstr(y + 2, equip_col_x, "Броня: -", get_color_pair(COLOR_GRAY))
            stdscr.addstr(y + 3, equip_col_x, "Аксессуар: -", get_color_pair(COLOR_GRAY))
        
        # Разделитель
        if y + 4 < height:
            separator_length = min(max_width - 4, width - x - 1)
            stdscr.addstr(y + 4, x, "─" * separator_length, get_color_pair(COLOR_GRAY) | curses.A_DIM)
            
    except curses.error:
        pass # Игнорируем ошибки отрисовки


class InventoryWindow(Window):
    """
    Окно для отображения инвентаря группы и характеристик игроков.
    """

    def __init__(self, stdscr: curses.window, players: List[Any]) -> None:
        """
        Инициализирует окно инвентаря.

        Args:
            stdscr: Основное окно curses.
            players: Список объектов игроков.
        """
        super().__init__(stdscr)
        self.players: List[Any] = players
        self.current_tab: int = 0 # Индекс активной вкладки (игрока)
        self.inventory = get_inventory() # Получаем синглтон инвентаря
        
        # Устанавливаем подсказки
        self.hint_class = InventoryHints()

    def get_header_text(self) -> str:
        """Возвращает текст заголовка окна."""
        return "🎒 ИНВЕНТАРЬ"

    def _display_body(self) -> None:
        """Отображение основного содержимого окна - характеристик и инвентаря."""
        if not self.players:
            try:
                self.stdscr.addstr(2, 2, "Нет игроков для отображения инвентаря.")
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

            # 2. Отображение характеристик текущего героя
            current_player = self.players[self.current_tab]
            max_content_width = width - 4
            _display_hero_stats_in_inventory(
                self.stdscr, 
                current_player, 
                HERO_STATS_START_Y, 
                2, 
                max_content_width
            )

            # 3. Отображение содержимого инвентаря
            inventory_start_y = INVENTORY_START_Y
            self.stdscr.addstr(inventory_start_y, 2, "🧳 ИНВЕНТАРЬ", get_color_pair(COLOR_MAGENTA) | curses.A_BOLD)
            self.stdscr.addstr(inventory_start_y + 1, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)
            
            # Отображение золота
            gold_y = inventory_start_y + 2
            self.stdscr.addstr(gold_y, 4, f"💰 Золото: {self.inventory.get_gold()}", get_color_pair(COLOR_YELLOW))

            # Отображение предметов
            item_objects: Dict[Item, int] = self.inventory.get_all_items()
            item_y = inventory_start_y + 4
            item_index = 0

            if not item_objects:
                self.stdscr.addstr(item_y, 4, "Инвентарь пуст", get_color_pair(COLOR_GRAY))
            else:
                for item_object, quantity in item_objects.items():
                    if item_y + item_index >= height - BOTTOM_MARGIN:
                        # Не хватает места, показываем многоточие
                        self.stdscr.addstr(item_y + item_index, 4, "...", get_color_pair(COLOR_GRAY))
                        break
                    
                    try:
                        # Получаем имя и редкость предмета
                        item_name = getattr(item_object, 'name', str(item_object))
                        rarity_color = getattr(item_object, 'get_rarity_color', lambda: COLOR_WHITE)()
                        
                        # Формируем строку предмета
                        item_line = f"◦ {item_name}"
                        if quantity > 1:
                            item_line += f" (x{quantity})"
                        
                        # Отображаем предмет
                        self.stdscr.addstr(item_y + item_index, 4, item_line, get_color_pair(rarity_color))
                        item_index += 1
                    except Exception: # На случай проблем с отдельными предметами
                        item_name = getattr(item_object, 'name', str(item_object))
                        self.stdscr.addstr(item_y + item_index, 4, f"◦ {item_name}: {quantity}", get_color_pair(COLOR_WHITE))
                        item_index += 1

        except curses.error:
            # Игнорируем ошибки отрисовки, например, при маленьком окне
            pass
        except Exception as e:
            # Можно добавить логирование ошибок
            try:
                self.stdscr.addstr(2, 2, f"Ошибка отображения инвентаря: {e}")
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
        # Обработка переключения вкладок игроков
        # Стрелки влево/вправо и Tab
        if key == curses.KEY_LEFT or key == curses.KEY_RIGHT or key == 9: # 9 - код клавиши Tab
            if len(self.players) > 1:
                if key == curses.KEY_LEFT:
                    # Переключение влево по стрелке
                    self.current_tab = (self.current_tab - 1) % len(self.players)
                elif key == curses.KEY_RIGHT or key == 9: # Вправо по стрелке или Tab
                    self.current_tab = (self.current_tab + 1) % len(self.players)
            return False # Продолжить работу

        # Обработка выхода
        if key == ord('q') or key == ord('Q'):
            return True # Сигнал для выхода из окна

        # Игнорировать другие клавиши
        return False
