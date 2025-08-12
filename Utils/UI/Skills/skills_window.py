# Utils/UI/Skills/skills_window.py - Окно умений персонажей

import curses
from typing import List, Dict, Any
from Utils.UI.ability_cards import AbilityCardNavigator
from Config.curses_config import (
    get_color_pair,
    COLOR_CYAN,
    COLOR_GRAY,
    COLOR_WHITE,
    COLOR_MAGENTA,
    COLOR_YELLOW
)
from Utils.UI.key_hints import ABILITIES_HINTS

# === КОНСТАНТЫ ===
WINDOW_TITLE = "⚔️ УМЕНИЯ ГЕРОЕВ"
SECTION_TITLE = "УМЕНИЯ ГЕРОЯ"
TAB_SPACING = 4
HEADER_HEIGHT = 4
ABILITIES_START_Y = 6
ABILITIES_START_X = 2
BOTTOM_MARGIN = 2

# Уникальные умения для разных классов
CLASS_ABILITIES = {
    "warrior": {
        "active": [
            {"name": "Разящий удар", "level": 3, "cooldown": 2, "energy": 20, "description": "Мощная атака по одной цели"},
            {"name": "Боевой клич", "level": 2, "cooldown": 4, "energy": 15, "description": "Повышает атаку союзников"},
            {"name": "Щит и меч", "level": 1, "cooldown": 3, "energy": 25, "description": "Атака с временным щитом"},
            {"name": "Кровавая ярость", "level": 4, "cooldown": 5, "energy": 30, "description": "Урон по всем врагам"},
            {"name": "Стойка защитника", "level": 2, "cooldown": 3, "energy": 20, "description": "Притягивает атаки врагов"},
            {"name": "Второе дыхание", "level": 1, "cooldown": 6, "energy": 35, "description": "Восстанавливает здоровье"}
        ],
        "passive": [
            {"name": "Железная воля", "level": 3, "description": "Сопротивление оглушению"},
            {"name": "Боевой опыт", "level": 2, "description": "Повышает получаемый опыт"},
            {"name": "Тяжелая броня", "level": 4, "description": "Снижает получаемый урон"},
            {"name": "Бесстрашие", "level": 1, "description": "Иммунитет к страху"},
            {"name": "Мастер щита", "level": 3, "description": "Частичное поглощение урона"},
            {"name": "Берсерк", "level": 2, "description": "Урон растет при низком HP"}
        ]
    },
    "mage": {
        "active": [
            {"name": "Огненный шар", "level": 4, "cooldown": 2, "energy": 25, "description": "Огненная магия по одной цели"},
            {"name": "Молния", "level": 3, "cooldown": 3, "energy": 20, "description": "Цепная магическая атака"},
            {"name": "Ледяная стена", "level": 2, "cooldown": 4, "energy": 30, "description": "Создает защитный барьер"},
            {"name": "Метеоритный дождь", "level": 5, "cooldown": 6, "energy": 40, "description": "Массовая атака по врагам"},
            {"name": "Мана буря", "level": 3, "cooldown": 4, "energy": 35, "description": "Восстанавливает ману союзников"},
            {"name": "Телепортация", "level": 2, "cooldown": 3, "energy": 25, "description": "Избегает следующей атаки"}
        ],
        "passive": [
            {"name": "Магическое проникновение", "level": 3, "description": "Игнорирует магическую защиту"},
            {"name": "Экономия маны", "level": 2, "description": "Снижает расход маны на 15%"},
            {"name": "Магическое восстановление", "level": 4, "description": "Восстановление маны каждый ход"},
            {"name": "Арканная сила", "level": 3, "description": "Повышает магический урон"},
            {"name": "Магическая защита", "level": 2, "description": "Сопротивление магическим эффектам"},
            {"name": "Критическая магия", "level": 1, "description": "Шанс критического магического урона"}
        ]
    },
    "rogue": {
        "active": [
            {"name": "Удар в спину", "level": 4, "cooldown": 3, "energy": 20, "description": "Критический урон сзади"},
            {"name": "Яд", "level": 2, "cooldown": 2, "energy": 15, "description": "Урон со временем"},
            {"name": "Скрытность", "level": 3, "cooldown": 4, "energy": 25, "description": "Временная невидимость"},
            {"name": "Отравляющий клинок", "level": 3, "cooldown": 3, "energy": 30, "description": "Атака с отравлением"},
            {"name": "Круговой удар", "level": 2, "cooldown": 3, "energy": 35, "description": "Атака по всем врагам"},
            {"name": "Бросок ножа", "level": 1, "cooldown": 2, "energy": 15, "description": "Дальняя атака"}
        ],
        "passive": [
            {"name": "Скрытный шаг", "level": 3, "description": "Шанс избежать атаки"},
            {"name": "Ядовитые клинки", "level": 2, "description": "Все атаки отравляют врагов"},
            {"name": "Критический удар", "level": 4, "description": "Повышенный шанс крита"},
            {"name": "Быстрые руки", "level": 2, "description": "Дополнительная атака"},
            {"name": "Воровская удача", "level": 1, "description": "Повышает шанс выпадения предметов"},
            {"name": "Скрытные атаки", "level": 3, "description": "Урон растет при атаке сзади"}
        ]
    },
    "healer": {
        "active": [
            {"name": "Исцеление", "level": 3, "cooldown": 2, "energy": 20, "description": "Лечение одной цели"},
            {"name": "Божественный свет", "level": 4, "cooldown": 4, "energy": 30, "description": "Массовое лечение"},
            {"name": "Очищение", "level": 2, "cooldown": 3, "energy": 25, "description": "Снимает негативные эффекты"},
            {"name": "Благословение", "level": 3, "cooldown": 5, "energy": 35, "description": "Повышает характеристики"},
            {"name": "Воскрешение", "level": 5, "cooldown": 8, "energy": 50, "description": "Оживляет павшего союзника"},
            {"name": "Святой щит", "level": 2, "cooldown": 3, "energy": 25, "description": "Временная неуязвимость"}
        ],
        "passive": [
            {"name": "Целительная сила", "level": 3, "description": "Повышает эффективность лечения"},
            {"name": "Божественная защита", "level": 2, "description": "Снижает получаемый урон"},
            {"name": "Эмпатия", "level": 4, "description": "Союзники получают часть лечения"},
            {"name": "Святая магия", "level": 3, "description": "Иммунитет к проклятиям"},
            {"name": "Духовное восстановление", "level": 2, "description": "Восстановление энергии союзников"},
            {"name": "Ангельская милость", "level": 1, "description": "Шанс спасти союзника от смерти"}
        ]
    }
}

