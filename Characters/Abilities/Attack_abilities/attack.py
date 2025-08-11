# Characters/Abilities/basic_attack.py

from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.abilities import Ability, AbilityResult

class Attack(Ability):
    """Базовая атака персонажа"""
    
    def __init__(self):
        super().__init__(
            name="Атака", 
            damage_scale=1.0, 
            cooldown=0, 
            energy_cost=10, 
            description="Базовая атака противника",
            icon="⚔️"
        )
    
    def execute(self, character, targets, **kwargs):
        """Выполняет базовую атаку по одной цели."""
        result = AbilityResult()
        result.ability_type = "basic_attack"
        result.character = character.name
        
        if not targets:
            result.success = False
            result.reason = 'Нет целей для атаки'
            return result
        
        # Выбираем первую живую цель
        target = None
        for t in targets:
            if t.is_alive():
                target = t
                break
        
        if not target:
            result.success = False
            result.reason = 'Нет живых целей для атаки'
            return result
        
        result.targets = [target.name]
        
        # Применяем все игровые механики сразу
        base_damage = int(character.derived_stats.attack * self.damage_scale)
        mechanics_results = GameMechanics.apply_all_mechanics(self, character, target, base_damage)
        
        # Формируем сообщение и финальные данные
        if mechanics_results['dodge_success']:
            # Цель уклонилась - используем сообщение из механик
            result.messages = [mechanics_results['dodge_message']]
            result.details['dodge'] = True
            result.details['target_alive'] = target.is_alive()
        else:
            # Атака прошла, наносим урон
            actual_damage = mechanics_results['final_damage']
            # Наносим урон цели
            target.take_damage(actual_damage)
            
            result.damage_dealt = actual_damage
            result.total_damage = actual_damage
            result.details['damage_blocked'] = mechanics_results['blocked_damage']
            result.is_critical = mechanics_results['critical_hit']
            result.details['target_alive'] = target.is_alive()
            
            # Создаем сообщение об успешной атаке
            result.messages = [self._create_attack_message(
                character, target, damage=actual_damage, 
                blocked=mechanics_results['blocked_damage'], 
                is_critical=mechanics_results['critical_hit']
            )]
        
        return result
    
    def _create_attack_message(self, character, target, damage=0, blocked=0, is_critical=False):
        """Создает сообщение для атаки в зависимости от результата."""
        if is_critical:
            template = "%1 %2 атакует %3 и наносит %4 КРИТИЧЕСКОГО урона! (%5 заблокировано) %6"
            crit_text = "💥" if damage > 0 else ""
            if character.is_player:
                elements = [(self.icon, 0), (character.name, 2), (target.name, 4), (str(damage), 1), (str(blocked), 3), (crit_text, 0)]
            else:
                elements = [(self.icon, 0), (character.name, 4), (target.name, 2), (str(damage), 1), (str(blocked), 3), (crit_text, 0)]
        else:
            template = "%1 %2 атакует %3 и наносит %4 урона. (%5 заблокировано)"
            if character.is_player:
                elements = [(self.icon, 0), (character.name, 2), (target.name, 4), (str(damage), 1), (str(blocked), 3)]
            else:
                elements = [(self.icon, 0), (character.name, 4), (target.name, 2), (str(damage), 1), (str(blocked), 3)]
            
        return battle_logger.create_log_message(template, elements)
    
    def check_specific_conditions(self, character, targets):
        return True