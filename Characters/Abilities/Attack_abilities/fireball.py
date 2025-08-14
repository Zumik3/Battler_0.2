# characters/abilities/attack/fireball.py

from typing import List, Dict, Any
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import ActiveAbility, AbilityResult
from Characters.character import Character
from Config.curses_config import COLOR_GREEN, COLOR_BLUE, COLOR_RED, COLOR_YELLOW
from Config.game_config import DAMAGE_LIST_ICON
from Utils.types import IApplyEffectResult


class Fireball(ActiveAbility):
    """Способность: Огненный шар - мощная одиночная атака огнём"""
    
    def __init__(self) -> None:
        super().__init__(
            name="Огненный шар",
            damage_scale=0.8,  # средний урон
            cooldown=1,
            energy_cost=5,
            description="Мощный огненный шар, наносящий средний урон одной цели",
            icon="🔥"
        )
        # Добавляем эффект ожога к списку возможных эффектов способности
        self.add_effect_by_class_name("BurnEffect")
    
    def execute(self, character: Character, targets: List[Character], **kwargs: Any) -> AbilityResult:
        """
        Выполняет огненную атаку по одной цели.
        
        :param character: Персонаж, использующий способность
        :param targets: Список целей (берется только первая)
        :param kwargs: Дополнительные параметры
        :return: Результат выполнения способности
        """
        result: AbilityResult = AbilityResult()
        result.ability_type = "fireball"
        result.character = character
        result.targets = targets
        
        # Берем только первую цель (одиночная атака)
        if not targets or not targets[0].is_alive():
            result.success = False
            result.reason = 'Нет цели для атаки'
            return result
        
        target: Character = targets[0]
        
        # Рассчитываем базовый урон
        base_damage: int = int(character.stats.intelligence * self.damage_scale)
        
        # Создаем начальное сообщение
        template: str = "%1 %2 выпускает огненный шар в %3"
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
            dodge_template: str = "  🔸 %1 уворачивается от огненного шара!"
            dodge_elements: List[tuple] = [(target.name, COLOR_BLUE)]
            result.messages.append(battle_logger.create_log_message(dodge_template, dodge_elements))
            result.success = False
        else:
            # Атака прошла, наносим урон
            actual_damage: int = mechanics_results['final_damage']
            # Наносим урон цели
            target.take_damage(actual_damage)

            # Применяем эффекты с определенным шансом
            apply_effect_result_list: List[IApplyEffectResult] = []
            if target.is_alive():
                apply_effect_result_list = self.apply_effects_with_chance(target, chance=1.0)  # 100% шанс наложить эффект

            target_info['damage_dealt'] = actual_damage
            target_info['damage_blocked'] = mechanics_results['blocked_damage']
            target_info['is_critical'] = mechanics_results['critical_hit']
            target_info['target_alive'] = target.is_alive()
            
            result.total_damage = actual_damage
            result.success = True
            
            # Добавляем сообщение о уроне
            damage_template: str = ""
            if mechanics_results['critical_hit']:
                damage_template = f"  {DAMAGE_LIST_ICON} %1 получает %2 КРИТИЧЕСКОГО огненного урона (%3 заблокировано) 💥"
            else:
                damage_template = f"  {DAMAGE_LIST_ICON} %1 получает %2 огненного урона (%3 заблокировано)"
                
            damage_elements: List[tuple] = [(target.name, COLOR_BLUE), 
                                          (str(actual_damage), COLOR_RED), 
                                          (str(mechanics_results['blocked_damage']), COLOR_YELLOW)]
            
            message = battle_logger.create_log_message(damage_template, damage_elements)
            result.messages.append(message)
            
            for apply_effect_result in apply_effect_result_list:
                result.messages.append(apply_effect_result.message)
            
        result.details['target_info'] = target_info
        return result
    
    def check_specific_conditions(self, character: Character, targets: List[Character]) -> bool:
        """
        Проверяет специфические условия для использования умения.
        
        :param character: Персонаж, использующий способность
        :param targets: Список целей
        :return: True если условия выполнены, False если нет
        """
        # Огненный шар можно использовать только против одной цели - пока отставить
        return True #len(targets) <= 1 and len(targets) > 0