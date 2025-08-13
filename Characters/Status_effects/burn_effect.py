# Characters/Status_effects/burn_effect.py
import random
from typing import Dict, Any, List

from curses import COLOR_RED, COLOR_WHITE, COLOR_YELLOW

from Battle.battle_logger import battle_logger
from Characters.Status_effects.effect_result import EffectResult
from Characters.Status_effects.status_effect import StatusEffect
from Characters.character import Character


class BurnEffect(StatusEffect):
    """Эффект ожога - наносит урон каждый ход с нарастающим эффектом и дополнительными механиками"""
    
    def __init__(self, duration: int = 3, base_damage: int = 3):
        """
        Инициализация эффекта ожога.
        
        :param duration: Базовая длительность эффекта в раундах
        :param base_damage: Базовый урон от ожога за ход (умножается на количество стаков)
        """
        super().__init__(
            name="Ожог",
            duration=duration,
            description=f"Наносит нарастающий урон каждый ход и снижает защиту",
            icon="🔥"
        )
        self.base_damage = base_damage
        self.base_duration = duration  # Сохраняем базовую длительность
        self.stacks = 1  # Количество стаков эффекта
    
    def apply_effect(self, target: Character) -> Dict[str, Any]:
        """Применяется при первом наложении эффекта или добавлении стака"""
        # Проверяем, есть ли уже такой эффект
        if target.has_status_effect("Ожог"):
            # Если эффект уже есть, увеличиваем стаки и обновляем длительность
            existing_effect = target.status_manager.get_effect("Ожог")
            if existing_effect:
                existing_effect.stacks += 1
                # Обновляем длительность до базового значения
                existing_effect.duration = existing_effect.base_duration
                return {
                    'message': f"{target.name} получает дополнительный стак ожога! (Стаков: {existing_effect.stacks})",
                    'effect': 'burn_stacked'
                }
        
        # Первичное применение эффекта
        return {
            'message': f"{target.name} получает эффект ожога!",
            'effect': 'burn_applied'
        }
    
    def update_effect(self, target: Character) -> EffectResult:
        """Вызывается каждый ход - наносит урон от ожога с нарастающим эффектом"""
        result: EffectResult = EffectResult()
        result.effect = 'burn_tick'
        
        # Рассчитываем урон с учетом стаков (линейный рост)
        current_damage = self.base_damage * self.stacks
        result.total_damage = current_damage

        # Наносим урон
        target.take_damage(current_damage)
        
        # Формируем сообщение об уроне
        damage_template = f"%1 %2 получает %3 урона от ожога"
        if self.stacks > 1:
            damage_template += f" ({self.stacks} стаков)"
            
        damage_elements: List[tuple] = [(self.icon, COLOR_WHITE), (target.name, COLOR_YELLOW), 
                                      (str(current_damage), COLOR_RED)]
        
        log_message = battle_logger.create_log_message(damage_template, damage_elements)
        result.messages.append(log_message)
        
        # Добавляем шанс на дополнительный эффект - воспламенение
        if random.random() < 0.15:  # 15% шанс
            result.additional_effects.append({
                'type': 'ignite',
                'message': f"{target.name} вспыхивает от огня!",
                'extra_damage': int(current_damage * 0.5)
            })
            # Наносим дополнительный урон от воспламенения
            target.take_damage(int(current_damage * 0.5))
        
        return result
    
    def remove_effect(self, target: Character) -> Dict[str, Any]:
        """Вызывается при окончании действия эффекта"""
        return {
            'message': f"Эффект ожога на {target.name} исчез",
            'effect': 'burn_removed'
        }
    
    def get_intensity_description(self) -> str:
        """Возвращает описание интенсивности эффекта в зависимости от количества стаков"""
        if self.stacks == 1:
            return "легкий"
        elif self.stacks == 2:
            return "средний"
        elif self.stacks == 3:
            return "сильный"
        else:
            return "разрушительный"