import random

# === Функции анализа поля боя ===

def analyze_battlefield(character, allies, enemies):
    """
    Анализирует состояние поля боя и возвращает рекомендацию по действию.
    
    :param character: Персонаж, принимающий решение
    :param allies: Список союзников
    :param enemies: Список врагов
    :return: dict с анализом ситуации
    """
    # Фильтруем живых персонажей
    alive_allies = [a for a in allies if a.is_alive()]
    alive_enemies = [e for e in enemies if e.is_alive()]
    
    # Анализ союзников - только для хилера пока
    if character.can_heal:
        allies_hp_ratio = []
        allies_need_healing = []
        allies_critical = []
        
        for ally in alive_allies:
            hp_ratio = ally.hp / ally.derived_stats.max_hp
            allies_hp_ratio.append(hp_ratio)
            
            if hp_ratio < 0.9:  # Ниже 90% HP
                allies_need_healing.append(ally)
            if hp_ratio < 0.5:  # Ниже 50% HP - критическое состояние
                allies_critical.append(ally)
        
        avg_allies_hp = sum(allies_hp_ratio) / len(allies_hp_ratio) if allies_hp_ratio else 1.0
    else:
        avg_allies_hp = 1.0 # пока заглушка для остальных
    
    # Анализ врагов
    enemies_hp_ratio = []
    weak_enemies = []
    strong_enemies = []
    
    for enemy in alive_enemies:
        hp_ratio = enemy.hp / enemy.derived_stats.max_hp
        enemies_hp_ratio.append(hp_ratio)
        
        if hp_ratio < 0.3:  # Слабые враги
            weak_enemies.append(enemy)
        elif hp_ratio > 0.7:  # Сильные враги
            strong_enemies.append(enemy)
    
    avg_enemies_hp = sum(enemies_hp_ratio) / len(enemies_hp_ratio) if enemies_hp_ratio else 1.0
    
    # Анализ энергии персонажа
    energy_ratio = character.energy / character.derived_stats.max_energy if hasattr(character, 'energy') else 1.0
    
    # Определяем приоритет действия
    action_priority = determine_action_priority(
        character, 
        avg_allies_hp, 
        len(allies_critical) if 'allies_critical' in locals() else 0, 
        len(allies_need_healing) if 'allies_need_healing' in locals() else 0, 
        avg_enemies_hp, 
        len(weak_enemies), 
        energy_ratio
    )
    
    return {
        'alive_allies_count': len(alive_allies),
        'alive_enemies_count': len(alive_enemies),
        'avg_allies_hp': avg_allies_hp,
        'avg_enemies_hp': avg_enemies_hp,
        'allies_need_healing': allies_need_healing if 'allies_need_healing' in locals() else [],
        'allies_critical': allies_critical if 'allies_critical' in locals() else [],
        'weak_enemies': weak_enemies,
        'strong_enemies': strong_enemies,
        'energy_ratio': energy_ratio,
        'action_priority': action_priority
    }

def determine_action_priority(character, avg_allies_hp, critical_allies_count, healing_needed_count, 
                            avg_enemies_hp, weak_enemies_count, energy_ratio):
    """
    Определяет приоритет действия на основе анализа.
    """
    
    # Приоритеты: heal, attack, rest
    priorities = []
    
    # Лечение - высокий приоритет, если есть раненые союзники
    heal_priority = 0
    if character.can_heal:
        # Для лекарей лечение приоритетнее

        if critical_allies_count > 0:
            heal_priority = 90  # Очень высокий приоритет
        elif healing_needed_count > 1:
            heal_priority = 70  # Высокий приоритет
    
    # Атака - приоритет зависит от состояния врагов и союзников
    attack_priority = 0
    if avg_enemies_hp < 0.3 and weak_enemies_count > 0:
        attack_priority = 80  # Добивание слабых врагов
    elif avg_allies_hp > 0.7:  # Союзники в хорошем состоянии
        attack_priority = 60
    elif not character.can_heal:  # Не-лекари склонны атаковать
        attack_priority = 50 + (1 - avg_enemies_hp) * 30
    else:  # Лекари атакуют реже
        attack_priority = 30 + (1 - avg_enemies_hp) * 20
    
    # Отдых - приоритет когда мало энергии и не критическая ситуация
    rest_priority = 0
    if energy_ratio < 0.2:
        if avg_allies_hp > 0.5 and critical_allies_count == 0:
            rest_priority = 70  # Хорошее время для отдыха
        else:
            rest_priority = 40  # Отдых, но не критично
    elif energy_ratio < 0.5:
        rest_priority = 20
    
    return {
        'heal': heal_priority,
        'attack': attack_priority,
        'rest': rest_priority
    }

