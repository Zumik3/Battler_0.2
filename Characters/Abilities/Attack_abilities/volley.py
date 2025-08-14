# Characters/Abilities/volley_ability.py

from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import Ability, AbilityResult

class Volley(Ability):
    """Способность: Град стрел - массовая атака по всем врагам"""
    
    def __init__(self):
        super().__init__(
            name="Град стрел",
            type=0,
            is_mass=True,
            damage_scale=0.6,
            cooldown=3,
            energy_cost=25,
            description="Массовая атака, поражающая всех врагов стрелами",
            icon="🏹"
        )
    
    def execute(self, character, targets, **kwargs):
        """Выполняет массовую атаку по всем врагам."""
        result = AbilityResult()
        result.ability_type = "volley"
        result.character = character.name
        
        # Фильтруем живые цели
        alive_targets = [target for target in targets if target.is_alive()]
        
        if not alive_targets:
            result.success = False
            result.reason = 'Нет целей для атаки'
            return result
        
        result.targets = [target.name for target in alive_targets]
        
        # Рассчитываем базовый урон
        base_damage = int(character.derived_stats.attack * self.damage_scale)
        
        # Атакуем каждую цель с применением игровых механик
        total_damage = 0
        target_details = {}
        
        # Создаем начальное сообщение
        template = "%1 %2 запускает способность Град стрел!"
        elements = [(self.icon, 0), (character.name, 2)]
        result.messages = [battle_logger.create_log_message(template, elements)]
        
        for target in alive_targets:
            mechanics_results = GameMechanics.apply_all_mechanics(self, character, target, base_damage)
            
            target_info = {
                'damage_dealt': 0,
                'damage_blocked': 0,
                'is_critical': False,
                'dodge': mechanics_results['dodge_success'],
                'target_alive': target.is_alive()
            }
            
            if mechanics_results['dodge_success']:
                # Цель уклонилась
                target_info['message'] = mechanics_results['dodge_message']
                # Добавляем сообщение об уклонении
                dodge_template = "  🔸 %1 уклоняется от стрел!"
                dodge_elements = [(target.name, 4)]
                result.messages.append(battle_logger.create_log_message(dodge_template, dodge_elements))
            else:
                # Атака прошла, наносим урон
                actual_damage = mechanics_results['final_damage']
                # Наносим урон цели
                target.take_damage(actual_damage)
                
                target_info['damage_dealt'] = actual_damage
                target_info['damage_blocked'] = mechanics_results['blocked_damage']
                target_info['is_critical'] = mechanics_results['critical_hit']
                target_info['target_alive'] = target.is_alive()
                
                total_damage += actual_damage
                
                # Добавляем детальное сообщение о уроне по цели
                if mechanics_results['critical_hit']:
                    damage_template = "  🔸 %1 получает %2 КРИТИЧЕСКОГО урона (%3 заблокировано) %4"
                    crit_text = "💥" if actual_damage > 0 else ""
                    damage_elements = [(target.name, 4), (str(actual_damage), 1), (str(mechanics_results['blocked_damage']), 3), (crit_text, 0)]
                else:
                    damage_template = "  🔸 %1 получает %2 урона (%3 заблокировано)"
                    damage_elements = [(target.name, 4), (str(actual_damage), 1), (str(mechanics_results['blocked_damage']), 3)]
                
                result.messages.append(battle_logger.create_log_message(damage_template, damage_elements))
            
            target_details[target.name] = target_info
        
        result.total_damage = total_damage
        result.details['targets_info'] = target_details
        
        return result
    
    def check_specific_conditions(self, character, targets):
        return True