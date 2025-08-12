# draw_character.py - Полностью автономный класс для отрисовки строки персонажа

import curses
import random
from Config.game_config import ENERGY_BAR_WIDTH, MONSTER_NAME_COLUMN_WIDTH, PLAYER_NAME_COLUMN_WIDTH, PROGRESS_BORDER_CHARS, PROGRESS_BAR_CHARS, HP_BAR_WIDTH, BASE_ENERGY_COST
from Config.curses_config import get_color_pair, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_GRAY, COLOR_WHITE

# Константы для отрисовки
ENEMY_NAME_EXTRA_WIDTH = 25
CLASS_ICON_DISPLAY_WIDTH = 3
LEVEL_DISPLAY_BASE_WIDTH = 2
DEATH_SYMBOL_WIDTH = 2
CLASS_DISPLAY_WIDTH = 4
MIN_LENGTH_FOR_DOTS = 2
MIN_LENGTH_FOR_DOT = 1
HP_BAR_DEFAULT_WIDTH = 10
ENERGY_BAR_DEFAULT_WIDTH = 8
DEFAULT_SPACING = 1
AFTER_BAR_SPACING = 2
ENERGY_BAR_COLOR = 7
HIGH_HP_THRESHOLD = 0.75
LOW_HP_THRESHOLD = 0.25
MAX_EFFECT_NAME_LENGTH = 6
MAX_DISPLAYED_EFFECTS = 3
EFFECT_DOTS_LENGTH = 2
STATUS_EFFECTS_MAX_WIDTH = 15


