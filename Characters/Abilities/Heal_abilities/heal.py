# Characters/Abilities/heal_ability.py

import random
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.abilities import Ability, AbilityResult

class Heal(Ability):
    """Способность: Лечение союзника"""
    
    def __init__(self):
        super().__init__(
            name="Лечение",
            type=1,
            damage_scale=0.0,
            cooldown=2,
            energy_cost=15,
            description="Лечит одного союзника",
            icon="💗"
        )
        self.base_heal_amount = 25
    
    def execute(self, character, targets, **kwargs):
        """Выполняет лечение одного союзника."""
        result = AbilityResult()
        result.ability_type = "heal"
        result.character = character.name
        
        if not targets:
            result.success = False
            result.reason = 'Нет целей для лечения'
            return result
        
        # Выбираем первую живую цель
        target = None
        for t in targets:
            if t.is_alive():
                target = t
                break
        
        if not target:
            result.success = False
            result.reason = 'Нет живых целей для лечения'
            return result
        
        result.targets = [target.name]
        
        # Рассчитываем базовое лечение
        base_heal = random.randint(self.base_heal_amount - 5, self.base_heal_amount + 5)
        
        # Проверка критического лечения
        mechanics_results = GameMechanics.apply_all_mechanics(self, character, target, base_heal)
        final_heal_amount = mechanics_results['final_damage']
        
        # Применяем лечение
        actual_heal = target.take_heal(final_heal_amount)
        
        result.heal_amount = actual_heal
        result.total_heal = actual_heal
        result.is_critical = mechanics_results['critical_hit']
        
        # Создаем сообщение
        if mechanics_results['critical_hit']:
            template = "%1 %2 лечит %3 на %4 КРИТИЧЕСКОГО здоровья! %5"
            crit_text = "✨" if actual_heal > 0 else ""
            elements = [(self.icon, 0), (character.name, 2), (target.name, 2), (str(actual_heal), 3), (crit_text, 0)]
        else:
            template = "%1 %2 лечит %3 на %4 здоровья."
            elements = [(self.icon, 0), (character.name, 2), (target.name, 2), (str(actual_heal), 3)]
        
        result.messages = [battle_logger.create_log_message(template, elements)]
        
        return result
    
    def check_specific_conditions(self, character, targets):
        return True