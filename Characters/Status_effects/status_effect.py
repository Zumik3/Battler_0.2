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
            return self.apply_effect(target)
        
        if self.duration > 0:
            self.duration -= 1
            
        result = self.update_effect(target)
        
        # Проверяем, закончился ли эффект
        #if self.duration == 0:
        #    removal_result = self.remove_effect(target)
        #    result.update(removal_result)
            
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
        
    def extend_duration(self, rounds: int) -> None:
        """
        Продлевает действие эффекта.
        
        :param rounds: Количество раундов для продления
        """
        if self.duration > 0 or self.duration == -1:
            if self.duration != -1:  # Не продлеваем постоянные эффекты
                self.duration += rounds
                
    def set_duration(self, duration: int) -> None:
        """
        Устанавливает новую длительность эффекта.
        
        :param duration: Новая длительность эффекта
        """
        self.duration = duration