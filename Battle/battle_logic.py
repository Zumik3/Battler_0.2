import random
from Battle.battle_logger import battle_logger
from Battle.round_logic import battle_round, display_round_separator
from Battle.rewards import BattleRewards
from Config.game_config import MAX_ROUNDS
from Inventory.inventory import get_inventory

def pre_battle_setup(players, enemies) -> None:
    """
    Выполняет подготовку перед началом боя.
    
    :param players: Список игроков
    :param enemies: Список врагов
    """
    # TODO: Добавить логику подготовки перед боем
    # Например:
    # - Проверка состояния персонажей
    # - Инициализация специальных эффектов
    # - Подготовка окружения боя
    # - Отображение информации о противниках
    pass

def simulate_battle(players, enemies) -> str:
    """
    Симулирует бой между игроками и врагами.
    
    :return: Результат битвы ("win", "loss", или "draw")
    """
    # Подготовка перед боем
    pre_battle_setup(players, enemies)
    
    # Начало боя
    battle_logger.log("")
    battle_logger.log("🏁 БОЙ НАЧИНАЕТСЯ!")
    battle_result = "draw"  # По умолчанию - ничья
    
    # Основной цикл боя
    for round_num in range(1, MAX_ROUNDS + 1):
        
        display_round_separator(round_num)
        round_result = battle_round(players, enemies, battle_logger)
        
        if round_result == "win" or round_result == "loss":
            battle_result = round_result
            break  # Заканчиваем бой
        
        if round_num == MAX_ROUNDS:
            battle_logger.log(f"⏳ Время вышло! Раунд {round_num} стал последним.")

    # Все действия после боя
    post_battle_processing(players, enemies, battle_result)
    
    return battle_result

def post_battle_processing(players, enemies, battle_result) -> None:
    """
    Выполняет все действия после завершения боя.
    
    :param players: Список игроков
    :param enemies: Список врагов
    :param battle_result: Результат боя ("win", "loss", "draw")
    """
    # Начисляем награды при победе
    if battle_result == "win":
        
        battle_logger.set_message_delay(0)

        battle_logger.log(f"🎖️ ПОБЕДА! Все враги повержены!")
        award_rewards(players, enemies)
        # Восстановление энергии всем выжившим игрокам
        restore_energy_after_battle([p for p in players if p.is_alive()])

        battle_logger.set_message_delay()
    
    # Сброс кулдаунов всех способностей у всех персонажей
    reset_all_cooldowns(players + enemies)

def award_rewards(players, defeated_enemies) -> None:
    """
    Начисляет награды игрокам за победу в бою.
    
    :param players: Список игроков
    :param defeated_enemies: Список побежденных врагов
    """
    if not defeated_enemies:
        return
    
    # Распределяем награды между выжившими игроками
    alive_players = [p for p in players if p.is_alive()]
    
    if not alive_players:
        return
    
    # Получаем награды
    reward_results = BattleRewards.distribute_rewards(defeated_enemies, alive_players)
    
    # Выводим сообщения о наградах
    for message in reward_results['messages']:
        battle_logger.log(message)

    for message in reward_results['level_up_messages']:
        battle_logger.log(message)

def restore_energy_after_battle(players) -> None:
    """
    Восстанавливает 30% максимальной энергии всем выжившим игрокам после боя.
    
    :param players: Список игроков
    """
    for player in players:
        if player.is_alive():
            player.restore_energy(percentage=30)
    
    #battle_logger.log(f"🧘 Команда восстанавливает часть энергии после боя")

def reset_all_cooldowns(characters) -> None:
    """
    Сбрасывает все кулдауны способностей у всех персонажей.
    
    :param characters: Список персонажей
    """
    for character in characters:
        if hasattr(character, 'ability_manager'):
            character.ability_manager.reset_all_cooldowns()