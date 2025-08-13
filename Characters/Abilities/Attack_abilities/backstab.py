# characters/abilities/attack/backstab.py

from typing import List, Dict, Any, Optional
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import ActiveAbility, AbilityResult
from Characters.character import Character
from Config.curses_config import COLOR_GREEN, COLOR_BLUE, COLOR_RED, COLOR_YELLOW
from Config.game_config import DAMAGE_LIST_ICON

class Backstab(ActiveAbility):
    """Способность: Удар в спину - мощная одиночная атака с бонусом к урону"""
    
    def __init__(self) -> None:
        super().__init__(
            name="Удар в спину",
            damage_scale=1.8,  # Высокий урон
            cooldown=4,
            energy_cost=30,
            description="Мощная атака в спину, наносящая увеличенный урон",
            icon="🔪"
        )
    
    def execute(self, character: Character, targets: List[Character], **kwargs: Any) -> AbilityResult:
        """Выполняет удар в спину по одной цели."""
        result: AbilityResult = AbilityResult()
        result.ability_type = "backstab"
        result.character = character.name
        
        # Берем только первую цель (одиночная атака)
        if not targets or not targets[0].is_alive():
            result.success = False
            result.reason = 'Нет цели для атаки'
            return result
        
        target: Character = targets[0]
        result.targets = [target.name]
        
        # Рассчитываем базовый урон с бонусом
        base_damage: int = int(character.derived_stats.attack * self.damage_scale)
        
        # Создаем начальное сообщение
        template: str = "%1 %2 заходит за спину %3"
        elements: List[tuple] = [(self.icon, 0), (character.name, COLOR_GREEN), (target.name, COLOR_BLUE)]
        result.messages = [battle_logger.create_log_message(template, elements)]
        
        # Применяем игровые механики
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
            dodge_template: str = "  🔸 %1 замечает атаку и уклоняется!"
            dodge_elements: List[tuple] = [(target.name, 4)]
            result.messages.append(battle_logger.create_log_message(dodge_template, dodge_elements))
            result.success = False
        else:
            # Атака прошла, наносим урон
            actual_damage: int = mechanics_results['final_damage']
            # Наносим урон цели
            target.take_damage(actual_damage)
            
            target_info['damage_dealt'] = actual_damage
            target_info['damage_blocked'] = mechanics_results['blocked_damage']
            target_info['is_critical'] = mechanics_results['critical_hit']
            target_info['target_alive'] = target.is_alive()
            
            result.total_damage = actual_damage
            result.success = True
            
            # Добавляем сообщение о уроне
            if mechanics_results['critical_hit']:
                damage_template: str = f"  {DAMAGE_LIST_ICON} %1 получает %2 КРИТИЧЕСКОГО урона в спину (%3 заблокировано) 💥"
            else:
                damage_template: str = f"  {DAMAGE_LIST_ICON} %1 получает %2 урона в спину (%3 заблокировано)"
                
            damage_elements: List[tuple] = [(target.name, COLOR_BLUE), 
                    (str(actual_damage), COLOR_RED), (str(mechanics_results['blocked_damage']), COLOR_YELLOW)]
            


            result.messages.append(battle_logger.create_log_message(damage_template, damage_elements))
        
        result.details['target_info'] = target_info
        return result
    
    def check_specific_conditions(self, character: Character, targets: List[Character]) -> bool:
        """Проверяет специфические условия для использования умения"""
        # Удар в спину можно использовать только против одной цели
        return True