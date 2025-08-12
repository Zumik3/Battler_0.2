# characters/abilities/misc/critical_strike.py

from typing import Any, Dict
from Characters.Abilities.abilities import PassiveAbility

class CriticalStrike(PassiveAbility):
    """Пассивная способность: Критический удар - повышает шанс критического удара"""
    
    def __init__(self) -> None:
        super().__init__(
            name="Критический удар",
            type=3,  # Тип для пассивных способностей
            description="Повышает шанс нанесения критического удара при атаках",
            icon="⚡"
        )
        # Базовый бонус за уровень
        self.base_critical_bonus: float = 0.05  # 5% за уровень
        self.max_level: int = 5  # Максимальный уровень способности
    
    def level_up(self) -> int:
        """Повышает уровень способности на 1, но не выше максимального"""
        if self.level < self.max_level:
            self.level += 1
        return self.level
    
    def set_level(self, level: int) -> int:
        """Устанавливает уровень способности с ограничением по максимальному уровню"""
        self.level = max(0, min(level, self.max_level))
        return self.level
    
    def get_current_bonus(self) -> float:
        """Возвращает текущий бонус к критическому шансу"""
        return self.base_critical_bonus * self.level
    
    def apply_effect(self, character: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Применяет эффект пассивной способности.
        Повышает шанс критического удара персонажа.
        """

        current_bonus = self.get_current_bonus()
    
        # Возвращаем информацию об эффекте
        return {
            'effect_applied': True,
            'critical_bonus': current_bonus,
            'current_level': self.level,
            'max_level': self.max_level,
            'character': character
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает информацию о пассивной способности."""
        info = super().get_info()
        info.update({
            'current_bonus': self.get_current_bonus(),
            'base_critical_bonus': self.base_critical_bonus,
            'max_level': self.max_level
        })
        return info
    
    def get_detailed_description(self) -> str:
        """Возвращает подробное описание способности с текущими бонусами"""
        current_bonus = self.get_current_bonus()
        return f"{self.description}\nБонус: +{current_bonus*100:.0f}% к шансу критического удара\nУровень: {self.level}/{self.max_level}"