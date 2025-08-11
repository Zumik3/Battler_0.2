# draw_character.py - Полностью автономный класс для отрисовки строки персонажа

import curses
import random
from Config.game_config import ENERGY_BAR_WIDTH, NAME_COLUMN_WIDTH, PROGRESS_BORDER_CHARS, PROGRESS_BAR_CHARS, HP_BAR_WIDTH, BASE_ENERGY_COST
from Config.curses_config import get_color_pair, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_GRAY, COLOR_WHITE


class DrawCharacter:
    """
    Класс для полной отрисовки строки персонажа: имя, HP, Energy, статусы.
    Включает ВСЁ: отрисовку имени, прогресс-бары, эффекты — без внешних зависимостей.
    """

    @staticmethod
    def draw_character_name(stdscr, y: int, x: int, char) -> None:
        """
        Отрисовывает имя персонажа с иконкой класса, уровнем, цветом и меткой смерти.
        - Игрок: больше места (NAME_COLUMN_WIDTH + 15)
        - Враг: меньше места (NAME_COLUMN_WIDTH)
        - Имя обрезается с "..", если не влезает с учётом класса и уровня
        - Цвета: имя — зелёное (игрок), синее (враг); класс — его цветом; уровень — жёлтый; скобки — белые
        - Мёртвый: † в начале, серый цвет, с пробелом после
        """
        # 🔹 Устанавливаем ширину в зависимости от типа персонажа
        if char.is_player:
            name_width = NAME_COLUMN_WIDTH  # Игрок — больше места
        else:
            name_width = NAME_COLUMN_WIDTH + 25      # Враг — стандартная ширина

        current_x = x
        max_x = x + name_width  # Правая граница

        # Цвета
        white_color = get_color_pair(COLOR_WHITE)
        yellow_color = get_color_pair(COLOR_YELLOW)
        gray_color = get_color_pair(COLOR_GRAY) | curses.A_DIM
        base_name_color = get_color_pair(COLOR_GREEN) if char.is_player else get_color_pair(COLOR_BLUE)
        name_color = gray_color if not char.is_alive() else base_name_color

        # 1. Рисуем † если мёртв + пробел после
        if not char.is_alive():
            try:
                if current_x < max_x:
                    stdscr.addstr(y, current_x, "† ", gray_color)
                    current_x += 2
            except curses.error:
                pass

        # 🔹 Предварительный расчёт: сколько займут суффиксы
        suffix_len = 0
        has_class = bool(getattr(char, 'class_icon', ''))
        has_level = getattr(char, 'level', None) is not None

        if has_class:
            suffix_len += 3  # " [X]" → 3 символа
        if has_level:
            suffix_len += 2 + len(str(char.level))  # " [10]" → 5, " [5]" → 4 и т.д.

        # Сколько символов доступно под имя (учитываем пробел после †)
        space_for_name = max_x - current_x - suffix_len
        space_for_name = max(0, space_for_name)

        # 2. Обрезаем имя с учётом места и добавляем ".."
        full_name = getattr(char, 'name', '')
        display_name = ""

        if space_for_name >= 2:
            if len(full_name) <= space_for_name:
                display_name = full_name
            else:
                display_name = full_name[:space_for_name - 2] + ".."
        elif space_for_name == 1:
            display_name = "." if len(full_name) > 0 else ""
        # Если 0 — ничего не выводим

        # Отрисовываем имя
        if display_name:
            try:
                if current_x < max_x:
                    # Не выходим за границу
                    end_x = min(current_x + len(display_name), max_x)
                    text_to_draw = display_name[:end_x - current_x]
                    stdscr.addstr(y, current_x, text_to_draw, name_color)
                    current_x += len(text_to_draw)
            except curses.error:
                pass

        # 3. Класс: [X]
        class_icon = getattr(char, 'class_icon', '')
        class_color_pair = get_color_pair(getattr(char, 'class_icon_color', COLOR_WHITE))
        if class_icon and current_x + 3 <= max_x:
            try:
                stdscr.addstr(y, current_x, " [", white_color)
                stdscr.addstr(y, current_x + 2, class_icon, class_color_pair)
                stdscr.addstr(y, current_x + 3, "]", white_color)
                current_x += 4  # " [X]" = 4 символа
            except curses.error:
                pass

        # 4. Уровень: [N]
        level = getattr(char, 'level', None)
        if level is not None:
            level_str = str(level)
            required = 3 + len(level_str)  # " [N]" → 3 + цифры
            if current_x + required <= max_x:
                try:
                    stdscr.addstr(y, current_x, " [", white_color)
                    stdscr.addstr(y, current_x + 2, level_str, yellow_color)
                    stdscr.addstr(y, current_x + 2 + len(level_str), "]", white_color)
                    current_x += required
                except curses.error:
                    pass

        # 5. Заполняем остаток пробелами
        try:
            while current_x < max_x:
                stdscr.addstr(y, current_x, " ", name_color)
                current_x += 1
        except curses.error:
            pass

    @staticmethod
    def draw_progress_bar(stdscr, y: int, x: int, current_value: int, max_value: int,
                         bar_width: int, bar_color=None,
                         show_percent: bool = False, show_values: bool = False,
                         border_chars=PROGRESS_BORDER_CHARS, bar_chars=PROGRESS_BAR_CHARS):
        """
        Универсальный прогресс-бар (HP, Energy и др.) — перенесён из progress_bar.py.
        """
        if max_value <= 0:
            ratio = 0
        else:
            ratio = max(0.0, min(1.0, current_value / max_value))

        filled_width = int(ratio * bar_width)
        if current_value > 0 and filled_width == 0 and bar_width > 0:
            filled_width = 1
        filled_width = max(0, min(filled_width, bar_width))

        filled_char = bar_chars[0]
        empty_char = bar_chars[1]
        bar = filled_char * filled_width + empty_char * (bar_width - filled_width)

        # Цвет
        if bar_color is None:
            if current_value <= 0:
                bar_color = get_color_pair(COLOR_RED)
            elif ratio > 0.75:
                bar_color = get_color_pair(COLOR_GREEN)
            elif ratio > 0.25:
                bar_color = get_color_pair(COLOR_YELLOW)
            else:
                bar_color = get_color_pair(COLOR_RED)
        elif isinstance(bar_color, int):
            bar_color = get_color_pair(bar_color)

        # Границы
        left_border, right_border = border_chars
        try:
            stdscr.addstr(y, x, left_border, get_color_pair(COLOR_GRAY))
            stdscr.addstr(y, x + 1, bar, bar_color)
            stdscr.addstr(y, x + 1 + bar_width, right_border, get_color_pair(COLOR_GRAY))

            # Текстовые данные
            text_parts = []
            if show_percent:
                text_parts.append(f"{int(ratio * 100)}%")
            if show_values:
                text_parts.append(f"{current_value}/{max_value}")
            if text_parts:
                text = " " + " ".join(text_parts)
                stdscr.addstr(y, x + 1 + bar_width + 1, text, get_color_pair(COLOR_GRAY))
        except curses.error:
            pass

    @staticmethod
    def draw_energy_bar(stdscr, y: int, x: int, current_energy: int, max_energy: int, bar_width: int = None):
        """
        Специализированный бар энергии — скрывает энергию, если < BASE_ENERGY_COST.
        """
        if bar_width is None:
            bar_width = HP_BAR_WIDTH

        display_energy = 0 if current_energy < BASE_ENERGY_COST else current_energy

        DrawCharacter.draw_progress_bar(
            stdscr=stdscr,
            y=y,
            x=x,
            current_value=display_energy,
            max_value=max_energy,
            bar_width=bar_width,
            bar_color=7,  # Предполагается, что цвет 7 — синий (энергия)
            show_percent=False,
            show_values=False
        )

    @staticmethod
    def draw_hp_bar(stdscr, y: int, x: int, character, bar_width: int = 10) -> int:
        """
        Отрисовка HP-бара по персонажу.
        """
        current_hp = getattr(character, 'hp', 0)
        max_hp = getattr(character.derived_stats, 'max_hp', 1)
        DrawCharacter.draw_progress_bar(
            stdscr=stdscr,
            y=y,
            x=x,
            current_value=current_hp,
            max_value=max_hp,
            bar_width=bar_width,
            bar_color=None,
            show_percent=False,
            show_values=False
        )
        return x + bar_width + 2

    @staticmethod
    def draw_energy_bar_direct(stdscr, y: int, x: int, character, bar_width: int = 8) -> int:
        """
        Удобная обёртка для отрисовки энергии.
        """
        current_energy = getattr(character, 'energy', 0)
        max_energy = getattr(character.derived_stats, 'max_energy', 1)
        DrawCharacter.draw_energy_bar(
            stdscr=stdscr,
            y=y,
            x=x,
            current_energy=current_energy,
            max_energy=max_energy,
            bar_width=bar_width
        )
        return x + bar_width + 2

    @staticmethod
    def draw_status_effects(stdscr, y: int, x: int, character, max_width: int = 15) -> int:
        """
        Отрисовка активных эффектов (пока — заглушка).
        """
        try:
            effects = getattr(character, 'active_effects', [])
            if not effects:
                return x

            names = [eff.name[:6] for eff in effects[:3]]
            text = " | ".join(names)
            if len(text) > max_width:
                text = text[:max_width - 2] + ".."

            stdscr.addstr(y, x, text, get_color_pair(COLOR_GRAY) | curses.A_DIM)
            return x + len(text) + 1
        except Exception:
            pass
        return x

    @classmethod
    def draw_character_row(cls, stdscr, character, y: int, x: int, is_player: bool = True):
        """
        Полная отрисовка строки персонажа.
        """
        current_x = x

        # 1. Имя
        cls.draw_character_name(stdscr, y, current_x, character)
        current_x += NAME_COLUMN_WIDTH + 1

        # 2. HP
        current_x = cls.draw_hp_bar(stdscr, y, current_x, character, HP_BAR_WIDTH)
        current_x += 1

        # 3. Energy
        current_x = cls.draw_energy_bar_direct(stdscr, y, current_x, character, ENERGY_BAR_WIDTH)
        current_x += 1

        # 4. Эффекты
        cls.draw_status_effects(stdscr, y, current_x, character, max_width=15)