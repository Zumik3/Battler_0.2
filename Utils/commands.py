# commands.py - Система команд

import curses
from Battle.battle_logic import simulate_battle
from Battle.battle_logger import battle_logger
from Config.curses_config import BATTLE_DELAY
from Characters.char_utils import create_enemies
from Inventory.inventory import get_inventory
from Utils.UI.Statistics.statistics_window import GlobalStatsWindow
from Utils.display import display_inventory_screen
from Utils.UI.Skills.skills_window import display_abilities_screen

class CommandHandler:
    def __init__(self, players, enemies, stdscr=None):
        self.players = players
        self.enemies = enemies
        self.stdscr = stdscr
        self.commands = {
            'go': self.start_battle,
            'start': self.start_battle,
            'fight': self.start_battle,
            'help': self.show_help,
            'h': self.show_help,
            'clear': self.clear_log,
            'cls': self.clear_log,
            'exit': self.exit_game,
            'quit': self.exit_game,
            'q': self.exit_game,
            'inventory': self.open_inventory,
            'inv': self.open_inventory,
            'i': self.open_inventory,
            'skills': self.open_skills,
            'abilities': self.open_skills,
            'abil': self.open_skills,
            'stat': self.open_statistics  # Тестовая команда
        }
    
    def process_input(self, key):
        """Обрабатывает ввод пользователя - теперь через одиночные клавиши"""
        try:
            if key == ord('q') or key == ord('Q'):
                return self.exit_game()
            elif key == 10 or key == 13:  # Enter
                return self.start_battle()
            elif key == ord('i') or key == ord('I'):
                self.open_inventory()
                return False
            elif key == ord('s') or key == ord('S'):
                self.open_skills()
                return False
            elif key == curses.KEY_F12:
                self.open_statistics()
                return False
            elif key == ord('h') or key == ord('H'):
                self.show_help()
                return False
            elif key == ord('c') or key == ord('C'):
                self.clear_log()
                return False
            elif key == 27:  # ESC
                return True  # Выход
            elif key == 3:   # Ctrl+C
                return True  # Выход
        except Exception:
            pass
        return False  # Продолжать
    
    def execute_command(self, command):
        """Выполняет команду"""
        cmd = command.strip().lower()
        
        if cmd in self.commands:
            return self.commands[cmd]()
        else:
            battle_logger.log_system_message(f"❌ Неизвестная команда: {command}")
            battle_logger.log_system_message("Введите 'help' для списка команд")
            return False  # Не выходить из игры
    
    def start_battle(self):
        """Начинает бой"""
        try:
            self.enemies = create_enemies(self.players)
            result = simulate_battle(self.players, self.enemies)
            return False  # Не выходить из игры
            
        except Exception as e:
            battle_logger.log_system_message(f"💥 Ошибка в бою: {str(e)}")
            return False  # Не выходить из игры
    
    def show_help(self):
        """Показывает помощь"""
        battle_logger.set_message_delay(0)
        battle_logger.log_system_message("📖 Доступные команды (нажмите клавишу):")
        battle_logger.log_system_message("  Enter - начать бой")
        battle_logger.log_system_message("  I - открыть инвентарь")
        battle_logger.log_system_message("  S - открыть умения")
        battle_logger.log_system_message("  H - показать помощь")
        battle_logger.log_system_message("  C - очистить лог")
        battle_logger.log_system_message("  T - тестовое окно")
        battle_logger.log_system_message("  Q - выйти из игры")
        battle_logger.set_message_delay(BATTLE_DELAY)
        return False  # Не выходить из игры
    
    def clear_log(self):
        """Очищает лог"""
        battle_logger.clear()
        battle_logger.log_system_message("🗑️  Лог очищен")
        return False  # Не выходить из игры
    
    def exit_game(self):
        """Выходит из игры"""
        battle_logger.log_system_message("👋 До новых встреч!")
        return True  # Выход из игры
    
    def open_inventory(self):
        """Открывает инвентарь"""
        if self.stdscr:  # Проверяем, что экран доступен
            try:
                display_inventory_screen(self.stdscr, self.players)
                #inventory = get_inventory()
                #window = InventoryWindow(self.stdscr, self.players, inventory)
                #window.run()
            except Exception as e:
                battle_logger.log_system_message(f"❌ Ошибка открытия инвентаря: {str(e)}")
        else:
            battle_logger.log_system_message("❌ Невозможно открыть инвентарь в текущем режиме")
        return False  # Не выходить из игры
    
    def open_skills(self):
        """Открывает дерево умений"""
        if self.stdscr:  # Проверяем, что экран доступен
            try:
                display_abilities_screen(self.stdscr, self.players)
            except Exception as e:
                battle_logger.log_system_message(f"❌ Ошибка открытия умений: {str(e)}")
        else:
            battle_logger.log_system_message("❌ Невозможно открыть умения в текущем режиме")
        return False  # Не выходить из игры
    
    def open_statistics(self):
        """Открывает тестовое окно"""
        if self.stdscr:  # Проверяем, что экран доступен
            try:
                window = GlobalStatsWindow(self.stdscr)
                window.run()
            except Exception as e:
                battle_logger.log_system_message(f"❌ Ошибка открытия статистики: {str(e)}")
        else:
            battle_logger.log_system_message("❌ Невозможно открыть статистику в текущем режиме")
        return False  # Не выходить из игры
    
    def get_input(self):
        """Возвращает текущую строку ввода (пустая для новой системы)"""
        return ""
    
    def get_available_commands(self):
        """Возвращает список доступных команд"""
        return list(self.commands.keys())

# Глобальный обработчик команд (будет инициализирован в main)
command_handler = None