import random
from xxlimited import Str
from Battle.battle_logger import battle_logger
from Battle.battle_statistics import CombatActionRecord, get_battle_statistics
from Characters.Status_effects import status_effect
from Characters.behavior import decide_action

def battle_round(players, enemies, battle_logger) -> str:
    """Один раунд боя"""
    
    battle_result: str = "draw"
    #эффекты срабатывающие в начале раунда
    pre_round_processing(players, enemies)

    # --- Ход игроков ---
    for player in players:
        if not player.is_alive():
            continue

        # Используем логику поведения для принятия решения
        action_result = decide_action(player, players, [e for e in enemies if e.is_alive()])
        log_result(action_result)

        # Простая проверка победы после каждого действия игрока
        if all(not e.is_alive() for e in enemies):
            return "win" # Возвращаем результат

    # --- Ход врагов ---
    for enemy in enemies:
        if not enemy.is_alive():
            continue

        # Используем логику поведения для принятия решения
        action_result = decide_action(enemy, enemies, [p for p in players if p.is_alive()])
        log_result(action_result)

        # Простая проверка поражения после каждого действия врага
        if all(not p.is_alive() for p in players):
            battle_logger.log("☠️ ПОРАЖЕНИЕ! Вся команда погибла...")
            battle_result = "loss"
            return battle_result # Возвращаем результат
        
    # Обновляем кулдауны способностей
    post_round_processing(players, enemies)
    
    # В любом случае завершаем бой без вывода статистики
    return battle_result # Возвращаем результат

def pre_round_processing(players, enemies):
    for player in players:
        results = player.status_manager.update_effects()
        for result in results:
            log_result(result)

    for enemy in enemies:
        results = enemy.status_manager.update_effects()
        for result in results:
            log_result(result)

def post_round_processing(players, enemies):

    for player in players:
        player.ability_manager.update_cooldowns()
    
    for enemy in enemies:
        enemy.ability_manager.update_cooldowns()

def log_result(action_result) -> None:

    if action_result:
        #Статистика
        stats = get_battle_statistics()
        action_record = CombatActionRecord.from_ability_result(action_result)
        stats.add_combat_action(action_record) 

        for message in action_result.messages:
            battle_logger.log(message)
    else:
        battle_logger.log_enemy_action("что-то не так при использовании способности")

def display_round_separator(round_num):
    """Отображает красивый разделитель раундов"""
    battle_logger.log("") # Пустая строка перед новым раундом
    #separator = f"◦•●◉✿◉●•◦•●◉✿◉●•◦•●◉✿◉●•(раунд: {round_num})•●◉✿◉●•◦•●◉✿◉●•◦•●◉✿◉●•◦"
    separator = [
    ("◦", 1), ("•", 2), ("●", 3), ("◉", 4), ("✿", 5), ("◉", 4), ("●", 3), ("•", 2), ("◦", 1),
    ("•", 6), ("●", 1), ("◉", 2), ("✿", 3), ("◉", 4), ("●", 5), ("•", 6), ("◦", 1),
    ("•", 2), ("●", 3), ("◉", 4), ("✿", 5), ("◉", 4), ("●", 3), ("•", 2), ("◦", 1),
    (f"(раунд: {round_num})", 8),  # Желтый цвет для основного текста
    ("•", 6), ("●", 1), ("◉", 2), ("✿", 3), ("◉", 4), ("●", 5), ("•", 6), ("◦", 1),
    ("•", 2), ("●", 3), ("◉", 4), ("✿", 5), ("◉", 4), ("●", 3), ("•", 2), ("◦", 1),
    ("•", 6), ("●", 1), ("◉", 2), ("✿", 3), ("◉", 4), ("●", 5), ("•", 6), ("◦", 1)
    ]
    
    battle_logger.log(separator)