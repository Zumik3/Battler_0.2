# characters/abilities/attack/fire_storm.py

from typing import List, Dict, Any
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics
from Characters.Abilities.ability import ActiveAbility, AbilityResult
from Characters.character import Character
from Config.curses_config import COLOR_GREEN, COLOR_BLUE, COLOR_RED, COLOR_YELLOW
from Config.game_config import DAMAGE_LIST_ICON
from Utils.types import IApplyEffectResult


class FireStorm(ActiveAbility):
    """Способность: Огненный шторм - мощная массовая атака огнём по всем врагам"""
    
    def __init__(self) -> None:
        super().__init__(
            name="Огненный шторм",
            damage_scale=0.6,  # немного меньше урона из-за массовости
            cooldown=3,        # больший кулдаун из-за мощности
            energy_cost=12,    # высокая стоимость энергии
            description="Мощный огненный шторм, наносящий урон всем врагам",
            icon="🌪️",
            is_mass=True       # массовая способность
        )
        # Добавляем эффект ожога к списку возможных эффектов способности
        self.add_effect_by_class_name("BurnEffect")
    
    def execute(self, character: Character, targets: List[Character], **kwargs: Any) -> AbilityResult:
        """
        Выполняет огненную атаку по всем целям.
        
        :param character: Персонаж, использующий способность
        :param targets: Список всех целей
        :param kwargs: Дополнительные параметры
        :return: Результат выполнения способности
        """
        result: AbilityResult = AbilityResult()
        result.ability_type = "fire_storm"
        result.character = character
        result.targets = targets
        
        # Проверяем наличие живых целей
        alive_targets = [target for target in targets if target.is_alive()]
        if not alive_targets:
            result.success = False
            result.reason = 'Нет целей для атаки'
            return result
        
        # Рассчитываем базовый урон
        base_damage: int = int(character.stats.intelligence * self.damage_scale)
        
        # Создаем начальное сообщение
        template: str = "%1 %2 призывает огненный шторм!"
        elements: List[tuple] = [(self.icon, 0), (character.name, COLOR_GREEN), ("", 0)]
        result.messages = [battle_logger.create_log_message(template, elements)]
        
        # Общая статистика
        result.total_damage = 0
        total_effects_applied = 0
        
        # Атакуем каждую цель
        for target in alive_targets:
            # Применяем игровые механики для каждой цели
            mechanics_results: Dict[str, Any] = GameMechanics.apply_all_mechanics(self, character, target, base_damage)
            
            if mechanics_results['dodge_success']:
                # Цель уклонилась
                dodge_template: str = "  🔸 %1 уворачивается от огненного шторма!"
                dodge_elements: List[tuple] = [(target.name, COLOR_BLUE)]
                result.messages.append(battle_logger.create_log_message(dodge_template, dodge_elements))
            else:
                # Атака прошла, наносим урон
                actual_damage: int = mechanics_results['final_damage']
                target.take_damage(actual_damage)

                # Применяем эффекты с определенным шансом
                apply_effect_result_list: List[IApplyEffectResult] = []
                if target.is_alive():
                    apply_effect_result_list = self.apply_effects_with_chance(target, chance=0.7)  # 70% шанс наложить эффект

                result.total_damage += actual_damage
                total_effects_applied += len(apply_effect_result_list)
                
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
        
        result.success = True
        result.details['targets_hit'] = len(alive_targets)
        result.details['effects_applied'] = total_effects_applied
        
        return result
    
    def check_specific_conditions(self, character: Character, targets: List[Character]) -> bool:
        """
        Проверяет специфические условия для использования умения.
        
        :param character: Персонаж, использующий способность
        :param targets: Список целей
        :return: True если условия выполнены, False если нет
        """
        # Огненный шторм может использоваться против нескольких целей
        return True