# commands.py - Система команд

import curses
from Battle.battle_logic import simulate_battle
from Battle.battle_logger import battle_logger
from Config.curses_config import BATTLE_DELAY
from Characters.char_utils import create_enemies

class CommandHandler:
    def __init__(self, players, enemies, stdscr=None):
        self.players = players
        self.enemies = enemies
        self.stdscr = stdscr
        self.input_str = ""
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
            'q': self.exit_game
        }
    
    def process_input(self, key):
        """Обрабатывает ввод пользователя"""
        if isinstance(key, str) and key.isprintable():
            self.input_str += key
            return None  # Продолжаем ввод
        elif key == curses.KEY_BACKSPACE or key == 127 or key == "\x7f":
            self.input_str = self.input_str[:-1]
            return None  # Продолжаем ввод
        elif key == "\n" or key == "\r":
            if self.input_str.strip():
                cmd = self.input_str.strip().lower()
                self.input_str = ""  # Очищаем ввод
                return self.execute_command(cmd)
            else:
                self.input_str = ""  # Очищаем пустой ввод
                return False  # Не выходить
        elif key == 27:  # ESC
            return True  # Выход
        elif key == 3:   # Ctrl+C
            return True  # Выход
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
        battle_logger.log_system_message("📖 Доступные команды:")
        battle_logger.log_system_message("  go/start/fight - начать бой")
        battle_logger.log_system_message("  help/h - показать помощь")
        battle_logger.log_system_message("  clear/cls - очистить лог")
        battle_logger.log_system_message("  exit/quit/q - выйти из игры")
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
    
    def get_input(self):
        """Возвращает текущую строку ввода"""
        return self.input_str
    
    def get_available_commands(self):
        """Возвращает список доступных команд"""
        return list(self.commands.keys())

# Глобальный обработчик команд (будет инициализирован в main)
command_handler = None