# Универсальные умения для неизвестных классов
DEFAULT_ABILITIES = {
    "active": [
        {"name": "Атака", "level": 1, "cooldown": 0, "energy": 10, "description": "Базовая атака"},
        {"name": "Защита", "level": 1, "cooldown": 2, "energy": 15, "description": "Повышает защиту"},
        {"name": "Удар", "level": 2, "cooldown": 3, "energy": 20, "description": "Сильный удар"},
        {"name": "Лечение", "level": 1, "cooldown": 4, "energy": 25, "description": "Восстанавливает здоровье"},
        {"name": "Специальная атака", "level": 3, "cooldown": 3, "energy": 30, "description": "Магическая атака"},
        {"name": "Блок", "level": 1, "cooldown": 2, "energy": 15, "description": "Блокирует следующую атаку"}
    ],
    "passive": [
        {"name": "Сила", "level": 2, "description": "Повышает силу атаки"},
        {"name": "Выносливость", "level": 1, "description": "Повышает максимальное здоровье"},
        {"name": "Ловкость", "level": 3, "description": "Повышает шанс уклонения"},
        {"name": "Интеллект", "level": 2, "description": "Повышает магический урон"},
        {"name": "Концентрация", "level": 1, "description": "Повышает восстановление энергии"},
        {"name": "Удача", "level": 1, "description": "Повышает шанс критического удара"}
    ]
}


