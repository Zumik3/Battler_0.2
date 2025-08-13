# Characters/Abilities/mass_heal_ability.py

import random
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import ActiveAbility, AbilityResult

class MassHeal(ActiveAbility):
    """Способность: Массовое лечение"""
    
    def __init__(self):
        super().__init__(
            name="Массовое лечение",
            type=1,
            is_mass=True,
            damage_scale=0.0,
            cooldown=4,
            energy_cost=30,
            description="Лечит всех союзников",
            icon="💖"
        )
        self.base_heal_amount = 20
    
    def execute(self, character, targets, **kwargs):
        """Выполняет массовое лечение всех союзников."""
        result = AbilityResult()
        result.ability_type = "mass_heal"
        result.character = character.name
        
        alive_allies = [ally for ally in targets if ally.is_alive()]
        
        if not alive_allies:
            result.success = False
            result.reason = 'Нет живых союзников для лечения'
            return result
        
        result.targets = [ally.name for ally in alive_allies]
        
        # Рассчитываем лечение на цель с защитой от деления на ноль
        heal_per_target = max(1, self.base_heal_amount // max(1, len(alive_allies)))
        base_heal_amount = max(1, random.randint(heal_per_target - 3, heal_per_target + 3))
        
        # Проверка критического лечения (сниженный шанс для массового)
        heal_crit_chance = GameMechanics.calculate_crit_chance(character) * 0.7
        is_critical = random.random() < heal_crit_chance
        heal_multiplier = 1.8 if is_critical else 1.0
        final_heal_amount = int(base_heal_amount * heal_multiplier)
        
        # Лечим каждого союзника и собираем информацию
        total_healed = 0
        healed_targets = []
        
        for target_ally in alive_allies:
            old_hp = target_ally.hp
            target_ally.hp = min(target_ally.derived_stats.max_hp, target_ally.hp + final_heal_amount)
            actual_heal = target_ally.hp - old_hp
            
            healed_targets.append({
                'target': target_ally.name,
                'heal_amount': actual_heal
            })
            total_healed += actual_heal
        
        result.total_heal = total_healed
        result.heal_amount = total_healed
        result.is_critical = is_critical
        result.details['healed_targets'] = healed_targets
        
        # Создаем детализированное сообщение
        if is_critical:
            message_template = "%1 %2 использует массовое лечение и восстанавливает %3 здоровья! %4"
            crit_text = "🌟" if total_healed > 0 else ""
            message_elements = [(self.icon, 0), (character.name, 2), (str(total_healed), 3), (crit_text, 0)]
        else:
            message_template = "%1 %2 использует массовое лечение и восстанавливает %3 здоровья."
            message_elements = [(self.icon, 0), (character.name, 2), (str(total_healed), 3)]
        
        result.messages = []
        result.messages.append(battle_logger.create_log_message(message_template, message_elements))

        # Добавляем детали по каждому союзнику (упрощенный формат)
        for target_info in healed_targets:
            # Для каждого союзника добавляем 3 элемента: имя, " вылечен на ", количество
            detail_template = "  🔹 %1 вылечен на %2 здоровья"
            detail_elements = [(target_info['target'], 2),  # имя - зеленый
                (str(target_info['heal_amount']), 6),  # количество - бирюзовый
            ]
            result.messages.append(battle_logger.create_log_message(detail_template, detail_elements))
        
        return result
    
    def check_specific_conditions(self, character, targets):
        return True