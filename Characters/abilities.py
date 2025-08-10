# abilities.py - Система способностей персонажей

import random
from Battle.battle_logger import battle_logger
from Battle.base_mechanics import GameMechanics

class Ability:
    """Базовый класс для способностей"""
    
    def __init__(self, name,  type=0, damage_scale=0.0, cooldown=1, energy_cost=0, description="", icon=""):
        """
        Инициализация способности.
        
        :param name: Название способности
        :param damage_scale: Процент урона от атаки владельца
        :param cooldown: Количество раундов до восстановления способности
        :param energy_cost: Стоимость энергии для использования
        :param description: Описание способности
        """
        self.name = name
        self.type = type # Тип способности - 0 - атака, 1 - лечение, 2 - отдых и т.д.
        self.damage_scale = damage_scale
        self.cooldown = cooldown # чтобы была задержка 1 ход - указываем 2
        self.current_cooldown = 0
        self.energy_cost = energy_cost
        self.description = description
        self.icon = icon
        
    
    def can_use(self, character, targets=None):
        """
        Проверяет, может ли персонаж использовать способность.
        
        :param character: Персонаж, который хочет использовать способность
        :param targets: Цели (опционально)
        :return: True, если можно использовать, иначе False
        """
        # Проверяем кулдаун
        if self.current_cooldown > 0:
            return False
            
        # Проверяем энергию
        if hasattr(character, 'energy') and character.energy < self.energy_cost:
            return False
            
        # Проверяем специфические условия для способности
        return self.check_specific_conditions(character, targets)
    
    def check_specific_conditions(self, character, targets):
        """
        Проверяет специфические условия для использования способности.
        Переопределяется в подклассах.
        """
        return True
    
    def use(self, character, targets, **kwargs):
        """
        Использует способность.
        
        :param character: Персонаж, использующий способность
        :param targets: Список целей
        :param kwargs: Дополнительные параметры
        :return: Результат использования способности
        """
        if not self.can_use(character, targets):
            return self.get_cannot_use_result(character)
        
        # Тратим энергию
        if hasattr(character, 'energy'):
            character.energy -= self.energy_cost
            
        # Запускаем кулдаун
        self.current_cooldown = self.cooldown
        
        # Выполняем способность
        result = self.execute(character, targets, **kwargs)
        
        # Обновляем статистику использования
        self.on_use(character, targets, result)
        
        return result
    
    def execute(self, character, targets, **kwargs):
        """
        Выполняет логику способности. Переопределяется в подклассах.
        """
        raise NotImplementedError("Метод execute должен быть реализован в подклассе")
    
    def update_cooldown(self):
        """Обновляет кулдаун способности в конце раунда."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    
    def on_use(self, character, targets, result):
        """
        Вызывается после использования способности.
        Можно использовать для обновления статистики и т.д.
        """
        pass
    
    def get_cannot_use_result(self, character):
        """
        Возвращает результат, когда способность нельзя использовать.
        """
        return {
            'success': False,
            'reason': 'Невозможно использовать способность',
            'character': character.name
        }
    
    def get_info(self):
        """Возвращает информацию о способности."""
        return {
            'name': self.name,
            'damage_scale': self.damage_scale,
            'cooldown': self.cooldown,
            'current_cooldown': self.current_cooldown,
            'energy_cost': self.energy_cost,
            'description': self.description
        }

class BasicAttack(Ability):
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
        if not targets:
            return {
                'success': False, 
                'message': 'Нет целей для атаки',
                'type': 'basic_attack'
            }
        
        # Выбираем первую живую цель
        target = None
        for t in targets:
            if t.is_alive():
                target = t
                break
        
        if not target:
            return {
                'success': False, 
                'message': 'Нет живых целей для атаки',
                'type': 'basic_attack'
            }
        
        # Применяем все игровые механики сразу
        base_damage = int(character.attack * self.damage_scale)
        mechanics_results = GameMechanics.apply_all_mechanics(character, target, base_damage)
        
        # Подготавливаем базовый результат
        result = {
            'type': 'basic_attack',
            'attacker': character.name,
            'target': target.name,
            'damage_dealt': 0,
            'damage_blocked': 0,
            'is_critical': False,
            'dodge': mechanics_results['dodge_success'],
            'target_alive': target.is_alive(),
            'mechanics_details': mechanics_results
        }
        
        # Формируем сообщение и финальные данные
        if mechanics_results['dodge_success']:
            # Цель уклонилась - используем сообщение из механик
            result['message'] = mechanics_results['dodge_message']
        else:
            # Атака прошла, наносим урон
            actual_damage = mechanics_results['final_damage']
            is_critical = mechanics_results['critical_hit']
            
            # Наносим урон цели
            damage_dealt, blocked = target.take_damage(actual_damage)
            
            result['damage_dealt'] = damage_dealt
            result['damage_blocked'] = blocked
            result['is_critical'] = is_critical
            result['target_alive'] = target.is_alive()
            
            # Создаем сообщение об успешной атаке
            result['message'] = self._create_attack_message(
                character, target, damage=actual_damage, is_critical=is_critical
            )
        
        return result
    
    def _create_attack_message(self, character, target, damage=0, is_critical=False):
        """Создает сообщение для атаки в зависимости от результата."""
        if is_critical:
            template = "%1 %2 атакует %3 и наносит %4 КРИТИЧЕСКОГО урона! %5"
            crit_text = "💥" if damage > 0 else ""
            if character.is_player:
                elements = [(self.icon, 0), (character.name, 2), (target.name, 4), (str(damage), 1), (crit_text, 0)]
            else:
                elements = [(self.icon, 0), (character.name, 4), (target.name, 2), (str(damage), 1), (crit_text, 0)]
        else:
            template = "%1 %2 атакует %3 и наносит %4 урона."
            if character.is_player:
                elements = [(self.icon, 0), (character.name, 2), (target.name, 4), (str(damage), 1)]
            else:
                elements = [(self.icon, 0), (character.name, 4), (target.name, 2), (str(damage), 1)]
        
        return battle_logger.create_log_message(template, elements)
    
    def check_specific_conditions(self, character, targets):
        return True

class RestAbility(Ability):
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
    
    def execute(self, character, targets, **kwargs):
        """Выполняет отдых и восстанавливает энергию."""
        # Сохраняем текущую энергию для отчета
        old_energy = character.energy if hasattr(character, 'energy') else 0
        
        # Восстанавливаем энергию
        if hasattr(character, 'energy') and hasattr(character, 'max_energy'):
            character.energy = min(character.max_energy, character.energy + self.energy_restore)
            actual_restore = character.energy - old_energy
        else:
            actual_restore = 0
            
        # Создаем сообщение
        template = "%1 %2 отдыхает и восстанавливает %3 энергии!"
        elements = [(self.icon, 0), (character.name, 2), (str(actual_restore), 6)]  # голубой цвет для энергии
        
        message = battle_logger.create_log_message(template, elements)
            
        return {
            'type': 'rest',
            'character': character.name,
            'energy_restored': actual_restore,
            'message': message
        }
    
    def check_specific_conditions(self, character, targets):
        """Проверяет, может ли персонаж отдыхать (не на максимуме энергии)."""
        if not hasattr(character, 'energy') or not hasattr(character, 'max_energy'):
            return False
        return character.energy < character.max_energy

class SplashAttack(Ability):
    """Способность: Атака по области (сплэш)"""
    
    def __init__(self):
        super().__init__(
            name="Сплэш Атака",
            damage_scale=0.7,
            cooldown=3,
            energy_cost=20,
            description="Атака, поражающая всех врагов",
            icon="💥"
        )
    
    def execute(self, character, targets, **kwargs):
        """Выполняет сплэш атаку по всем целям."""
        # Фильтруем живые цели
        alive_targets = [target for target in targets if target.is_alive()]
        
        if not alive_targets:
            return {
                'success': False,
                'message': 'Нет целей для атаки',
                'type': 'splash_attack'
            }
        
        results = {
            'type': 'splash_attack',
            'attacker': character.name,
            'targets': {},
            'total_damage': 0
        }
        
        # Рассчитываем базовый урон
        base_damage = int(character.attack * self.damage_scale)
        
        # Атакуем каждую цель с применением игровых механик
        for target in alive_targets:
            mechanics_results = GameMechanics.apply_all_mechanics(character, target, base_damage)
            
            target_result = {
                'damage_dealt': 0,
                'damage_blocked': 0,
                'is_critical': False,
                'dodge': mechanics_results['dodge_success'],
                'target_alive': target.is_alive()
            }
            
            if mechanics_results['dodge_success']:
                # Цель уклонилась
                target_result['message'] = mechanics_results['dodge_message']
            else:
                # Атака прошла, наносим урон
                actual_damage = mechanics_results['final_damage']
                is_critical = mechanics_results['critical_hit']
                
                # Наносим урон цели
                damage_dealt, blocked = target.take_damage(actual_damage)
                
                target_result['damage_dealt'] = damage_dealt
                target_result['damage_blocked'] = blocked
                target_result['is_critical'] = is_critical
                target_result['target_alive'] = target.is_alive()
                
                results['total_damage'] += damage_dealt
            
            results['targets'][target.name] = target_result
        
        # Создаем общее сообщение
        template = "%1 %2 использует Сплэш Атаку по %3 целям!"
        elements = [(self.icon, 0), (character.name, 2), (str(len(alive_targets)), 1)]
        
        results['message'] = battle_logger.create_log_message(template, elements)
        
        return results
    
    def check_specific_conditions(self, character, targets):
        return True

class HealAbility(Ability):
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
        if not targets:
            return {
                'success': False, 
                'message': 'Нет целей для лечения',
                'type': 'heal'
            }
        
        # Выбираем первую живую цель
        target = None
        for t in targets:
            if t.is_alive():
                target = t
                break
        
        if not target:
            return {
                'success': False, 
                'message': 'Нет живых целей для лечения',
                'type': 'heal'
            }
        
        # Рассчитываем базовое лечение
        base_heal = random.randint(self.base_heal_amount - 5, self.base_heal_amount + 5)
        
        # Проверка критического лечения
        is_critical = GameMechanics.check_critical(character)
        heal_multiplier = 2.0 if is_critical else 1.0
        final_heal_amount = int(base_heal * heal_multiplier)
        
        # Применяем лечение
        old_hp = target.hp
        target.hp = min(target.max_hp, target.hp + final_heal_amount)
        actual_heal = target.hp - old_hp
        
        # Создаем сообщение
        if is_critical:
            template = "%1 %2 лечит %3 на %4 КРИТИЧЕСКОГО здоровья! %5"
            crit_text = "✨" if actual_heal > 0 else ""
            elements = [(self.icon, 0), (character.name, 2), (target.name, 2), (str(actual_heal), 3), (crit_text, 0)]
        else:
            template = "%1 %2 лечит %3 на %4 здоровья."
            elements = [(self.icon, 0), (character.name, 2), (target.name, 2), (str(actual_heal), 3)]
        
        message = battle_logger.create_log_message(template, elements)
        
        return {
            'type': 'heal',
            'healer': character.name,
            'target': target.name,
            'heal_amount': actual_heal,
            'is_critical': is_critical,
            'message': message
        }
    
    def check_specific_conditions(self, character, targets):
        """Проверяет, есть ли живые союзники для лечения."""
        return True

class MassHealAbility(Ability):
    """Способность: Массовое лечение"""
    
    def __init__(self):
        super().__init__(
            name="Массовое лечение",
            type=1,
            damage_scale=0.0,
            cooldown=4,
            energy_cost=30,
            description="Лечит всех союзников",
            icon="💖"
        )
        self.base_heal_amount = 20
    
    def execute(self, character, targets, **kwargs):
        """Выполняет массовое лечение всех союзников."""
        alive_allies = [ally for ally in targets if ally.is_alive()]
        
        if not alive_allies:
            return {
                'success': False, 
                'message': 'Нет живых союзников для лечения',
                'type': 'mass_heal'
            }
        
        results = {
            'type': 'mass_heal',
            'healer': character.name,
            'targets': [],
            'total_healed': 0
        }
        
        # Рассчитываем лечение на цель
        heal_per_target = max(1, self.base_heal_amount // len(alive_allies))
        base_heal_amount = max(1, random.randint(heal_per_target - 3, heal_per_target + 3))
        
        # Проверка критического лечения (сниженный шанс для массового)
        heal_crit_chance = GameMechanics.calculate_crit_chance(character) * 0.7
        is_critical = random.random() < heal_crit_chance
        heal_multiplier = 1.8 if is_critical else 1.0
        final_heal_amount = int(base_heal_amount * heal_multiplier)
        
        # Лечим каждого союзника
        for target_ally in alive_allies:
            old_hp = target_ally.hp
            target_ally.hp = min(target_ally.max_hp, target_ally.hp + final_heal_amount)
            actual_heal = target_ally.hp - old_hp
            
            results['targets'].append({
                'target': target_ally.name,
                'heal_amount': actual_heal
            })
            results['total_healed'] += actual_heal
        
        # Создаем сообщение
        if is_critical:
            template = "%1 %2 использует массовое лечение и восстанавливает %3 здоровья! %4"
            crit_text = "🌟" if results['total_healed'] > 0 else ""
            elements = [(self.icon, 0), (character.name, 2), (str(results['total_healed']), 3), (crit_text, 0)]
        else:
            template = "%1 %2 использует массовое лечение и восстанавливает %3 здоровья."
            elements = [(self.icon, 0), (character.name, 2), (str(results['total_healed']), 3)]
        
        results['message'] = battle_logger.create_log_message(template, elements)
        results['is_critical'] = is_critical
        
        return results
    
    def check_specific_conditions(self, character, targets):
        """Проверяет, есть ли живые союзники для лечения."""
        if not targets:
            return False
        return any(target.is_alive() for target in targets)

# === Система управления способностями персонажа ===

class AbilityManager:
    """Менеджер способностей персонажа"""
    
    def __init__(self):
        # Один словарь, хранящий отдельные экземпляры способностей для каждого персонажа
        self.abilities = {}  # {name: Ability instance}
        # Добавляем базовые способности по умолчанию
        self.add_ability('basic_attack', BasicAttack())
        self.add_ability('rest', RestAbility())
    
    def add_ability(self, name, ability_instance):
        """Добавляет способность персонажу."""
        self.abilities[name] = ability_instance
    
    def remove_ability(self, name):
        """Удаляет способность по имени."""
        if name in self.abilities:
            del self.abilities[name]
            return True
        return False
    
    def clear_abilities(self):
        """Удаляет все способности."""
        self.abilities.clear()
    
    def get_ability(self, name):
        """Получает способность по имени."""
        return self.abilities.get(name)
    
    def get_all_abilities(self):
        """Возвращает все способности персонажа."""
        return list(self.abilities.values())
    
    def get_all_ability_names(self):
        """Возвращает имена всех способностей персонажа."""
        return list(self.abilities.keys())
    
    def get_available_abilities(self, character):
        """
        Возвращает список ссылок на способности, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список доступных способностей (Ability instances)
        """
        return [ability for ability in self.abilities.values() if ability.can_use(character)]
    
    def get_available_ability_names(self, character):
        """
        Возвращает список имен способностей, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список имен доступных способностей
        """
        return [name for name, ability in self.abilities.items() if ability.can_use(character)]
    
    def use_ability(self, ability, character, targets, **kwargs):
        """Использует способность напрямую."""
        if ability and ability.can_use(character, targets):
            return ability.use(character, targets, **kwargs)
        return None
    
    def update_cooldowns(self):
        """Обновляет кулдауны всех способностей в конце раунда."""
        for ability in self.abilities.values():
            ability.update_cooldown()

    def reset_all_cooldowns(self):
        """Сбрасывает все кулдауны способностей до 0."""
        for ability in self.abilities.values():
            ability.current_cooldown = 0

# === Предопределенные способности ===

ABILITY_TEMPLATES = {
    'basic_attack': BasicAttack,
    'rest': RestAbility,
    'splash_attack': SplashAttack,
    'heal': HealAbility,
    'mass_heal': MassHealAbility
}

def create_ability(ability_name):
    """Создает экземпляр способности по имени."""
    ability_class = ABILITY_TEMPLATES.get(ability_name)
    if ability_class:
        return ability_class()
    return None