# characters/abilities/attack/sliding_strike.py

from typing import List, Dict, Any
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import ActiveAbility, AbilityResult
from Characters.character import Character
from Config.curses_config import COLOR_GREEN, COLOR_BLUE, COLOR_RED, COLOR_YELLOW
from Config.game_config import DAMAGE_LIST_ICON
from Utils.types import IApplyEffectResult

class SlidingStrike(ActiveAbility):
    """Способность: Скользящий удар - проходит сквозь врагов, атакуя 2х"""
    
    def __init__(self) -> None:
        super().__init__(
            name="Скользящий удар",
            is_mass=True,
            damage_scale=0.55,  # Умеренный урон за каждого врага
            cooldown=4,
            energy_cost=25,
            description="Проходит сквозь врагов, атакуя 2х на пути",
            icon="🗡️"
        )
        # Добавляем эффект отравления к списку возможных эффектов способности
        self.add_effect_by_class_name("PoisonEffect")
    
    def execute(self, character: 'Character', targets: List[Character], **kwargs: Any) -> AbilityResult:
        """Выполняет скользящий удар по всем врагам."""
        result: AbilityResult = AbilityResult()
        result.ability_type = "sliding_strike"
        result.character = character
        
        # Фильтруем живые цели
        alive_targets = [target for target in targets if target.is_alive()]
        
        if not alive_targets:
            result.success = False
            result.reason = 'Нет целей для атаки'
            return result
        
        chosen_targets = character.ability_manager.get_random_elements(alive_targets, 2)
        result.targets = chosen_targets
        
        # Рассчитываем базовый урон
        base_damage: int = int(character.derived_stats.attack * self.damage_scale)
        
        # Создаем начальное сообщение
        template: str = "%1 %2 совершает скользящий удар по врагам!"
        elements: List[tuple] = [(self.icon, 0), (character.name, COLOR_GREEN)]
        result.messages = [battle_logger.create_log_message(template, elements)]
        
        # Атакуем каждую цель
        total_damage = 0
        target_details = {}
        
        for target in chosen_targets:
            # Применяем игровые механики для каждой цели
            mechanics_results: Dict[str, Any] = GameMechanics.apply_all_mechanics(self, character, target, base_damage)
            
            target_info: Dict[str, Any] = {
                'damage_dealt': 0,
                'damage_blocked': 0,
                'is_critical': False,
                'dodge': mechanics_results['dodge_success'],
                'target_alive': target.is_alive()
            }
            
            if mechanics_results['dodge_success']:
                # Цель уклонилась
                target_info['message'] = mechanics_results['dodge_message']
                dodge_template: str = "  🔸 %1 уклоняется от скользящего удара!"
                dodge_elements: List[tuple] = [(target.name, COLOR_BLUE)]
                result.messages.append(battle_logger.create_log_message(dodge_template, dodge_elements))
            else:
                # Атака прошла, наносим урон
                actual_damage: int = mechanics_results['final_damage']
                # Наносим урон цели
                target.take_damage(actual_damage)
                
                # Применяем эффекты с определенным шансом
                apply_effect_result_list: List[IApplyEffectResult] = []
                if target.is_alive():
                    apply_effect_result_list = self.apply_effects_with_chance(target, chance=0.7)  # 100% шанс наложить эффект


                target_info['damage_dealt'] = actual_damage
                target_info['damage_blocked'] = mechanics_results['blocked_damage']
                target_info['is_critical'] = mechanics_results['critical_hit']
                target_info['target_alive'] = target.is_alive()
                
                total_damage += actual_damage
                
                # Добавляем сообщение о уроне
                damage_template: str = ""
                if mechanics_results['critical_hit']:
                    damage_template = f"  {DAMAGE_LIST_ICON} %1 получает %2 КРИТИЧЕСКОГО урона от скользящего удара! (%3 заблокировано) 💥"
                else:
                    damage_template = f"  {DAMAGE_LIST_ICON} %1 получает %2 урона от скользящего удара. (%3 заблокировано)"
                
                damage_elements: List[tuple] = [(target.name, COLOR_BLUE), 
                                              (str(actual_damage), COLOR_RED), 
                                              (str(mechanics_results['blocked_damage']), COLOR_YELLOW)]
                
                result.messages.append(battle_logger.create_log_message(damage_template, damage_elements))

                for apply_effect_result in apply_effect_result_list:
                    result.messages.append(apply_effect_result.message)
            
            target_details[target.name] = target_info
        
        result.total_damage = total_damage
        result.details['targets_info'] = target_details
        result.success = True
        
        return result
    
    def check_specific_conditions(self, character: Character, targets: List[Character]) -> bool:
        """Проверяет специфические условия для использования умения"""
        # Скользящий удар может атаковать несколько целей
        return True