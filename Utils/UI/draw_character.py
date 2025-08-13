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

        if character.is_player:
            # Логика для игроков
            current_x_position = DrawCharacter._draw_player_name(screen, position_y, current_x_position, max_x_position, character, 
                                                               white_color_pair, yellow_color_pair, final_name_color_pair)
        else:
            # Логика для монстров
            current_x_position = DrawCharacter._draw_monster_name(screen, position_y, current_x_position, max_x_position, character,
                                                               white_color_pair, yellow_color_pair, final_name_color_pair)

        # Заполняем остаток пробелами
        try:
            while current_x_position < max_x_position:
                screen.addstr(position_y, current_x_position, " ", final_name_color_pair)
                current_x_position += 1
        except curses.error:
            pass

        return current_x_position

    @staticmethod
    def _draw_player_name(screen, position_y: int, position_x: int, max_x_position: int, character,
                         white_color_pair, yellow_color_pair, final_name_color_pair) -> int:
        """Отрисовка имени игрока с классом и уровнем: Роланд [W][1]"""
        current_x_position = position_x
        
        # Расчет длины суффиксов
        suffix_length = 0
        has_class = bool(getattr(character, 'class_icon', ''))
        has_level = getattr(character, 'level', None) is not None
        
        if has_class and has_level:
            # [W][1] = 5 символов
            suffix_length = 5
        elif has_class:
            # [W] = 3 символа
            suffix_length = 3
        elif has_level:
            # [1] = 3 символа
            suffix_length = 3

        # Расчет доступного места для имени
        available_space = max_x_position - current_x_position - suffix_length
        available_space = max(0, available_space)

        # Обрезка имени
        character_name = getattr(character, 'name', '')
        display_name = ""
        
        if available_space >= MIN_LENGTH_FOR_DOTS:
            if len(character_name) <= available_space:
                display_name = character_name
            else:
                display_name = character_name[:available_space - EFFECT_DOTS_LENGTH] + ".."
        elif available_space == MIN_LENGTH_FOR_DOT:
            display_name = "." if len(character_name) > 0 else ""

        # Отрисовка имени
        if display_name:
            try:
                if current_x_position < max_x_position:
                    end_x = min(current_x_position + len(display_name), max_x_position)
                    text_to_draw = display_name[:end_x - current_x_position]
                    screen.addstr(position_y, current_x_position, text_to_draw, final_name_color_pair)
                    current_x_position += len(text_to_draw)
            except curses.error:
                pass

        # Отрисовка суффиксов
        class_icon = getattr(character, 'class_icon', '')
        character_level = getattr(character, 'level', None)
        
        if class_icon and character_level is not None:
            # [W][1]
            level_str = str(character_level)
            if current_x_position + 5 + len(level_str) <= max_x_position:
                try:
                    screen.addstr(position_y, current_x_position, " [", white_color_pair)
                    screen.addstr(position_y, current_x_position + 2, class_icon, 
                                get_color_pair(getattr(character, 'class_icon_color', COLOR_WHITE)))
                    screen.addstr(position_y, current_x_position + 3, "][", white_color_pair)
                    screen.addstr(position_y, current_x_position + 5, level_str, yellow_color_pair)
                    screen.addstr(position_y, current_x_position + 5 + len(level_str), "]", white_color_pair)
                    current_x_position += 6 + len(level_str)
                except curses.error:
                    pass
        elif class_icon:
            # [W]
            if current_x_position + 4 <= max_x_position:
                try:
                    screen.addstr(position_y, current_x_position, " [", white_color_pair)
                    screen.addstr(position_y, current_x_position + 2, class_icon, 
                                get_color_pair(getattr(character, 'class_icon_color', COLOR_WHITE)))
                    screen.addstr(position_y, current_x_position + 3, "]", white_color_pair)
                    current_x_position += 4
                except curses.error:
                    pass
        elif character_level is not None:
            # [1]
            level_str = str(character_level)
            if current_x_position + 3 + len(level_str) <= max_x_position:
                try:
                    screen.addstr(position_y, current_x_position, " [", white_color_pair)
                    screen.addstr(position_y, current_x_position + 2, level_str, yellow_color_pair)
                    screen.addstr(position_y, current_x_position + 2 + len(level_str), "]", white_color_pair)
                    current_x_position += 3 + len(level_str)
                except curses.error:
                    pass

        return current_x_position

    @staticmethod
    def _draw_monster_name(screen, position_y: int, position_x: int, max_x_position: int, character,
                          white_color_pair, yellow_color_pair, final_name_color_pair) -> int:
        """Отрисовка имени монстра с уровнем: Бешеный мутант [1]"""
        current_x_position = position_x
        
        # Расчет длины суффикса
        suffix_length = 0
        has_level = getattr(character, 'level', None) is not None
        if has_level:
            suffix_length = 3  # [1]

        # Расчет доступного места для имени
        available_space = max_x_position - current_x_position - suffix_length
        available_space = max(0, available_space)

        # Обрезка имени
        character_name = getattr(character, 'name', '')
        display_name = ""
        
        if available_space >= MIN_LENGTH_FOR_DOTS:
            if len(character_name) <= available_space:
                display_name = character_name
            else:
                display_name = character_name[:available_space - EFFECT_DOTS_LENGTH] + ".."
        elif available_space == MIN_LENGTH_FOR_DOT:
            display_name = "." if len(character_name) > 0 else ""

        # Отрисовка имени
        if display_name:
            try:
                if current_x_position < max_x_position:
                    end_x = min(current_x_position + len(display_name), max_x_position)
                    text_to_draw = display_name[:end_x - current_x_position]
                    screen.addstr(position_y, current_x_position, text_to_draw, final_name_color_pair)
                    current_x_position += len(text_to_draw)
            except curses.error:
                pass

        # Отрисовка уровня
        character_level = getattr(character, 'level', None)
        if character_level is not None:
            level_str = str(character_level)
            if current_x_position + 3 + len(level_str) <= max_x_position:
                try:
                    screen.addstr(position_y, current_x_position, " [", white_color_pair)
                    screen.addstr(position_y, current_x_position + 2, level_str, yellow_color_pair)
                    screen.addstr(position_y, current_x_position + 2 + len(level_str), "]", white_color_pair)
                    current_x_position += 3 + len(level_str)
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
            bar_color=ENERGY_BAR_COLOR,
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

    # Не забудьте добавить необходимые импорты в начало файла, если их там еще нет
