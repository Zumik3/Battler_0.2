# Utils/UI/event_window.py
"""Окно отображения игрового события/боя."""

import curses
import time
import uuid
from typing import List, Optional, TYPE_CHECKING

# Импорты внутри метода, чтобы избежать циклических импортов
# from Battle.battle_logger import battle_logger
# from Battle.battle_statistics import get_battle_statistics
# from Battle.rewards import BattleRewards
# from Config.game_config import MAX_ROUNDS
# from Battle.round_logic import battle_round

if TYPE_CHECKING:
    from Characters.player_classes import Player
    from Utils.command_handler import CommandHandler

from Utils.UI.window import Window
from Utils.UI.key_hints import BattleHints
from Battle.battle_logger import battle_logger
from Characters.char_utils import create_enemies


class EventWindow(Window):
    """Окно отображения игрового события/боя."""

    def __init__(self, stdscr: curses.window, players: List['Player']) -> None:
        """Инициализация окна события."""
        super().__init__(stdscr)
        self.players: List['Player'] = players
        self.enemies: List = create_enemies(players)
        # Импортируем CommandHandler внутри, чтобы избежать циклических импортов
        from Utils.command_handler import CommandHandler
        self.command_handler: CommandHandler = CommandHandler(
            players=self.players,
            enemies=self.enemies,
            stdscr=self.stdscr
        )
        self.hint_class = BattleHints()
        self.battle_started = False # Флаг для отслеживания запуска боя


    def get_header_text(self) -> str:
        """Возвращает текст заголовка окна."""
        return "⚔️ БИТВА"

    def _display_body(self) -> None:
        """Отображение основного содержимого окна - лог боя."""
        try:
            height, width = self.stdscr.getmaxyx()
            log_start_y = 3
            max_log_lines = max(1, height - log_start_y - 3)

            if hasattr(battle_logger, 'log_lines'):
                start_index = max(0, len(battle_logger.log_lines) - max_log_lines)
                lines_to_display = battle_logger.log_lines[start_index:]

                for i, line in enumerate(lines_to_display):
                    y_pos = log_start_y + i
                    if y_pos >= height - 3:
                        break
                    if isinstance(line, str):
                        self.stdscr.addstr(y_pos, 2, line[:width - 4], curses.A_NORMAL)
                    elif isinstance(line, tuple) and len(line) >= 2:
                        text, attr = line[0], line[1]
                        self.stdscr.addstr(y_pos, 2, text[:width - 4], attr)
            else:
                self.stdscr.addstr(log_start_y, 2, "Лог боя недоступен", curses.A_DIM)

        except curses.error:
            pass
        except Exception as e:
            battle_logger.log_system_message(f"❌ Ошибка отрисовки тела EventWindow: {e}")

    def _handle_input(self, key: int) -> bool:
        """Обработка пользовательского ввода.
        Args:
            key: Код нажатой клавиши.
        Returns:
            bool: True, если окно должно закрыться (например, по 'q'), иначе False.
        """
        # Обрабатываем только команды выхода ('q', 'Q', ESC)
        # Пробел больше не нужен для продолжения боя
        try:
            if key in [ord('q'), ord('Q'), 27]: # ESC, Q
                # Устанавливаем флаг выхода в command_handler.context
                if self.command_handler.context:
                    self.command_handler.context.set_exit_flag(True)
                return True # Сигнал для выхода из окна/состояния
            # Игнорируем другие клавиши, включая пробел
            return False
        except Exception as e:
            battle_logger.log_system_message(f"❌ Ошибка обработки ввода EventWindow: {e}")
            return False

    def render(self) -> None:
        """Отрисовывает содержимое окна события/боя.
        Использует внутренний self.stdscr.
        Этот метод необходим для совместимости с GameContext/GameState."""
        try:
            # Очищаем окно перед отрисовкой
            self.stdscr.clear()
            # Вызываем стандартные методы отрисовки из Window
            self._display_header() # Отрисовка заголовка
            self._display_body()   # Отрисовка тела (лог боя)
            self._display_footer() # Отрисовка подсказок
            # Обновляем экран
            self.stdscr.refresh()
        except curses.error:
            # Игнорируем ошибки отрисовки curses
            pass
        except Exception as e:
            # Можно добавить логирование других ошибок
            battle_logger.log_system_message(f"❌ Критическая ошибка отрисовки EventWindow: {e}")
            pass

    def run(self) -> None:
        """Запускает основной цикл окна.
        Переопределяем, чтобы добавить автоматический запуск боя и очистку ресурсов."""
        try:
            if not self.battle_started:
                self.battle_started = True
                # Очищаем лог перед началом нового боя
                if hasattr(battle_logger, 'log_lines'):
                    battle_logger.log_lines.clear()
                battle_logger.log("")
                battle_logger.log("🏁 БОЙ НАЧИНАЕТСЯ!")

                # Запускаем автоматический бой
                self.run_automatic_battle()

            else:
                # Если run вызван снова (например, после перерисовки), просто продолжаем цикл отображения
                super().run()

        finally:
            try:
                pass
            except Exception as e:
                pass

    def run_automatic_battle(self) -> None:
        """Запускает автоматический бой, обновляя экран после каждого раунда."""
        # Импортируем необходимые функции и константы
        from Battle.battle_statistics import get_battle_statistics
        from Battle.rewards import BattleRewards
        from Config.game_config import MAX_ROUNDS
        from Battle.round_logic import battle_round
        from Config.curses_config import ROUND_DELAY_MS

        # Подготовка перед боем
        from Battle.battle_simulator import BattleSimulator
        BattleSimulator.pre_battle_setup(self.players, self.enemies)

        # Начало записи статистики
        battle_id = str(uuid.uuid4())
        stats = get_battle_statistics()
        stats.start_battle_tracking(battle_id, self.players, self.enemies)

        # Начало боя
        battle_result = "draw" # По умолчанию - ничья

        # Основной цикл боя
        for round_num in range(1, MAX_ROUNDS + 1):
            # Проверка, не завершился ли бой ранее (например, пользователь нажал 'q')
            if self.command_handler.context and self.command_handler.context.should_exit():
                battle_result = "interrupted"
                break

            # Отображаем разделитель раундов
            battle_logger.log(f"--- Раунд {round_num} ---")

            # Выполняем один раунд
            round_result = battle_round(self.players, self.enemies, battle_logger)

            # Проверяем результат раунда
            if round_result == "win":
                battle_result = "win"
                battle_logger.log("🎉 ПОБЕДА! Все враги повержены!")
                break
            elif round_result == "loss":
                battle_result = "loss"
                # Сообщение уже залогировано в battle_round
                break

            # Обновляем кулдауны способностей
            from Battle.round_logic import post_round_processing
            post_round_processing(self.players, self.enemies)

            # Обновляем экран
            self.render()
            self.stdscr.refresh()

            # Пауза между раундами
            delay_ms = ROUND_DELAY_MS

            # Используем getch с таймаутом для неблокирующего ожидания
            self.stdscr.timeout(delay_ms)
            key = self.stdscr.getch()
            self.stdscr.timeout(-1)

            # Проверяем ввод на случай досрочного выхода ('q')
            if key != -1: # Если была нажата клавиша
                if self._handle_input(key): # _handle_input возвращает True для выхода ('q')
                    battle_result = "interrupted"
                    battle_logger.log("⚠️ Бой прерван пользователем.")
                    break # Выходим из цикла

        # Если цикл завершился без победы/поражения
        if battle_result == "draw":
            battle_logger.log("⚔️ Бой завершен (ничья или превышено максимальное количество раундов).")

        # Завершение боя
        BattleSimulator.post_battle_processing(self.players, self.enemies, battle_result)

        # Обновляем экран после завершения
        self.render()
        self.stdscr.refresh()

        # Сообщаем, что бой завершен (например, для EventState)
        battle_logger.log("Нажмите 'Q' или ESC для возврата в меню.")
