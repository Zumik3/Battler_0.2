# battle_logger.py - Централизованный логгер боя с паттерном Observer

import time
from Config.curses_config import BATTLE_DELAY

class BattleLogger:
    def __init__(self):
        self.log_lines = []
        self.max_lines = 100
        self.observers = []  # Список наблюдателей
        self.message_delay = BATTLE_DELAY  # Задержка между сообщениями
    
    def set_message_delay(self, delay=BATTLE_DELAY):
        """Устанавливает задержку между сообщениями"""
        self.message_delay = max(0, delay)
    
    def get_message_delay(self):
        """Возвращает текущую задержку"""
        return self.message_delay
    
    def add_observer(self, observer):
        """Добавляет наблюдателя"""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer):
        """Удаляет наблюдателя"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, message):
        """Уведомляет всех наблюдателей о новом сообщении"""
        for observer in self.observers:
            try:
                observer(message)
            except:
                pass  # Игнорируем ошибки
    
    def log(self, message):
        """Добавляет сообщение в лог и уведомляет наблюдателей"""
        self.log_lines.append(message)
        if len(self.log_lines) > self.max_lines:
            self.log_lines = self.log_lines[-self.max_lines:]
        self._notify_observers(message)  # Уведомляем наблюдателей
        
        # Автоматическая задержка
        if self.message_delay > 0:
            time.sleep(self.message_delay)

    def log_player_action(self, message):
        """Добавляет сообщение о действии игрока"""
        self.log(f"👤 {message}")
    
    def log_enemy_action(self, message):
        """Добавляет сообщение о действии врага"""
        self.log(message)
    
    def log_system_message(self, message):
        """Добавляет системное сообщение"""
        self.log(f"ℹ️  {message}")
    
    def log_combat_result(self, message):
        """Добавляет сообщение о результате боя"""
        self.log(f"⚔️  {message}")
    
    def log_heal(self, message):
        """Добавляет сообщение о лечении"""
        self.log(f"💖 {message}")
    
    def log_death(self, message):
        """Добавляет сообщение о смерти"""
        self.log(f"💀 {message}")
    
    def get_lines(self):
        """Возвращает копию списка строк лога"""
        return self.log_lines.copy()
    
    def clear(self):
        """Очищает лог"""
        self.log_lines.clear()

    @staticmethod
    def create_log_message(template: str, elements: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """
        Создает цветное сообщение для лога из шаблона и элементов.
        
        :param template: Строка с шаблонами типа %1, %2, %3
        :param elements: Список упорядоченных пар [(ключ, цвет), ...] 
                        где ключ может быть строкой или числом
        :return: Список кортежей (текст, цвет) для цветного вывода
        """
        result = []
        current_pos = 0
        
        while current_pos < len(template):
            # Ищем шаблон %число
            template_start = template.find('%', current_pos)
            
            if template_start == -1:
                # Больше шаблонов нет, добавляем остаток строки
                if current_pos < len(template):
                    result.append((template[current_pos:], 0))
                break
            
            # Добавляем текст до шаблона (включая возможные \n)
            if template_start > current_pos:
                result.append((template[current_pos:template_start], 0))
            
            # Проверяем, является ли следующий символ цифрой
            if (template_start + 1 < len(template) and 
                template[template_start + 1].isdigit()):
                
                # Находим конец номера шаблона
                num_end = template_start + 1
                while num_end < len(template) and template[num_end].isdigit():
                    num_end += 1
                
                template_num = int(template[template_start + 1:num_end])
                
                # Заменяем шаблон на элемент (индексация с 1)
                if 1 <= template_num <= len(elements):
                    key, color = elements[template_num - 1]  # -1 потому что индексация с 0
                    # Преобразуем ключ в строку, если он является числом
                    key_str = str(key) if not isinstance(key, str) else key
                    result.append((key_str, color))
                else:
                    # Если шаблон выходит за границы, оставляем как есть
                    result.append((template[template_start:num_end], 0))
                
                current_pos = num_end
            else:
                # Это просто символ %, добавляем его
                result.append(('%', 0))
                current_pos = template_start + 1
        
        return result

# Глобальный экземпляр логгера
battle_logger = BattleLogger()