class DrawCharacter:
    """
    Класс для полной отрисовки строки персонажа: имя, HP, Energy, статусы.
    Включает ВСЁ: отрисовку имени, прогресс-бары, эффекты — без внешних зависимостей.
    """

    @staticmethod
    def draw_character_name(screen, position_y: int, position_x: int, character) -> int:
        """
        Отрисовывает имя персонажа с иконкой класса, уровнем, цветом и меткой смерти.
        - Игрок: больше места (NAME_COLUMN_WIDTH + 15)
        - Враг: меньше места (NAME_COLUMN_WIDTH)
        - Имя обрезается с "..", если не влезает с учётом класса и уровня
        - Цвета: имя — зелёное (игрок), синее (враг); класс — его цветом; уровень — жёлтый; скобки — белые
        - Мёртвый: † в начале, серый цвет, с пробелом после
        """
        # Устанавливаем ширину в зависимости от типа персонажа
        total_name_width = PLAYER_NAME_COLUMN_WIDTH if character.is_player else MONSTER_NAME_COLUMN_WIDTH

        current_x_position = position_x
        max_x_position = position_x + total_name_width  # Правая граница

        # Цвета
        white_color_pair = get_color_pair(COLOR_WHITE)
        yellow_color_pair = get_color_pair(COLOR_YELLOW)
        gray_dim_color_pair = get_color_pair(COLOR_GRAY) | curses.A_DIM
        base_name_color_pair = get_color_pair(COLOR_GREEN) if character.is_player else get_color_pair(COLOR_BLUE)
        final_name_color_pair = gray_dim_color_pair if not character.is_alive() else base_name_color_pair

        # 1. Рисуем † если мёртв + пробел после
        if not character.is_alive():
            try:
                if current_x_position < max_x_position:
                    screen.addstr(position_y, current_x_position, "† ", gray_dim_color_pair)
                    current_x_position += DEATH_SYMBOL_WIDTH
            except curses.error:
                pass

        # 🔹 Предварительный расчёт: сколько займут суффиксы
        suffix_total_length = 0
        has_class_icon = bool(getattr(character, 'class_icon', ''))
        has_level_info = getattr(character, 'level', None) is not None

        if has_class_icon:
            suffix_total_length += CLASS_ICON_DISPLAY_WIDTH  # " [X]" → 3 символа
        if has_level_info:
            suffix_total_length += LEVEL_DISPLAY_BASE_WIDTH + len(str(character.level))  # " [10]" → 5, " [5]" → 4 и т.д.

        # Сколько символов доступно под имя (учитываем пробел после †)
        available_space_for_name = max_x_position - current_x_position - suffix_total_length
        available_space_for_name = max(0, available_space_for_name)

        # 2. Обрезаем имя с учётом места и добавляем ".."
        character_full_name = getattr(character, 'name', '')
        display_name_text = ""

        if available_space_for_name >= MIN_LENGTH_FOR_DOTS:
            if len(character_full_name) <= available_space_for_name:
                display_name_text = character_full_name
            else:
                display_name_text = character_full_name[:available_space_for_name - EFFECT_DOTS_LENGTH] + ".."
        elif available_space_for_name == MIN_LENGTH_FOR_DOT:
            display_name_text = "." if len(character_full_name) > 0 else ""
        # Если 0 — ничего не выводим

        # Отрисовываем имя
        if display_name_text:
            try:
                if current_x_position < max_x_position:
                    # Не выходим за границу
                    end_x_position = min(current_x_position + len(display_name_text), max_x_position)
                    text_to_render = display_name_text[:end_x_position - current_x_position]
                    screen.addstr(position_y, current_x_position, text_to_render, final_name_color_pair)
                    current_x_position += len(text_to_render)
            except curses.error:
                pass

        # 3. Класс: [X]
        class_icon_symbol = getattr(character, 'class_icon', '')
        class_icon_color_pair = get_color_pair(getattr(character, 'class_icon_color', COLOR_WHITE))
        if class_icon_symbol and current_x_position + CLASS_ICON_DISPLAY_WIDTH <= max_x_position:
            try:
                screen.addstr(position_y, current_x_position, " [", white_color_pair)
                screen.addstr(position_y, current_x_position + LEVEL_DISPLAY_BASE_WIDTH, class_icon_symbol, class_icon_color_pair)
                screen.addstr(position_y, current_x_position + CLASS_ICON_DISPLAY_WIDTH, "]", white_color_pair)
                current_x_position += CLASS_DISPLAY_WIDTH  # " [X]" = 4 символа
            except curses.error:
                pass

        # 4. Уровень: [N]
        character_level = getattr(character, 'level', None)
        if character_level is not None:
            level_string = str(character_level)
            required_space = LEVEL_DISPLAY_BASE_WIDTH + len(level_string) + DEFAULT_SPACING  # " [N]" → 3 + цифры
            if current_x_position + required_space <= max_x_position:
                try:
                    screen.addstr(position_y, current_x_position, " [", white_color_pair)
                    screen.addstr(position_y, current_x_position + LEVEL_DISPLAY_BASE_WIDTH, level_string, yellow_color_pair)
                    screen.addstr(position_y, current_x_position + LEVEL_DISPLAY_BASE_WIDTH + len(level_string), "]", white_color_pair)
                    current_x_position += required_space
                except curses.error:
                    pass

        # 5. Заполняем остаток пробелами
        try:
            while current_x_position < max_x_position:
                screen.addstr(position_y, current_x_position, " ", final_name_color_pair)
                current_x_position += 1
        except curses.error:
            pass

        return current_x_position

    @staticmethod
    def draw_progress_bar(screen, position_y: int, position_x: int, current_value: int, max_value: int,
                         bar_width: int, bar_color=None,
                         show_percent: bool = False, show_values: bool = False,
                         border_characters=PROGRESS_BORDER_CHARS, bar_characters=PROGRESS_BAR_CHARS):
        """
        Универсальный прогресс-бар (HP, Energy и др.) — перенесён из progress_bar.py.
        """
        if max_value <= 0:
            ratio_value = 0
        else:
            ratio_value = max(0.0, min(1.0, current_value / max_value))

        filled_segment_width = int(ratio_value * bar_width)
        if current_value > 0 and filled_segment_width == 0 and bar_width > 0:
            filled_segment_width = 1
        filled_segment_width = max(0, min(filled_segment_width, bar_width))

        filled_character = bar_characters[0]
        empty_character = bar_characters[1]
        progress_bar_string = filled_character * filled_segment_width + empty_character * (bar_width - filled_segment_width)

        # Цвет
        if bar_color is None:
            if current_value <= 0:
                bar_color_pair = get_color_pair(COLOR_RED)
            elif ratio_value > HIGH_HP_THRESHOLD:
                bar_color_pair = get_color_pair(COLOR_GREEN)
            elif ratio_value > LOW_HP_THRESHOLD:
                bar_color_pair = get_color_pair(COLOR_YELLOW)
            else:
                bar_color_pair = get_color_pair(COLOR_RED)
        elif isinstance(bar_color, int):
            bar_color_pair = get_color_pair(bar_color)
        else:
            bar_color_pair = bar_color

        # Границы
        left_border_char, right_border_char = border_characters
        try:
            screen.addstr(position_y, position_x, left_border_char, get_color_pair(COLOR_GRAY))
            screen.addstr(position_y, position_x + 1, progress_bar_string, bar_color_pair)
            screen.addstr(position_y, position_x + 1 + bar_width, right_border_char, get_color_pair(COLOR_GRAY))

            # Текстовые данные
            text_parts_list = []
            if show_percent:
                text_parts_list.append(f"{int(ratio_value * 100)}%")
            if show_values:
                text_parts_list.append(f"{current_value}/{max_value}")
            if text_parts_list:
                additional_text = " " + " ".join(text_parts_list)
                screen.addstr(position_y, position_x + 1 + bar_width + 1, additional_text, get_color_pair(COLOR_GRAY))
        except curses.error:
            pass

    @staticmethod
    def draw_energy_bar(screen, position_y: int, position_x: int, current_energy: int, max_energy: int, bar_width: int = None):
        """
        Специализированный бар энергии — скрывает энергию, если < BASE_ENERGY_COST.
        """
        if bar_width is None:
            bar_width = HP_BAR_WIDTH

        display_energy_value = 0 if current_energy < BASE_ENERGY_COST else current_energy

        DrawCharacter.draw_progress_bar(
            screen=screen,
            position_y=position_y,
            position_x=position_x,
            current_value=display_energy_value,
            max_value=max_energy,
            bar_width=bar_width,
            bar_color=ENERGY_BAR_COLOR,  # Предполагается, что цвет 7 — синий (энергия)
            show_percent=False,
            show_values=False
        )

    @staticmethod
    def draw_hp_bar(screen, position_y: int, position_x: int, character, bar_width: int = None) -> int:
        """
        Отрисовка HP-бара по персонажу.
        """
        if bar_width is None:
            bar_width = HP_BAR_DEFAULT_WIDTH
            
        current_hp_value = getattr(character, 'hp', 0)
        max_hp_value = getattr(character.derived_stats, 'max_hp', 1)
        DrawCharacter.draw_progress_bar(
            screen=screen,
            position_y=position_y,
            position_x=position_x,
            current_value=current_hp_value,
            max_value=max_hp_value,
            bar_width=bar_width,
            bar_color=None,
            show_percent=False,
            show_values=False
        )
        return position_x + bar_width + AFTER_BAR_SPACING

    @staticmethod
    def draw_energy_bar_direct(screen, position_y: int, position_x: int, character, bar_width: int = None) -> int:
        """
        Удобная обёртка для отрисовки энергии.
        """
        if bar_width is None:
            bar_width = ENERGY_BAR_DEFAULT_WIDTH
            
        current_energy_value = getattr(character, 'energy', 0)
        max_energy_value = getattr(character.derived_stats, 'max_energy', 1)
        DrawCharacter.draw_energy_bar(
            screen=screen,
            position_y=position_y,
            position_x=position_x,
            current_energy=current_energy_value,
            max_energy=max_energy_value,
            bar_width=bar_width
        )
        return position_x + bar_width + AFTER_BAR_SPACING

    @staticmethod
    def draw_status_effects(screen, position_y: int, position_x: int, character, max_width: int = None) -> int:
        """
        Отрисовка активных эффектов (пока — заглушка).
        """
        if max_width is None:
            max_width = STATUS_EFFECTS_MAX_WIDTH
            
        try:
            active_effects_list = getattr(character, 'active_effects', [])
            if not active_effects_list:
                return position_x

            effect_names_list = [effect.name[:MAX_EFFECT_NAME_LENGTH] for effect in active_effects_list[:MAX_DISPLAYED_EFFECTS]]
            effects_text = " | ".join(effect_names_list)
            if len(effects_text) > max_width:
                effects_text = effects_text[:max_width - EFFECT_DOTS_LENGTH] + ".."

            screen.addstr(position_y, position_x, effects_text, get_color_pair(COLOR_GRAY) | curses.A_DIM)
            return position_x + len(effects_text) + DEFAULT_SPACING
        except Exception:
            pass
        return position_x

    @classmethod
    def draw_character_row(cls, screen, character, position_y: int, position_x: int, is_player: bool = True):
        """
        Полная отрисовка строки персонажа.
        """
        current_x_position = position_x

        # 1. Имя
        current_x_position = cls.draw_character_name(screen, position_y, current_x_position, character)
        current_x_position += DEFAULT_SPACING
        # 2. HP
        current_x_position = cls.draw_hp_bar(screen, position_y, current_x_position, character, HP_BAR_WIDTH)
        current_x_position += DEFAULT_SPACING

        # 3. Energy
        current_x_position = cls.draw_energy_bar_direct(screen, position_y, current_x_position, character, ENERGY_BAR_WIDTH)
        current_x_position += DEFAULT_SPACING

        # 4. Эффекты
        cls.draw_status_effects(screen, position_y, current_x_position, character, max_width=STATUS_EFFECTS_MAX_WIDTH)