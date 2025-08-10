# mechanics.py
import random
#from config import Config

def calculate_dodge_chance(target):
    """
    Рассчитывает шанс уклонения от атаки на основе ловкости цели.
    :param target: Персонаж, от которого пытается уклониться атака.
    :return: Вероятность уклонения (float от 0.0 до 1.0).
    """
    # Базовый шанс уклонения 5%
    base_dodge = 0.05
    # Бонус к уклонению: +1% за каждые 2 единицы ловкости сверх 10
    if hasattr(target, 'dexterity'):
        dex_bonus = max(0, (target.dexterity - 10) * 0.005) # +0.5% за каждую единицу dex > 10
    else:
        dex_bonus = 0 # Если атрибута нет, бонус 0
    
    # Максимальный шанс уклонения 30%
    return min(0.30, base_dodge + dex_bonus)

def calculate_crit_chance(character, is_heal=False):
    """
    Рассчитывает шанс критического эффекта (удара или лечения) на основе ловкости персонажа.
    :param character: Персонаж, применяющий эффект.
    :param is_heal: Флаг, указывающий, является ли эффект лечением (по умолчанию False для атаки).
    :return: Вероятность критического эффекта (float от 0.0 до 1.0).
    """
    # Только игроки могут наносить криты
    if not hasattr(character, 'dexterity') or character.role == "enemy":
        return 0.0
        
    # Базовый шанс крита 5%
    base_crit = 0.05
    # Бонус к криту: +1% за каждую единицу ловкости сверх 10
    dex_bonus = max(0, (character.dexterity - 10) * 0.01)
    
    # Максимальный шанс крита 50%
    return min(0.50, base_crit + dex_bonus)

