# Characters/Status_effects/status_effect.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from Characters.character import Character

class StatusEffect(ABC):
    """Абстрактный базовый класс для статус-эффектов."""
    
    def __init__(self, name: str, duration: int, description: str = "", icon: str = ""):
        """
        Инициализация статус-эффекта.
        
        :param name: Название эффекта
        :param duration: Длительность эффекта в раундах (-1 для постоянных)
        :param description: Описание эффекта
        :param icon: Иконка эффекта
        """
        self.name = name
        self.duration = duration  # -1 означает постоянный эффект
        self.description = description
        self.icon = icon
        self.applied = False  # Флаг для отслеживания первого применения
        
    @abstractmethod
    def apply_effect(self, target: Character) -> Dict[str, Any]:
        """
        Применяет эффект к цели при первом наложении.
        Вызывается только один раз при применении эффекта.
        
        :param target: Цель эффекта (персонаж)
        :return: Словарь с информацией об эффекте (сообщения, изменения статов и т.д.)
        """
        pass
    
    @abstractmethod
    def update_effect(self, target: Character) -> Dict[str, Any]:
        """
        Обновляет эффект на цели каждый раунд.
        Вызывается каждый раунд, пока эффект активен.
        
        :param target: Цель эффекта (персонаж)
        :return: Словарь с информацией об эффекте (урон, сообщения и т.д.)
        """
        pass
    
    @abstractmethod
    def remove_effect(self, target: Character) -> Dict[str, Any]:
        """
        Удаляет эффект с цели.
        Вызывается при окончании действия эффекта или его преждевременном удалении.
        
        :param target: Цель эффекта (персонаж)
        :return: Словарь с информацией об удалении эффекта (сообщения и т.д.)
        """
        pass
    
    def tick(self, target: Character) -> Dict[str, Any]:
        """
        Обрабатывает эффект в каждом раунде.
        Управляет длительностью и вызывает соответствующие методы.
        
        :param target: Цель эффекта (персонаж)
        :return: Словарь с результатами обработки эффекта
        """
        if not self.applied:
            self.applied = True

        
        if self.duration > 0:
            self.duration -= 1
            
        result = self.update_effect(target)
            
        return result
    
    def is_expired(self) -> bool:
        """
        Проверяет, истек ли срок действия эффекта.
        
        :return: True если эффект истек, False если еще активен
        """
        return self.duration == 0
    
    def get_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию об эффекте.
        
        :return: Словарь с информацией об эффекте
        """
        return {
            'name': self.name,
            'duration': self.duration,
            'description': self.description,
            'icon': self.icon,
            'applied': self.applied
        }
        
    def extend_duration(self) -> None:
        """
        Продлевает действие эффекта.
        
        :param rounds: Количество раундов для продления
        """
        if self.duration > 0:
            self.duration = self.base_duration
                
    def set_duration(self, duration: int) -> None:
        """
        Устанавливает новую длительность эффекта.
        
        :param duration: Новая длительность эффекта
        """
        self.duration = duration


class StackableStatusEffect(StatusEffect):
    """Базовый класс для стакающихся статус-эффектов."""
    
    def __init__(self, name: str, duration: int, description: str = "", icon: str = ""):
        """
        Инициализация стакающегося эффекта.
        
        :param name: Название эффекта
        :param duration: Базовая длительность эффекта в раундах
        :param description: Описание эффекта
        :param icon: Иконка эффекта
        """
        super().__init__(name=name, duration=duration, description=description, icon=icon)
        self.stacks: int = 0
        self.max_stacks: int = 5  # Максимальное количество стаков по умолчанию
        
    def add_stack(self, stacks: int = 1) -> bool:
        """
        Добавляет стаки к эффекту.
        
        :param stacks: Количество стаков для добавления
        :return: True если стаки добавлены, False если достигнут максимум
        """
        if self.stacks < self.max_stacks:
            self.stacks = min(self.stacks + stacks, self.max_stacks)
            # Продлеваем длительность при добавлении стаков
            self.extend_duration()
            return True
        return False
    
    def remove_stack(self, stacks: int = 1) -> int:
        """
        Удаляет стаки из эффекта.
        
        :param stacks: Количество стаков для удаления
        :return: Количество реально удаленных стаков
        """
        removed_stacks = min(stacks, self.stacks)
        self.stacks = max(1, self.stacks - stacks)  # Минимум 1 стак
        return removed_stacks
    
    def get_stack_multiplier(self) -> float:
        """
        Возвращает множитель эффекта на основе количества стаков.
        
        :return: Множитель (1.0 для 1 стака, 1.5 для 2 стаков и т.д.)
        """
        return 1.0 + (self.stacks - 1) * 0.5  # Каждый дополнительный стак дает +50%
    
    def get_total_effect_value(self, base_value: int) -> int:
        """
        Рассчитывает итоговое значение эффекта с учетом стаков.
        
        :param base_value: Базовое значение эффекта
        :return: Итоговое значение с учетом стаков
        """
        return int(base_value * self.get_stack_multiplier())
    
    def get_stacks_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о стаках эффекта.
        
        :return: Словарь с информацией о стаках
        """
        return {
            'stacks': self.stacks,
            'max_stacks': self.max_stacks,
            'multiplier': self.get_stack_multiplier()
        }
    
    def reset_stacks(self) -> None:
        """Сбрасывает количество стаков до 1."""
        self.stacks = 1
    
    def is_max_stacks(self) -> bool:
        """Проверяет, достигнуто ли максимальное количество стаков."""
        return self.stacks >= self.max_stacks
