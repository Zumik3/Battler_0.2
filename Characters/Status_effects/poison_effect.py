# Characters/Status_effects/poison_effect.py
from typing import Dict, Any, List
from Config.curses_config import COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_WHITE, COLOR_YELLOW

from Battle.battle_logger import battle_logger
from Characters.Status_effects.effect_result import ApplyEffectResult, EffectResult
from Characters.Status_effects.status_effect import StackableStatusEffect
from Characters.Status_effects.status_manager import register_effect
from Characters.character import Character
from Config.game_config import EFFECT_LIST_ICON, SPACES_SECOND_LEVEL
from Utils.types import IEffectResult


class PoisonEffect(StackableStatusEffect):
    """Эффект отравления - наносит урон каждый ход с нарастающим эффектом"""
    
    def __init__(self, duration: int = 3, base_damage: int = 5):
        """
        Инициализация эффекта отравления.
        
        :param duration: Базовая длительность эффекта в раундах
        :param base_damage: Базовый урон от отравления за ход (умножается на количество стаков)
        """
        super().__init__(
            name="Отравление",
            duration=duration,
            description=f"Наносит нарастающий урон каждый ход",
            icon="☠️"
        )
        self.base_damage = base_damage
        self.base_duration = duration  # Сохраняем базовую длительность
        self.stacks = 0  # Количество стаков эффекта
    
    def apply_effect(self, target: Character) -> IEffectResult:
        """Применяется при первом наложении эффекта или добавлении стака"""
        
        # Первичное применение эффекта
        apply_effect_result = ApplyEffectResult("poison")
        
        target_color = COLOR_GREEN if target.is_player else COLOR_BLUE

        template: str = f"{SPACES_SECOND_LEVEL}%1 %2 получает %3"        
        elements: List[tuple] = [(EFFECT_LIST_ICON, COLOR_RED), 
            (target.name, target_color), ("отравление", COLOR_GREEN)]
        message = battle_logger.create_log_message(template, elements)

        apply_effect_result.add_message(message)
        return apply_effect_result

    
    def update_effect(self, target: Character) -> EffectResult:
        """Вызывается каждый ход - наносит урон от отравления с нарастающим эффектом"""
        result: EffectResult = EffectResult()
        result.effect = 'poison_tick'
        
        # Рассчитываем урон с учетом стаков (линейный рост)
        current_damage = self.get_total_effect_value(self.base_damage)
        target.take_damage(current_damage)
        result.total_damage = current_damage
        
        # Формируем сообщение об уроне
        damage_template = f"%1 %2 получает %3 урона от отравления"
        if self.stacks > 1:
            damage_template += f" ({self.stacks} стаков)"
            
        damage_elements: List[tuple] = [(self.icon, COLOR_WHITE), (target.name, COLOR_YELLOW), 
                                      (str(current_damage), COLOR_RED)]
        
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