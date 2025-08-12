# Characters/Abilities/rest_ability.py

from Battle.battle_logger import battle_logger
from Characters.Abilities.abilities import ActiveAbility, AbilityResult

class Rest(ActiveAbility):
    """Способность: Отдых - восстанавливает энергию"""
    
    def __init__(self):
        super().__init__(
            name="Отдых",
            type=2,
            damage_scale=0.0,
            cooldown=0,  # Нет кулдауна
            energy_cost=0,  # Не требует энергии для использования
            description="Восстанавливает 30 энергии",
            icon="🧘"
        )
        self.energy_restore = 30
        self.set_level(1)
    
    def execute(self, character, targets, **kwargs):
        """Выполняет отдых и восстанавливает энергию."""
        result = AbilityResult()
        result.ability_type = "rest"
        result.character = character.name
        
        # Сохраняем текущую энергию для отчета
        old_energy = character.energy if hasattr(character, 'energy') else 0
        
        # Восстанавливаем энергию
        if hasattr(character, 'energy') and hasattr(character, 'derived_stats'):
            character.energy = min(character.derived_stats.max_energy, character.energy + self.energy_restore)
            actual_restore = character.energy - old_energy
        else:
            actual_restore = 0
            
        result.energy_restored = actual_restore
        result.details['old_energy'] = old_energy
        result.details['new_energy'] = character.energy if hasattr(character, 'energy') else 0
            
        # Создаем сообщение
        template = "%1 %2 отдыхает и восстанавливает %3 энергии!"
        elements = [(self.icon, 0), (character.name, 2), (str(actual_restore), 6)]
        
        result.messages = [battle_logger.create_log_message(template, elements)]
            
        return result
    
    def check_specific_conditions(self, character, targets):
        """Проверяет, может ли персонаж отдыхать (не на максимуме энергии)."""
        if not hasattr(character, 'energy') or not hasattr(character, 'derived_stats'):
            return False
        return character.energy < character.derived_stats.max_energy