def perform_attack(attacker, target, battle_logger):
    """
    Выполняет атаку одного персонажа по другому с учетом уклонения и критических ударов.
    
    :param attacker: Персонаж, атакующий.
    :param target: Персонаж, цель атаки.
    :param battle_logger: Экземпляр BattleLogger для логирования.
    """
    # Проверка уклонения
    dodge_chance = calculate_dodge_chance(target)
    if random.random() < dodge_chance:
        # Цель уклоняется
        #combat_stats.record_damage_dealt(attacker.name, 0) # Записываем 0 урона как попытку атаки
        
        # Определяем эмодзи и тип сообщения для battle_logger
        message = f"{attacker.name} атакует {target.name}, но {target.name} УКЛОНИЛСЯ!"
        battle_logger.log_combat_result(message)
        return # Атака не попала, выходим из функции

    # --- Атака попала ---
    # Базовый урон
    base_damage = random.randint(attacker.attack // 2, attacker.attack)
    
    # Проверка критического удара
    is_critical = False
    crit_multiplier = 1.5
    final_damage = base_damage
    
    # Используем универсальную функцию для атаки (is_heal=False по умолчанию)
    crit_chance = calculate_crit_chance(attacker)
    if random.random() < crit_chance:
        is_critical = True
        final_damage = int(base_damage * crit_multiplier)
    
    # Наносим урон и расходуем энергию
    #combat_stats.record_damage_dealt(attacker.name, final_damage)
    dealt, blocked = target.take_damage(final_damage)
    attacker.spend_energy() #расход энергии на атаку
    
    # Формируем сообщение
    blocked_text = f" ({blocked} заблокировано)" if blocked > 0 else ""
    
    if is_critical:
        # Яркое отображение критического удара
        message = f"{attacker.name} наносит КРИТИЧЕСКИЙ УДАР по {target.name}! Урон: {dealt}!{blocked_text}"
        battle_logger.log_combat_result(message) # Используем специализированный метод для крит. ударов
    else:
        message = f"{attacker.name} атакует {target.name} и наносит {dealt} урона!{blocked_text}"
        battle_logger.log_combat_result(message) # Используем специализированный метод для атак
        
    if not target.is_alive():
        #combat_stats.record_kill(attacker.name)
        #combat_stats.record_death(target.name)
        message = f"{target.name} повержен!"
        battle_logger.log_death(message) # Используем специализированный метод для смерти

# === Функции для лечения ===
def execute_heal_ability(healer, target_ally, heal_amount_base, battle_logger):
    """
    Выполняет способность лечения с возможностью критического лечения.
    
    :param healer: Персонаж, применяющий лечение.
    :param target_ally: Цель лечения (союзник).
    :param heal_amount_base: Базовое количество лечения.
    :param battle_logger: Экземпляр BattleLogger для логирования.
    """
    # Случайное значение лечения вокруг базового
    base_heal_amount = random.randint(heal_amount_base - 5, heal_amount_base + 5)
    
    # Проверка критического лечения
    is_heal_critical = False
    heal_crit_multiplier = 2
    final_heal_amount = base_heal_amount
    
    # Используем универсальную функцию для лечения (is_heal=True)
    heal_crit_chance = calculate_crit_chance(healer, is_heal=True)
    if random.random() < heal_crit_chance:
        is_heal_critical = True
        final_heal_amount = int(base_heal_amount * heal_crit_multiplier)
    
    # Записываем статистику ДО применения лечения
    #combat_stats.record_healing_done(healer.name, final_heal_amount)
    #combat_stats.record_healing_taken(target_ally.name, final_heal_amount)
    
    # Применяем лечение
    old_hp = target_ally.hp
    target_ally.hp = min(target_ally.max_hp, target_ally.hp + final_heal_amount)
    actual_heal = target_ally.hp - old_hp # Реальное количество восстановленных HP
    
    # Выводим сообщение в лог
    if is_heal_critical:
        # Яркое отображение критического лечения
        message = f"{healer.name} применяет КРИТИЧЕСКОЕ ЛЕЧЕНИЕ на {target_ally.name}! Восстановлено: {actual_heal} HP!"
        battle_logger.log_heal(message) # Используем специализированный метод для крит. лечения
    else:
        message = f"{healer.name} использует способность и лечит {target_ally.name} на {actual_heal} HP"
        battle_logger.log_heal(message) # Используем специализированный метод для лечения

def execute_mass_heal_ability(healer, allies_list, heal_amount_base, battle_logger):
    """
    Выполняет массовое лечение всех союзников с возможностью критического лечения.
    
    :param healer: Персонаж, применяющий лечение.
    :param allies_list: Список союзников для лечения.
    :param heal_amount_base: Базовое количество лечения.
    :param battle_logger: Экземпляр BattleLogger для логирования.
    """
    # Фильтруем только живых союзников СРАЗУ
    alive_allies = [ally for ally in allies_list if ally.is_alive()]
    
    if not alive_allies:
        message = f"{healer.name} пытается применить массовое лечение, но нет живых союзников!"
        battle_logger.log_heal(message)
        return
    
    # Распределяем лечение между живыми союзниками
    heal_per_target = heal_amount_base // len(alive_allies)
    heal_per_target = max(1, heal_per_target)  # Минимум 1
    
    # Случайное значение лечения вокруг базового на цель
    try:
        base_heal_amount = random.randint(int(heal_per_target) - 3, int(heal_per_target) + 3)
        base_heal_amount = max(1, base_heal_amount)  # Минимум 1
    except ValueError:
        # Если диапазон неверный, используем базовое значение
        base_heal_amount = max(1, int(heal_per_target))
    
    # Проверка критического лечения (один шанс на все цели)
    is_heal_critical = False
    heal_crit_multiplier = 1.8  # Меньше, чем у одиночного лечения
    final_heal_amount = base_heal_amount
    
    # Используем универсальную функцию для лечения (is_heal=True)
    heal_crit_chance = calculate_crit_chance(healer, is_heal=True) * 0.7  # Меньше шанс крита для массового
    if random.random() < heal_crit_chance:
        is_heal_critical = True
        final_heal_amount = int(base_heal_amount * heal_crit_multiplier)
    
    total_healed = 0
    individual_heals = []  # Сохраняем индивидуальное лечение для точного подсчета
    
    # Лечим каждого союзника и сохраняем реальное лечение
    for target_ally in alive_allies:
        # Записываем статистику ДО применения лечения
        #combat_stats.record_healing_done(healer.name, final_heal_amount)
        #combat_stats.record_healing_taken(target_ally.name, final_heal_amount)
        
        # Применяем лечение
        old_hp = target_ally.hp
        target_ally.hp = min(target_ally.max_hp, target_ally.hp + final_heal_amount)
        actual_heal = target_ally.hp - old_hp  # Реальное количество восстановленных HP
        
        individual_heals.append((target_ally.name, actual_heal))
        total_healed += actual_heal
    
    # Выводим сообщение в лог
    crit_text = "КРИТИЧЕСКОЕ " if is_heal_critical else ""
    crit_emoji = "✨" if is_heal_critical else ""
    
    message = f"{healer.name} применяет {crit_text}МАССОВОЕ ЛЕЧЕНИЕ! Восстановлено {total_healed} HP у {len(alive_allies)} союзников!"
    battle_logger.log_heal(message) # Используем специализированный метод для массового лечения
    
    # Подробная информация о лечении каждого персонажа
    for ally_name, actual_heal in individual_heals:
        if actual_heal > 0:
            message = f"   {ally_name}: +{actual_heal} HP"
            battle_logger.log_heal(message) # Используем специализированный метод для деталей лечения

def perform_rest(character, battle_logger):
    """
    Выполняет действие отдыха для персонажа.
    Восстанавливает фиксированное количество энергии.
    
    :param character: Персонаж, который отдыхает.
    :param battle_logger: Экземпляр BattleLogger для логирования.
    """
    
    # Восстанавливаем энергию
    RESTORE_ENERGY_AMOUNT = 30
    character.restore_energy(amount=RESTORE_ENERGY_AMOUNT)
    
    # Формируем сообщение
    message = f"{character.name} отдыхает и восстанавливает {RESTORE_ENERGY_AMOUNT} энергии"
    battle_logger.log(message, character=character)