# import curses
# from Config.curses_config import get_color_pair, COLOR_GRAY

    @staticmethod
    def draw_status_effects(screen, position_y: int, position_x: int, character, max_width: int = None) -> int:
        """
        Отрисовывает активные статус-эффекты персонажа в виде иконок.
        
        Args:
            screen: Экран curses для отрисовки.
            position_y: Координата Y для отрисовки.
            position_x: Координата X для отрисовки.
            character: Объект персонажа.
            max_width: Максимальная ширина для отрисовки эффектов.
            
        Returns:
            int: Новая позиция X после отрисовки.
        """
        if max_width is None:
            max_width = STATUS_EFFECTS_MAX_WIDTH
            
        try:
            # Получаем список активных эффектов
            active_effects_list = character.get_active_status_effects()
            
            # Если нет активных эффектов, возвращаем текущую позицию X
            if not active_effects_list:
                return position_x

            # Берем максимум 5 первых эффектов
            displayed_effects = active_effects_list[:5]
            
            # Создаем строку с иконками эффектов, разделенными пробелами
            effect_icons = []
            current_width = 0
            
            for effect in displayed_effects:
                # Предполагаем, что у эффекта есть атрибут icon или используем первый символ имени
                icon = getattr(effect, 'icon', effect.name[0] if effect.name else '?')
                
                # Проверяем, поместится ли еще один эффект
                icon_width = len(icon)
                spacing = 1 if effect_icons else 0  # Пробел перед каждым эффектом, кроме первого
                
                if current_width + spacing + icon_width <= max_width:
                    effect_icons.append(icon)
                    current_width += spacing + icon_width
                else:
                    # Если не помещается, добавляем многоточие
                    if current_width + 3 <= max_width:
                        # Заменяем последний эффект на многоточие, если есть место
                        if effect_icons:
                            effect_icons[-1] = '..' if len('..') <= max_width - (current_width - len(effect_icons[-1])) else '.'
                        else:
                            effect_icons.append('.' * min(3, max_width))
                    break
            
            # Объединяем иконки пробелами
            effects_text = ' '.join(effect_icons) if effect_icons else ''
            
            # Отрисовываем иконки эффектов на экране
            if effects_text:
                screen.addstr(position_y, position_x, effects_text)
            
            # Возвращаем новую позицию X для следующего элемента интерфейса
            return position_x + len(effects_text) + DEFAULT_SPACING
            
        except Exception as e:
            # В случае ошибки возвращаем исходную позицию X
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
        return current_x_position