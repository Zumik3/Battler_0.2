# Characters/Abilities/splash_attack.py

from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import ActiveAbility, AbilityResult

class SplashAttack(ActiveAbility):
    """Способность: Атака по области (сплэш)"""
    
    def __init__(self):
        super().__init__(
            name="Сплэш Атака",
            is_mass=True,
            damage_scale=0.7,
            cooldown=3,
            energy_cost=20,
            description="Атака, поражающая всех врагов",
            icon="💥"
        )
    
    def execute(self, character, targets, **kwargs):
        """Выполняет сплэш атаку по всем целям."""
        result = AbilityResult()
        result.ability_type = "splash_attack"
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
            else:
                # Атака прошла, наносим урон
                actual_damage = mechanics_results['final_damage']
                is_critical = mechanics_results['critical_hit']
                
                # Наносим урон цели
                damage_dealt, blocked = target.take_damage(actual_damage)
                
                target_info['damage_dealt'] = damage_dealt
                target_info['damage_blocked'] = blocked
                target_info['is_critical'] = is_critical
                target_info['target_alive'] = target.is_alive()
                
                total_damage += damage_dealt
            
            target_details[target.name] = target_info
        
        result.total_damage = total_damage
        result.details['targets_info'] = target_details
        
        # Создаем общее сообщение
        template = "%1 %2 использует Сплэш Атаку по %3 целям!"
        elements = [(self.icon, 0), (character.name, 2), (str(len(alive_targets)), 1)]
        
        result.messages = [battle_logger.create_log_message(template, elements)]
        
        return result
    
    def check_specific_conditions(self, character, targets):
        return True