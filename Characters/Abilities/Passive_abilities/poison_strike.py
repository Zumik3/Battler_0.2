# Characters/Abilities/Passive_abilities/poison_strike.py
import random
from typing import Any, Dict, List
from Characters.Abilities.abilities import PassiveAbility
from Characters.Status_effects.poison_effect import PoisonEffect

class PoisonStrike(PassiveAbility):
    """Пассивная способность: Отравляющий удар - с шансом накладывает отравление при атаке"""
    
    def __init__(self) -> None:
        super().__init__(
            name="Отравляющий удар",
            type=3,  # Тип для пассивных способностей
            description="С шансом накладывает эффект отравления при успешной атаке",
            icon="☠️"
        )
        # Параметры способности
        self.base_chance: float = 0.15  # Базовый шанс 15%
        self.chance_per_level: float = 0.05  # +5% за уровень
        self.poison_duration: int = 3  # Длительность отравления
        self.poison_damage: int = 4  # Урон от отравления за ход
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
    
    def get_current_chance(self) -> float:
        """Возвращает текущий шанс наложения отравления"""
        return min(self.base_chance + (self.chance_per_level * (self.level - 1)), 0.5)  # Максимум 50%
    
    def apply_effect(self, character: Any, target: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Применяет эффект пассивной способности - пытается наложить отравление.
        Вызывается после успешной атаки.
        """
        
        # Проверяем уровень способности
        if self.level <= 0:
            return {
                'effect_applied': False,
                'reason': 'ability_not_learned'
            }
        
        # Проверяем, есть ли цель
        if target is None:
            return {
                'effect_applied': False,
                'reason': 'no_target'
            }
        
        # Проверяем, жив ли target
        if not hasattr(target, 'is_alive') or not target.is_alive():
            return {
                'effect_applied': False,
                'reason': 'target_dead'
            }
        
        # Рассчитываем шанс наложения отравления
        current_chance = self.get_current_chance()
        
        # Проверяем, сработал ли эффект
        if random.random() < current_chance:
            # Создаем эффект отравления
            poison_effect = PoisonEffect(
                duration=self.poison_duration,
                damage_per_turn=self.poison_damage,
                chance=current_chance
            )
            
            # Применяем эффект к цели
            result = target.add_status_effect(poison_effect)
            
            return {
                'effect_applied': True,
                'poison_applied': True,
                'chance': current_chance,
                'target': target.name,
                'effect_instance': poison_effect,
                'message': result.get('message', f'{target.name} отравлен!')
            }
        else:
            return {
                'effect_applied': True,
                'poison_applied': False,
                'chance': current_chance,
                'target': target.name,
                'message': 'Отравление не сработало'
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает информацию о пассивной способности."""
        info = super().get_info()
        info.update({
            'current_chance': self.get_current_chance(),
            'base_chance': self.base_chance,
            'chance_per_level': self.chance_per_level,
            'poison_duration': self.poison_duration,
            'poison_damage': self.poison_damage,
            'max_level': self.max_level
        })
        return info
    
    def get_detailed_description(self) -> str:
        """Возвращает подробное описание способности с текущими параметрами"""
        current_chance = self.get_current_chance()
        return (f"{self.description}\n"
                f"Шанс: {current_chance*100:.0f}%\n"
                f"Урон от отравления: {self.poison_damage} за ход\n"
                f"Длительность: {self.poison_duration} раунда\n"
                f"Уровень: {self.level}/{self.max_level}")