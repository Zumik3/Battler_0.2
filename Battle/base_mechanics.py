import random
from typing import Tuple, Dict, List, Any, Optional, Union
from Battle.battle_logger import battle_logger

# Для аннотаций типов избегаем циклических импортов
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Characters.character import Character
    from Characters.Abilities.ability import Ability


class GameMechanics:
    """Базовые игровые механики."""

    # ==================== Расчеты вероятностей ====================
    @staticmethod
    def calculate_dodge_chance(target: 'Character') -> float:
        """
        Рассчитывает шанс уклонения от атаки на основе ловкости цели.
        :param target: Персонаж, от которого пытается уклониться атака.
        :return: Вероятность уклонения (float от 0.0 до 1.0).
        """
        # Базовый шанс уклонения 5%
        base_dodge = 0.05
        # Бонус к уклонению: +1% за каждые 2 единицы ловкости сверх 10
        dex_bonus = max(0, (target.stats.dexterity - 10) * 0.005)  # +0.5% за каждую единицу dex > 10
        
        # Максимальный шанс уклонения 30%
        return min(0.30, base_dodge + dex_bonus)

    @staticmethod
    def calculate_crit_chance(character: 'Character') -> float:
        """
        Рассчитывает шанс критического эффекта (удара или лечения) на основе ловкости персонажа.
        :param character: Персонаж, применяющий эффект.
        :return: Вероятность критического эффекта (float от 0.0 до 1.0).
        """
        # Базовый шанс крита 5%
        base_crit = 0.05
        # Бонус к криту: +1% за каждую единицу ловкости сверх 10
        crit_bonus = max(0, (character.stats.dexterity - 10) * 0.01)
        
        # TODO: пока делаем крит как решение в лоб - надо переделать
        a = 0
        crit_ability = character.ability_manager.get_passive_ability('criticalstrike')
        if crit_ability:
            ability_effect = crit_ability.apply_effect(character)
            crit_bonus += ability_effect['critical_bonus']
        # Максимальный шанс крита 50%
        return min(0.50, base_crit + crit_bonus)

    @staticmethod
    def check_critical(character: 'Character') -> bool:
        """
        Проверяет, был ли эффект критическим.
        :param character: Персонаж, применяющий эффект
        :return: True если критический эффект, False если нет
        """
        crit_chance = GameMechanics.calculate_crit_chance(character)
        return random.random() < crit_chance

    @staticmethod
    def check_dodge_with_message(attacker: 'Character', target: 'Character') -> Tuple[bool, Optional[List]]:
        """
        Проверяет, удалось ли персонажу уклониться и генерирует сообщение.
        :param attacker: Атакующий персонаж
        :param target: Цель, которая пытается уклониться
        :return: Кортеж (успешно_уклонился: bool, сообщение: list или None)
        """
        dodge_chance = GameMechanics.calculate_dodge_chance(target)
        dodge_success = random.random() < dodge_chance
        
        if dodge_success:
            # Генерируем сообщение об уклонении
            icon = "🏃"

            template = "%1 %2 атакует %3, но тот уклоняется!"
            if attacker.is_player:
                elements = [(icon, 0), (attacker.name, 2), (target.name, 4)]
            else:
                elements = [(icon, 0), (attacker.name, 4), (target.name, 2)]
            message = battle_logger.create_log_message(template, elements)
        else:
            message = None
            
        return dodge_success, message

    # ==================== Расчеты урона ====================
    @staticmethod
    def calculate_damage_variance(base_damage: float, variance_percent: float = 0.1) -> float:
        """
        Рассчитывает случайное отклонение урона.
        :param base_damage: Базовый урон
        :param variance_percent: Процент отклонения (по умолчанию 10%)
        :return: Финальный урон с учетом вариации
        """
        min_damage = base_damage * (1 - variance_percent)
        max_damage = base_damage * (1 + variance_percent)
        return random.uniform(min_damage, max_damage)

    @staticmethod
    def calculate_armor_reduction(damage: float, armor: int) -> Tuple[int, int]:
        """
        Рассчитывает снижение урона броней с плавной S-образной кривой.
        :param damage: Исходный урон
        :param armor: Показатель брони
        :return: Кортеж (урон после снижения, заблокированный урон)
        """
        if armor <= 0:
            return int(damage), 0
        
        # S-образная кривая (сигмоид) для плавного масштабирования
        # k - коэффициент крутизны кривой (меньше значение = более плавная кривая)
        k = 0.03
        armor_effectiveness = 1 / (1 + 2.718 ** (-k * (armor - 50)))  # Сигмоид с центром в 50
        # Ограничиваем эффективность (максимум 85% блокировки)
        armor_effectiveness = min(armor_effectiveness, 0.85)
        reduced_damage = damage * (1 - armor_effectiveness)
        # Урон не может быть меньше 1
        final_damage = max(1, int(reduced_damage))
        blocked_damage = int(damage - reduced_damage)
        return final_damage, blocked_damage

    # ==================== Комплексные механики ====================
    @staticmethod
    def apply_all_mechanics(ability: 'Ability', attacker: 'Character', target: 'Character', base_damage: float) -> Dict[str, Any]:
        """
        Применяет все базовые игровые механики последовательно.
        :param ability: Способность, которая применяется
        :param attacker: Атакующий персонаж
        :param target: Цель атаки
        :param base_damage: Базовый урон
        :return: Словарь с результатами всех проверок и финальным уроном
        """
        results = {
            'dodge_success': False,
            'dodge_message': None,
            'critical_hit': False,
            'base_damage': base_damage,
            'varied_damage': 0,
            'blocked_damage': 0,
            'reduced_damage': 0,
            'final_damage': 0
        }
        
        # Проверка критического удара
        results['critical_hit'] = GameMechanics.check_critical(attacker)
        crit_multiplier = 2.0 if results['critical_hit'] else 1.0
        
        # Применение вариации урона/хила
        results['varied_damage'] = GameMechanics.calculate_damage_variance(base_damage)
        damage_after_variance = results['varied_damage'] * crit_multiplier
        results['final_damage'] = int(damage_after_variance)
        
        if ability.type == 0:  # (проверяем только атаки)
            
            # Проверка уклонения с генерацией сообщения
            dodge_success, dodge_message = GameMechanics.check_dodge_with_message(attacker, target)
            results['dodge_success'] = dodge_success
            results['dodge_message'] = dodge_message
            
            if dodge_success:
                results['final_damage'] = 0
                return results
        
            # Применение брони
            defence = target.derived_stats.defense
            if defence > 0:
                results['reduced_damage'], results['blocked_damage'] = GameMechanics.calculate_armor_reduction(
                    damage_after_variance, defence)
            else:
                results['reduced_damage'] = damage_after_variance
            
            results['final_damage'] = max(0, round(results['reduced_damage']))

            # Проверяем пассивные способности атакующего на наложение статус-эффектов
            if results['final_damage'] > 0:  # Только если атака попала и нанесла урон
                # Проверяем способность "Отравляющий удар"
                poison_ability = attacker.ability_manager.get_passive_ability('poisonstrike')
                if poison_ability and poison_ability.is_available():
                    poison_result = poison_ability.apply_effect(attacker, target=target)
        
        return results

    # ==================== Информационные методы ====================
    @staticmethod
    def get_mechanics_summary() -> Dict[str, str]:
        """
        Возвращает описание всех доступных механик.
        :return: Словарь с описанием механик
        """
        return {
            'dodge': 'Расчет шанса уклонения от атаки',
            'crit': 'Расчет шанса критического удара',
            'variance': 'Случайное отклонение урона',
            'armor': 'Снижение урона броней',
            'all': 'Применение всех механик последовательно'
        }