def display_abilities_screen(stdscr, players: List[Any]) -> None:
    """
    Отображает экран умений персонажей на весь экран с вкладками и навигацией по карточкам
    
    Args:
        stdscr: Окно curses
        players: Список игроков
    """
    if not players:
        return

    current_tab = 0
    current_navigator = None  # Навигатор для текущего персонажа
    
    while True:
        try:
            height, width = stdscr.getmaxyx()
            stdscr.clear()

            # Заголовок
            stdscr.addstr(0, width // 2 - 8, WINDOW_TITLE,
                         get_color_pair(COLOR_CYAN) | curses.A_BOLD)
            stdscr.addstr(1, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # Вкладки с именами персонажей
            tab_x = 2
            for i, player in enumerate(players):
                if i == current_tab:
                    # Активная вкладка
                    stdscr.attron(get_color_pair(COLOR_CYAN) | curses.A_BOLD)
                    stdscr.addstr(2, tab_x, f" [{player.name}] ")
                    stdscr.attroff(get_color_pair(COLOR_CYAN) | curses.A_BOLD)
                else:
                    # Неактивная вкладка
                    stdscr.attron(get_color_pair(COLOR_WHITE))
                    stdscr.addstr(2, tab_x, f" {player.name} ")
                    stdscr.attroff(get_color_pair(COLOR_WHITE))
                tab_x += len(player.name) + TAB_SPACING

            stdscr.addstr(3, 0, "─" * (width - 1), get_color_pair(COLOR_GRAY) | curses.A_DIM)

            # Получаем текущего игрока
            current_player = players[current_tab]
            
            # Определяем класс персонажа для выбора умений
            class_name = getattr(current_player, 'role', 'default')
            
            # Получаем умения для текущего класса
            abilities_data = CLASS_ABILITIES.get(class_name, DEFAULT_ABILITIES)
            all_abilities = abilities_data["active"] + abilities_data["passive"]
            
            # Создаем навигатор, если его еще нет или сменился персонаж
            if current_navigator is None:
                current_navigator = AbilityCardNavigator(all_abilities)
            
            # Заголовки секций
            stdscr.addstr(4, 2, SECTION_TITLE, get_color_pair(COLOR_MAGENTA) | curses.A_BOLD)
            
            # Отображаем все умения с навигацией
            current_navigator.display_abilities_grid(stdscr, ABILITIES_START_Y, ABILITIES_START_X, width - 4)
            
            # Подсказка выхода
            ABILITIES_HINTS.display_hints(stdscr)


            stdscr.refresh()

            # Обработка ввода
            key = stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_LEFT:
                current_tab = (current_tab - 1) % len(players)
                current_navigator = None  # Сброс навигатора при смене персонажа
            elif key == curses.KEY_RIGHT:
                current_tab = (current_tab + 1) % len(players)
                current_navigator = None  # Сброс навигатора при смене персонажа
            elif key == curses.KEY_UP:
                current_navigator.prev_ability()
            elif key == curses.KEY_DOWN:
                current_navigator.next_ability()
            elif key == curses.KEY_RESIZE:
                continue

        except curses.error:
            pass  # Защита от ошибок curses при ресайзе или переполнении


def get_player_abilities(player: Any) -> List[Dict[str, Any]]:
    """
    Получает список умений для конкретного игрока
    
    Args:
        player: Объект игрока
        
    Returns:
        List[Dict[str, Any]]: Список умений игрока
    """
    class_name = getattr(player, 'role', 'default')
    abilities_data = CLASS_ABILITIES.get(class_name, DEFAULT_ABILITIES)
    return abilities_data["active"] + abilities_data["passive"]