def select_ability_based_on_analysis(character, analysis):
    """
    Выбирает способность на основе анализа поля боя.
    
    :param character: Персонаж
    :param analysis: Результат анализа поля боя
    :return: Ссылка на способность для использования (или None)
    """

    available_abilities = character.ability_manager.get_available_abilities(character)
    
    if not available_abilities:
        return None
    
    # Если отдых - единственная доступная способность, используем её
    if len(available_abilities) == 1 and _is_rest_ability(available_abilities[0]):
        return available_abilities[0]
    
    # Получаем приоритеты действий
    priorities = analysis['action_priority']
    
    # Фильтруем доступные способности по типам
    heal_abilities = [ability for ability in available_abilities if _is_heal_ability(ability)]
    attack_abilities = [ability for ability in available_abilities if _is_attack_ability(ability)]
    rest_abilities = [ability for ability in available_abilities if _is_rest_ability(ability)]
    
    # Выбираем действие с наивысшим приоритетом
    max_priority = max(priorities.values())
    chosen_action = None
    
    for action, priority in priorities.items():
        if priority == max_priority and priority > 0:
            chosen_action = action
            break
    
    # Если приоритеты равны нулю, выбираем случайно (но не отдых)
    if chosen_action is None:
        non_rest_abilities = [ability for ability in available_abilities if not _is_rest_ability(ability)]
        if non_rest_abilities:
            return random.choice(non_rest_abilities)
        elif rest_abilities:
            return random.choice(rest_abilities)
        else:
            return random.choice(available_abilities)
    
    # Выбираем конкретную способность в зависимости от действия
    if chosen_action == 'heal' and heal_abilities:
        # Выбираем наиболее подходящую лечебную способность
        single_heals = [a for a in heal_abilities if a.name.lower() in ['heal', 'лечить', 'лечение']]
        mass_heals = [a for a in heal_abilities if a.name.lower() in ['mass_heal', 'массовое лечение']]
        
        if analysis['allies_critical'] and single_heals:
            return random.choice(single_heals)
        elif (analysis['avg_allies_hp'] < 0.6 and mass_heals and analysis['alive_allies_count'] > 2):
            return random.choice(mass_heals)
        else:
            return random.choice(heal_abilities)
    
    elif chosen_action == 'attack' and attack_abilities:
        return random.choice(attack_abilities)
    
    elif chosen_action == 'rest' and rest_abilities:
        return random.choice(rest_abilities)
    
    # Фолбэк - если выбранное действие недоступно
    non_rest_abilities = [ability for ability in available_abilities if not _is_rest_ability(ability)]
    if non_rest_abilities:
        return random.choice(non_rest_abilities)
    elif rest_abilities:
        return random.choice(rest_abilities)
    else:
        return random.choice(available_abilities) if available_abilities else None

def _is_rest_ability(ability):
    """Проверяет, является ли способность отдыхом."""
    return ability.type == 2

def _is_heal_ability(ability):
    """Проверяет, является ли способность лечением."""
    return ability.type == 1

def _is_attack_ability(ability):
    """Проверяет, является ли способность атакой."""
    return ability.type == 0

# === Функции для выбора действия ===

def decide_action(character, allies, enemies):
    """
    Определяет, какое действие выполнит персонаж.
    :param character: Персонаж, принимающий решение.
    :param allies: Список живых союзников.
    :param enemies: Список живых врагов.
    :return: dict с результатом действия или None
    """
    # Фильтруем живых врагов и союзников
    alive_enemies = [e for e in enemies if e.is_alive()]
    alive_allies = [a for a in allies if a.is_alive()]
    
    if not alive_enemies and not alive_allies:
        # Если нет целей, возвращаем None
        return None
    
    # Анализируем поле боя
    analysis = analyze_battlefield(character, allies, enemies)
    
    # Выбираем способность на основе анализа
    chosen_ability = select_ability_based_on_analysis(character, analysis)
    
    if not chosen_ability:
        return None
    
    # Определяем цель
    target = None
    if _is_heal_ability(chosen_ability):
        # Для лечения выбираем самого раненого союзника
        if analysis['allies_critical']:
            target = min(analysis['allies_critical'], key=lambda x: x.hp/x.derived_stats.max_hp)
        elif analysis['allies_need_healing']:
            target = min(analysis['allies_need_healing'], key=lambda x: x.hp/x.derived_stats.max_hp)
        else:
            target = character  # Если некого лечить, лечим себя
    elif _is_rest_ability(chosen_ability):
        # Для отдыха цель - сам персонаж
        target = character
    elif chosen_ability.name.lower() in ['mass_heal', 'массовое лечение', 'mass_heal']:
        # Для массового лечения используем всех союзников
        target = alive_allies if alive_allies else [character]
    else:
        # Для атакующих способностей выбираем врага
        if analysis['weak_enemies']:
            # Предпочтительно атакуем слабых врагов
            target = random.choice(analysis['weak_enemies'])
        elif alive_enemies:
            target = random.choice(alive_enemies)
        else:
            target = None
    
    # Используем способность по ссылке и получаем результат
    if isinstance(target, list):
        result = character.ability_manager.use_ability(chosen_ability, character, target)
    else:
        result = character.ability_manager.use_ability(chosen_ability, character, [target] if target else [])
    
    # Если результат уже содержит сообщение, возвращаем его
    if result and isinstance(result, dict):
        if 'message' in result:
            return result
        # Если нет сообщения, но есть тип действия, создаем сообщение
        elif 'type' in result:
            if result['type'] == 'basic_attack':
                message = f"{character.name} атакует {result.get('target', 'цель')} и наносит {result.get('damage_dealt', 0)} урона!"
                result['message'] = message
                return result
            elif result['type'] == 'rest':
                message = f"{character.name} отдыхает и восстанавливает {result.get('energy_restored', 30)} энергии!"
                result['message'] = message
                return result
            elif result['type'] == 'heal':
                message = f"{character.name} лечит {result.get('target', 'союзника')} на {result.get('heal_amount', 0)} HP!"
                result['message'] = message
                return result
            elif result['type'] == 'mass_heal':
                message = f"{character.name} использует массовое лечение!"
                result['message'] = message
                return result
            elif result['type'] == 'splash_attack':
                message = f"{character.name} использует сплэш атаку!"
                result['message'] = message
                return result
    
    # Если нет результата или он некорректный, создаем базовый результат
    if not result:
        result = {
            'success': True,
            'message': f"{character.name} использует {chosen_ability.name}!"
        }
    
    return result