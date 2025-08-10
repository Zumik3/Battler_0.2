import random
from xxlimited import Str
from Battle.battle_logger import battle_logger
from Characters.behavior import decide_action

def battle_round(players, enemies, battle_logger) -> str:
    """Один раунд боя"""
    
    battle_result = None

    # --- Ход игроков ---
    for player in players:
        if not player.is_alive():
            continue

        # Используем логику поведения для принятия решения
        action_result = decide_action(player, players, [e for e in enemies if e.is_alive()])
        
        if action_result and 'message' in action_result:
            battle_logger.log(action_result['message'])

        # Простая проверка победы после каждого действия игрока
        if all(not e.is_alive() for e in enemies):
            battle_logger.log(f"🎖️ ПОБЕДА! Все враги повержены!")
            return "win" # Возвращаем результат

    # --- Ход врагов ---
    for enemy in enemies:
        if not enemy.is_alive():
            continue

        # Используем логику поведения для принятия решения
        action_result = decide_action(enemy, enemies, [p for p in players if p.is_alive()])
        
        if action_result and 'message' in action_result:
            battle_logger.log_enemy_action(action_result['message'])
        else:
            battle_logger.log_enemy_action("что-то не так при использовании способности")

        # Простая проверка поражения после каждого действия врага
        if all(not p.is_alive() for p in players):
            battle_logger.log("☠️ ПОРАЖЕНИЕ! Вся команда погибла...")
            battle_result = "loss"
            return battle_result # Возвращаем результат
        
    # Обновляем кулдауны способностей
    for player in players:
            player.ability_manager.update_cooldowns()
    
    for enemy in enemies:
            enemy.ability_manager.update_cooldowns()
    
    # В любом случае завершаем бой без вывода статистики
    return battle_result # Возвращаем результат

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