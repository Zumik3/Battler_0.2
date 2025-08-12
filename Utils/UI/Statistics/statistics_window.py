# stats_windows.py

import curses
import abc
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from Battle.battle_statistics import BattleSummaryRecord, CombatActionRecord, GameTotalsRecord

from Battle.battle_statistics import get_battle_statistics
from Utils.UI.window import AbstractWindow
from Utils.UI.key_hints import STATISTICS_HINTS

class GlobalStatsWindow(AbstractWindow):
    """Окно глобальной статистики"""
    
    def __init__(self, stdscr) -> None:
        super().__init__(stdscr)
        self.battle_stats = get_battle_statistics()
        self.selected_battle_index: int = 0
        self.battle_summaries: List['BattleSummaryRecord'] = []
        self.hint_class = STATISTICS_HINTS
    
    def get_header_text(self) -> str:
        return "📊 ГЛОБАЛЬНАЯ СТАТИСТИКА"
    
    def _display_body(self) -> None:
        """Отображение основного содержимого - глобальная статистика и список битв"""
        if self.height < 5:
            return
            
        # Получаем данные
        game_totals = self.battle_stats.get_current_game_totals()
        self.battle_summaries = self.battle_stats.get_battle_summaries()
        
        # Отображаем глобальную статистику (верхняя часть)
        self._display_global_stats(game_totals, 2)
        
        # Отображаем разделитель
        separator_y = min(12, self.height - 3)
        if separator_y > 3:
            try:
                self.stdscr.addstr(separator_y, 0, "─" * (self.width - 1), self.get_separator_style())
                if separator_y + 1 < self.height - 2:
                    self.stdscr.addstr(separator_y + 1, max(0, self.width // 2 - 7), "Список битв", curses.A_BOLD)
            except curses.error:
                pass
        
        # Отображаем список битв (нижняя часть)
        list_start_y = separator_y + 3
        if list_start_y < self.height - 2:
            self._display_battle_list(list_start_y)
    
    def _display_global_stats(self, game_totals: 'GameTotalsRecord', start_y: int) -> None:
        """Отображение глобальной статистики"""
        if self.height <= start_y:
            return
            
        stats_lines = [
            f"Всего боёв: {game_totals.total_battles}",
            f"Побед: {game_totals.total_victories} | Поражений: {game_totals.total_defeats}",
            f"Процент побед: {self._calculate_win_rate(game_totals):.1f}%",
            f"Общий нанесённый урон: {game_totals.total_damage_dealt}",
            f"Общий полученный урон: {game_totals.total_damage_taken}",
            f"Общее лечение: {game_totals.total_healing_done}",
            f"Максимальный урон в битве: {game_totals.most_damage_in_single_battle}",
            f"Самая длинная битва: {game_totals.longest_battle_rounds} раундов"
        ]
        
        for i, line in enumerate(stats_lines):
            if start_y + i >= self.height - 3:
                break
            try:
                self.stdscr.addstr(start_y + i, 2, line[:self.width - 4], curses.A_NORMAL)
            except curses.error:
                pass
    
    def _calculate_win_rate(self, game_totals: 'GameTotalsRecord') -> float:
        """Вычисляет процент побед"""
        if game_totals.total_battles == 0:
            return 0.0
        return (game_totals.total_victories / game_totals.total_battles) * 100
    
    def _display_battle_list(self, start_y: int) -> None:
        """Отображение списка проведённых битв"""
        if not self.battle_summaries:
            if start_y < self.height - 3:
                try:
                    self.stdscr.addstr(start_y, 2, "Нет проведённых боёв", curses.A_DIM)
                except curses.error:
                    pass
            return
        
        # Отображаем битвы с выделением выбранной
        max_battles_to_show = max(1, self.height - start_y - 3)
        
        for i, battle in enumerate(self.battle_summaries[:max_battles_to_show]):
            if start_y + i >= self.height - 3:
                break
                
            y_pos = start_y + i
            battle_text = f"Битва {battle.battle_id[:10]} - Раундов: {battle.total_rounds} - "
            battle_text += "Победа" if battle.player_victory else "Поражение"
            
            try:
                if i == self.selected_battle_index:
                    # Выделенная битва
                    self.stdscr.addstr(y_pos, 2, f"> {battle_text[:self.width - 6]}", 
                                     curses.A_BOLD | curses.A_REVERSE)
                else:
                    # Обычная битва
                    self.stdscr.addstr(y_pos, 2, f"  {battle_text[:self.width - 6]}", 
                                     curses.A_NORMAL)
            except curses.error:
                pass
    
    def _handle_input(self, key: int) -> bool:
        """Обработка ввода для окна глобальной статистики"""
        if key in [ord('q'), ord('Q'), ord('e'), ord('E'), 27]:  # ESC, q, e
            return True
        elif key == curses.KEY_UP:
            if self.battle_summaries:
                self.selected_battle_index = max(0, self.selected_battle_index - 1)
        elif key == curses.KEY_DOWN:
            if self.battle_summaries:
                self.selected_battle_index = min(len(self.battle_summaries) - 1, 
                                               self.selected_battle_index + 1)
        elif key in [10, 13]:  # Enter
            # Открытие окна деталей выбранной битвы
            if self.battle_summaries and 0 <= self.selected_battle_index < len(self.battle_summaries):
                selected_battle = self.battle_summaries[self.selected_battle_index]
                battle_detail_window = BattleDetailWindow(self.stdscr, selected_battle)
                battle_detail_window.run()
        elif key == curses.KEY_RESIZE:
            return False  # Продолжить работу при ресайзе
        
        return False


class BattleDetailWindow(AbstractWindow):
    """Окно деталей конкретной битвы"""
    
    def __init__(self, stdscr, battle_record: 'BattleSummaryRecord') -> None:
        super().__init__(stdscr)
        self.battle_record = battle_record
        self.battle_stats = get_battle_statistics()
        self.selected_action_index: int = 0
        self.detailed_actions: List['CombatActionRecord'] = []
        self.hint_class = STATISTICS_HINTS
    
    def get_header_text(self) -> str:
        return f"📊 ДЕТАЛИ БИТВЫ {self.battle_record.battle_id}"
    
    def _display_body(self) -> None:
        """Отображение основного содержимого - общая информация о битве и детальные записи"""
        if self.height < 5:
            return
            
        # Получаем детальные записи для этой битвы
        self.detailed_actions = self.battle_stats.get_detailed_records(self.battle_record.battle_id)
        
        # Отображаем общую информацию о битве (верхняя часть)
        self._display_battle_summary(2)
        
        # Отображаем разделитель
        separator_y = min(10, self.height - 3)
        if separator_y > 4:
            try:
                self.stdscr.addstr(separator_y, 0, "─" * (self.width - 1), self.get_separator_style())
                if separator_y + 1 < self.height - 2:
                    self.stdscr.addstr(separator_y + 1, max(0, self.width // 2 - 12), "Детали боевых действий", curses.A_BOLD)
            except curses.error:
                pass
        
        # Отображаем детальные записи (нижняя часть)
        list_start_y = separator_y + 3
        if list_start_y < self.height - 2:
            self._display_detailed_actions(list_start_y)
    
    def _display_battle_summary(self, start_y: int) -> None:
        """Отображение общей информации о битве"""
        if self.height <= start_y:
            return
            
        summary_lines = [
            f"Результат: {'Победа' if self.battle_record.player_victory else 'Поражение'}",
            f"Всего раундов: {self.battle_record.total_rounds}",
            f"Игроки: {', '.join(self.battle_record.player_names)}",
            f"Враги: {', '.join(self.battle_record.enemy_names)}",
            f"Урон игроков: {self.battle_record.total_damage_dealt_by_players}",
            f"Урон по игрокам: {self.battle_record.total_damage_dealt_to_players}",
            f"Лечение: {self.battle_record.total_healing_done}",
            f"Критические удары: {self.battle_record.critical_hits_count}",
            f"Уклонения: {self.battle_record.dodges_count}"
        ]
        
        for i, line in enumerate(summary_lines):
            if start_y + i >= self.height - 3:
                break
            try:
                self.stdscr.addstr(start_y + i, 2, line[:self.width - 4], curses.A_NORMAL)
            except curses.error:
                pass
    
    def _display_detailed_actions(self, start_y: int) -> None:
        """Отображение детальных боевых действий"""
        if not self.detailed_actions:
            if start_y < self.height - 3:
                try:
                    self.stdscr.addstr(start_y, 2, "Нет детальных записей", curses.A_DIM)
                except curses.error:
                    pass
            return
        
        # Отображаем действия с выделением выбранного
        max_actions_to_show = max(1, self.height - start_y - 3)
        
        for i, action in enumerate(self.detailed_actions[:max_actions_to_show]):
            if start_y + i >= self.height - 3:
                break
                
            y_pos = start_y + i
            action_text = f"Раунд {action.round_number}: {action.attacker_name} -> {action.target_name} ({action.ability_name})"
            if action.damage_dealt > 0:
                action_text += f" Урон: {action.damage_dealt}"
            if action.heal_amount > 0:
                action_text += f" Лечение: {action.heal_amount}"
            if action.is_critical:
                action_text += " [КРИТ]"
            if action.is_dodge:
                action_text += " [УКЛОНЕНИЕ]"
            
            try:
                if i == self.selected_action_index:
                    # Выделенное действие
                    self.stdscr.addstr(y_pos, 2, f"> {action_text[:self.width - 6]}", 
                                     curses.A_BOLD | curses.A_REVERSE)
                else:
                    # Обычное действие
                    self.stdscr.addstr(y_pos, 2, f"  {action_text[:self.width - 6]}", 
                                     curses.A_NORMAL)
            except curses.error:
                pass
    
    def _handle_input(self, key: int) -> bool:
        """Обработка ввода для окна деталей битвы"""
        if key in [ord('q'), ord('Q'), ord('e'), ord('E'), 27]:  # ESC, q, e
            return True
        elif key == curses.KEY_UP:
            if self.detailed_actions:
                self.selected_action_index = max(0, self.selected_action_index - 1)
        elif key == curses.KEY_DOWN:
            if self.detailed_actions:
                self.selected_action_index = min(len(self.detailed_actions) - 1, 
                                               self.selected_action_index + 1)
        elif key == curses.KEY_RESIZE:
            return False  # Продолжить работу при ресайзе
        
        return False


# Функция для запуска окна глобальной статистики
def display_global_stats_screen(stdscr) -> None:
    """Отображает экран глобальной статистики"""
    window = GlobalStatsWindow(stdscr)
    window.run()