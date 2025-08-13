# Characters/Status_effects/poison_effect.py
import random
from typing import Dict, Any, List

from curses import COLOR_BLUE, COLOR_RED, COLOR_WHITE

from Battle.battle_logger import battle_logger
from Characters.Status_effects.effect_result import EffectResult
from Characters.Status_effects.status_effect import StatusEffect
from Characters.Status_effects.status_manager import register_effect
from Characters.character import Character


class PoisonEffect(StatusEffect):
    """Эффект отравления - наносит урон каждый ход"""
    
    def __init__(self, duration: int = 3, damage_per_turn: int = 5, chance: float = 0.3):
        """
        Инициализация эффекта отравления.
        
        :param duration: Длительность эффекта в раундах
        :param damage_per_turn: Урон от отравления за ход
        :param chance: Шанс наложения эффекта (используется при отображении информации)
        """
        super().__init__(
            name="Отравление",
            duration=duration,
            description=f"Наносит {damage_per_turn} урона каждый ход в течение {duration} раундов",
            icon="☠️"
        )
        self.damage_per_turn = damage_per_turn
        self.chance = chance
    
    def apply_effect(self, target: Character) -> Dict[str, Any]:
        """Применяется при первом наложении эффекта"""
        return {
            'messages': [f"{target.name} получает эффект отравления!"],
            'effect': 'poison_applied'
        }
    
    def update_effect(self, target: Character) -> EffectResult:
        """Вызывается каждый ход - наносит урон от отравления"""
        # Наносим урон от отравления
        result: EffectResult = EffectResult()
        result.effect = 'poison_tick'
        result.total_damage = self.damage_per_turn

        target.take_damage(self.damage_per_turn)
        
        # Формируем сообщение
        damage_template = f"%1 %2 получает %3 урона от отравления"
        damage_elements: List[tuple] = [(self.icon, COLOR_WHITE), (target.name, COLOR_BLUE), 
                                       (str(self.damage_per_turn), COLOR_RED)]
        
        log_message = battle_logger.create_log_message(damage_template, damage_elements)
        result.messages.append(log_message)
        
        return result
    
    def remove_effect(self, target: Character) -> Dict[str, Any]:
        """Вызывается при окончании действия эффекта"""
        return {
            'message': f"Эффект отравления на {target.name} исчез",
            'effect': 'poison_removed'
        }

# Регистрируем эффект в реестре
register_effect(PoisonEffect)