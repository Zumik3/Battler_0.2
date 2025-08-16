import uuid
from typing import List, Dict, Any, Optional

from Battle.battle_logger import battle_logger
from Battle.battle_statistics import get_battle_statistics
from Battle.round_logic import battle_round, display_round_separator
from Battle.rewards import BattleRewards
from Config.game_config import MAX_ROUNDS
from Inventory.inventory import get_inventory

# Для аннотаций типов избегаем циклических импортов
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Characters.character import Character


class BattleSimulator:
    """Класс для управления симуляцией боя."""

    # ==================== Основная логика боя ====================
    @staticmethod
    def simulate_battle(players: List['Character'], enemies: List['Character']) -> str:
        """
        Симулирует бой между игроками и врагами.
        
        :param players: Список игроков
        :param enemies: Список врагов
        :return: Результат битвы ("win", "loss", или "draw")
        """
        # Подготовка перед боем
        BattleSimulator.pre_battle_setup(players, enemies)
        
        # Начало боя
        battle_logger.log("")
        battle_logger.log("🏁 БОЙ НАЧИНАЕТСЯ!")
        battle_result = "draw"  # По умолчанию - ничья
        
        # Начало записи статистики
        battle_id = str(uuid.uuid4())
        stats = get_battle_statistics()
        stats.start_battle_tracking(battle_id, players, enemies)

        # Основной цикл боя
        for round_num in range(1, MAX_ROUNDS + 1):
            display_round_separator(round_num)
            round_result = battle_round(players, enemies, battle_logger)
            
            if round_result in ["win", "loss"]:
                battle_result = round_result
                break  # Заканчиваем бой
            
            if round_num == MAX_ROUNDS:
                battle_logger.log(f"⏳ Время вышло! Раунд {round_num} стал последним.")

        # Все действия после боя
        # Статистика после боя
        stats.end_battle(battle_id, True, 1)

        BattleSimulator.post_battle_processing(players, enemies, battle_result)
        
        return battle_result

    # ==================== Подготовка и завершение боя ====================
    @staticmethod
    def pre_battle_setup(players: List['Character'], enemies: List['Character']) -> None:
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

    @staticmethod
    def post_battle_processing(players: List['Character'], enemies: List['Character'], battle_result: str) -> None:
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
            BattleSimulator.award_rewards(players, enemies)
            # Восстановление энергии всем выжившим игрокам
            BattleSimulator.restore_energy_after_battle([p for p in players if p.is_alive()])
            battle_logger.set_message_delay()
        
        # Сброс кулдаунов всех способностей и статус эффектов у всех персонажей
        BattleSimulator.reset_all_cooldowns(players + enemies)
        BattleSimulator.reset_all_effects(players + enemies)

    # ==================== Награды и восстановление ====================
    @staticmethod
    def award_rewards(players: List['Character'], defeated_enemies: List['Character']) -> None:
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

    @staticmethod
    def restore_energy_after_battle(players: List['Character']) -> None:
        """
        Восстанавливает 30% максимальной энергии всем выжившим игрокам после боя.
        
        :param players: Список игроков
        """
        for player in players:
            if player.is_alive():
                player.restore_energy(percentage=30)
        
        # battle_logger.log(f"🧘 Команда восстанавливает часть энергии после боя")

    # ==================== Сброс состояний ====================
    @staticmethod
    def reset_all_cooldowns(characters: List['Character']) -> None:
        """
        Сбрасывает все кулдауны способностей у всех персонажей.
        
        :param characters: Список персонажей
        """
        for character in characters:
            if hasattr(character, 'ability_manager') and character.ability_manager is not None:
                character.ability_manager.reset_all_cooldowns()

    @staticmethod
    def reset_all_effects(characters: List['Character']) -> None:
        """
        Сбрасывает все статус-эффекты у всех персонажей.
        
        :param characters: Список персонажей
        """
        for character in characters:
            if hasattr(character, 'status_manager') and character.status_manager is not None:
                character.status_manager.clear_all_effects()


# ==================== Совместимость с предыдущим API ====================
def simulate_battle(players: List['Character'], enemies: List['Character']) -> str:
    """Совместимость с предыдущим API."""
    return BattleSimulator.simulate_battle(players, enemies)

def pre_battle_setup(players: List['Character'], enemies: List['Character']) -> None:
    """Совместимость с предыдущим API."""
    BattleSimulator.pre_battle_setup(players, enemies)

def post_battle_processing(players: List['Character'], enemies: List['Character'], battle_result: str) -> None:
    """Совместимость с предыдущим API."""
    BattleSimulator.post_battle_processing(players, enemies, battle_result)

def award_rewards(players: List['Character'], defeated_enemies: List['Character']) -> None:
    """Совместимость с предыдущим API."""
    BattleSimulator.award_rewards(players, defeated_enemies)

def restore_energy_after_battle(players: List['Character']) -> None:
    """Совместимость с предыдущим API."""
    BattleSimulator.restore_energy_after_battle(players)

def reset_all_cooldowns(characters: List['Character']) -> None:
    """Совместимость с предыдущим API."""
    BattleSimulator.reset_all_cooldowns(characters)

def reset_all_effects(characters: List['Character']) -> None:
    """Совместимость с предыдущим API."""
    BattleSimulator.reset_all_effects(characters)