# battle/battle_statistics.py

from typing import Any, List, Dict, Optional, DefaultDict
from dataclasses import dataclass, field
from collections import defaultdict

from Characters.Abilities.ability import AbilityResult

@dataclass
class CharacterBattleStats:
    """Статистика конкретного персонажа в битве"""
    name: str
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    total_healing_done: int = 0
    total_healing_received: int = 0
    abilities_damage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))  # способность -> урон
    abilities_healing: Dict[str, int] = field(default_factory=lambda: defaultdict(int))  # способность -> лечение
    critical_hits: int = 0
    dodges: int = 0
    abilities_used: Dict[str, int] = field(default_factory=lambda: defaultdict(int))  # способность -> количество использований
    survived: bool = True

@dataclass
class CombatActionRecord:
    """Детальная запись о боевом действии"""
    round_number: int
    attacker_name: str
    target_name: str
    ability_name: str
    damage_dealt: int
    damage_blocked: int
    is_critical: bool
    is_dodge: bool
    heal_amount: int
    attacker_hp_before: int
    attacker_hp_after: int
    target_hp_before: int
    target_hp_after: int
    energy_cost: int
    additional_effects: List[str]
    battle_id: str
    
    @classmethod
    def from_ability_result(cls, ability_result: AbilityResult, **kwargs) -> 'CombatActionRecord':
        """
        Создает CombatActionRecord из AbilityResult
        Все недостающие параметры передаются через kwargs
        
        :param ability_result: Результат выполнения способности
        :param kwargs: Дополнительные параметры (round_number, attacker_name, target_name, и т.д.)
        :return: CombatActionRecord
        """
        # Извлекаем дополнительную информацию из details если есть
        damage_blocked = 0
        is_dodge = False
        additional_effects = []
        
        # Пытаемся получить информацию из details
        if hasattr(ability_result, 'details'):
            # Для атакующих способностей
            if 'target_info' in ability_result.details:
                target_info = ability_result.details['target_info']
                damage_blocked = target_info.get('damage_blocked', 0)
                is_dodge = target_info.get('dodge', False)
            
            # Для массовых атак
            if 'targets_info' in ability_result.details:
                # Берем информацию по первой цели или суммируем
                targets_info = ability_result.details['targets_info']
                if targets_info:
                    first_target_info = next(iter(targets_info.values()))
                    damage_blocked = first_target_info.get('damage_blocked', 0)
                    is_dodge = first_target_info.get('dodge', False)
            
            # Эффекты из details
            if 'effects' in ability_result.details:
                additional_effects = ability_result.details['effects']
        
        return cls(
            round_number=kwargs.get('round_number', 0),
            attacker_name=kwargs.get('attacker_name', getattr(ability_result, 'character', '')),
            target_name=kwargs.get('target_name', ''),
            ability_name=kwargs.get('ability_name', getattr(ability_result, 'ability_type', '')),
            damage_dealt=getattr(ability_result, 'damage_dealt', 0),
            damage_blocked=damage_blocked,
            is_critical=getattr(ability_result, 'is_critical', False),
            is_dodge=is_dodge,
            heal_amount=getattr(ability_result, 'heal_amount', 0),
            attacker_hp_before=kwargs.get('attacker_hp_before', 0),
            attacker_hp_after=kwargs.get('attacker_hp_after', 0),
            target_hp_before=kwargs.get('target_hp_before', 0),
            target_hp_after=kwargs.get('target_hp_after', 0),
            energy_cost=kwargs.get('energy_cost', 0),
            additional_effects=additional_effects,
            battle_id=kwargs.get('battle_id', '')
        )

@dataclass
class BattleInProgress:
    """Текущая статистика битвы в процессе"""
    battle_id: str
    total_rounds: int = 0
    player_names: List[str] = field(default_factory=list)
    enemy_names: List[str] = field(default_factory=list)
    total_damage_dealt_by_players: int = 0
    total_damage_dealt_to_players: int = 0
    total_healing_done: int = 0
    abilities_used: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    critical_hits_count: int = 0
    dodges_count: int = 0
    special_effects_triggered: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    participants: set = field(default_factory=set)  # Все участники битвы
    character_stats: Dict[str, CharacterBattleStats] = field(default_factory=dict)  # Статистика по персонажам

@dataclass
class BattleSummaryRecord:
    """Суммирующая информация по битве"""
    battle_id: str
    total_rounds: int
    player_names: List[str]
    enemy_names: List[str]
    player_victory: bool
    total_damage_dealt_by_players: int
    total_damage_dealt_to_players: int
    total_healing_done: int
    abilities_used: Dict[str, int]
    critical_hits_count: int
    dodges_count: int
    player_survival_rate: float
    special_effects_triggered: Dict[str, int]
    character_stats: Dict[str, CharacterBattleStats]  # Детальная статистика по каждому персонажу

@dataclass
class GameTotalsRecord:
    """Итоговая запись со статистикой за всю игру"""
    total_battles: int = 0
    total_victories: int = 0
    total_defeats: int = 0
    total_enemies_defeated: int = 0
    total_player_deaths: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    total_healing_done: int = 0
    most_used_ability: str = ""
    most_damage_in_single_battle: int = 0
    longest_battle_rounds: int = 0
    favorite_class: str = ""
    achievements_unlocked: List[str] = field(default_factory=list)
    battles_by_difficulty: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

class BattleStatistics:
    """Синглтон класс для хранения боевой статистики"""
    _instance: Optional['BattleStatistics'] = None
    
    def __new__(cls) -> 'BattleStatistics':
        if cls._instance is None:
            cls._instance = super(BattleStatistics, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        # Инициализируем только один раз
        if not hasattr(self, '_initialized'):
            self.detailed_records: List[CombatActionRecord] = []
            self.battle_summaries: List[BattleSummaryRecord] = []
            self.game_totals: GameTotalsRecord = GameTotalsRecord()
            self.current_battles: Dict[str, BattleInProgress] = {}  # Активные битвы
            self._initialized = True
    
    def start_battle_tracking(self, battle_id: str, players: List[Any], 
                            enemies: List[Any]) -> None:
        """Начинает отслеживание новой битвы"""

        player_names = [player.name for player in players]
        enemy_names = [enemy.name for enemy in enemies]

        # Инициализируем статистику для каждого персонажа
        character_stats = {}
        for name in player_names + enemy_names:
            character_stats[name] = CharacterBattleStats(name=name)
            
        self.current_battles[battle_id] = BattleInProgress(
            battle_id=battle_id,
            player_names=player_names,
            enemy_names=enemy_names,
            participants=set(player_names + enemy_names),
            character_stats=character_stats
        )
    
    def add_combat_action(self, record: CombatActionRecord) -> None:
        """Добавляет детальную запись о боевом действии и обновляет статистику"""
        # Добавляем детальную запись
        self.detailed_records.append(record)
        
        # Обновляем статистику текущей битвы
        self._update_battle_statistics(record)
        
        # Обновляем итоговую статистику игры
        self._update_game_totals_from_action(record)
    
    def _update_battle_statistics(self, record: CombatActionRecord) -> None:
        """Обновляет статистику текущей битвы на основе действия"""
        battle = self.current_battles.get(record.battle_id)
        if not battle:
            return
        
        # Обновляем максимальный номер раунда
        battle.total_rounds = max(battle.total_rounds, record.round_number)
        
        # Обновляем участников
        battle.participants.add(record.attacker_name)
        battle.participants.add(record.target_name)
        
        # Получаем статистику персонажей
        attacker_stats = battle.character_stats.get(record.attacker_name)
        target_stats = battle.character_stats.get(record.target_name)
        
        if not attacker_stats:
            attacker_stats = CharacterBattleStats(name=record.attacker_name)
            battle.character_stats[record.attacker_name] = attacker_stats
            
        if not target_stats:
            target_stats = CharacterBattleStats(name=record.target_name)
            battle.character_stats[record.target_name] = target_stats
        
        # Обновляем статистику атакующего
        if record.damage_dealt > 0:
            attacker_stats.total_damage_dealt += record.damage_dealt
            attacker_stats.abilities_damage[record.ability_name] += record.damage_dealt
            attacker_stats.abilities_used[record.ability_name] += 1
            
            # Обновляем общую статистику битвы
            is_player_attacker = record.attacker_name in battle.player_names
            if is_player_attacker:
                battle.total_damage_dealt_by_players += record.damage_dealt
            else:
                battle.total_damage_dealt_to_players += record.damage_dealt
        
        # Обновляем лечение
        if record.heal_amount > 0:
            attacker_stats.total_healing_done += record.heal_amount
            attacker_stats.abilities_healing[record.ability_name] += record.heal_amount
            attacker_stats.abilities_used[record.ability_name] += 1
            battle.total_healing_done += record.heal_amount
        
        # Обновляем статистику цели
        if record.damage_dealt > 0:
            target_stats.total_damage_taken += record.damage_dealt
        
        if record.heal_amount > 0:
            target_stats.total_healing_received += record.heal_amount
        
        # Обновляем критические удары
        if record.is_critical:
            attacker_stats.critical_hits += 1
            battle.critical_hits_count += 1
        
        # Обновляем уклонения
        if record.is_dodge:
            target_stats.dodges += 1
            battle.dodges_count += 1
        
        # Обновляем специальные эффекты
        for effect in record.additional_effects:
            battle.special_effects_triggered[effect] += 1
        
        # Обновляем использованные способности на уровне битвы
        battle.abilities_used[record.ability_name] += 1
    
    def _update_game_totals_from_action(self, record: CombatActionRecord) -> None:
        """Обновляет итоговую статистику игры на основе действия"""
        # Обновляем общий урон
        self.game_totals.total_damage_dealt += record.damage_dealt
        self.game_totals.total_healing_done += record.heal_amount
        pass
    
    def end_battle(self, battle_id: str, player_victory: bool, 
                   player_survival_rate: float) -> None:
        """Завершает отслеживание битвы и сохраняет итоги"""
        battle = self.current_battles.pop(battle_id, None)
        if not battle:
            return
        
        # Обновляем статистику выживания
        self._update_survival_stats(battle, player_victory)
        
        # Создаем итоговую запись битвы
        battle_summary = BattleSummaryRecord(
            battle_id=battle.battle_id,
            total_rounds=battle.total_rounds,
            player_names=battle.player_names,
            enemy_names=battle.enemy_names,
            player_victory=player_victory,
            total_damage_dealt_by_players=battle.total_damage_dealt_by_players,
            total_damage_dealt_to_players=battle.total_damage_dealt_to_players,
            total_healing_done=battle.total_healing_done,
            abilities_used=dict(battle.abilities_used),
            critical_hits_count=battle.critical_hits_count,
            dodges_count=battle.dodges_count,
            player_survival_rate=player_survival_rate,
            special_effects_triggered=dict(battle.special_effects_triggered),
            character_stats=battle.character_stats  # Детальная статистика по персонажам
        )
        
        # Добавляем итог битвы
        self.battle_summaries.append(battle_summary)
        
        # Обновляем итоговую статистику игры
        self._update_game_totals_from_battle(battle_summary)
    
    def _update_survival_stats(self, battle: BattleInProgress, player_victory: bool) -> None:
        """Обновляет статистику выживания персонажей"""
        # Здесь можно добавить логику определения выживших персонажей
        # Пока просто помечаем всех как выживших
        pass
    
    def _update_game_totals_from_battle(self, battle_record: BattleSummaryRecord) -> None:
        """Обновляет итоговую статистику на основе результатов битвы"""
        self.game_totals.total_battles += 1
        if battle_record.player_victory:
            self.game_totals.total_victories += 1
        else:
            self.game_totals.total_defeats += 1
        
        self.game_totals.total_damage_dealt += battle_record.total_damage_dealt_by_players
        self.game_totals.total_damage_taken += battle_record.total_damage_dealt_to_players
        self.game_totals.total_healing_done += battle_record.total_healing_done
        
        # Обновляем максимальный урон в одной битве
        if battle_record.total_damage_dealt_by_players > self.game_totals.most_damage_in_single_battle:
            self.game_totals.most_damage_in_single_battle = battle_record.total_damage_dealt_by_players
            
        # Обновляем максимальное количество раундов в битве
        if battle_record.total_rounds > self.game_totals.longest_battle_rounds:
            self.game_totals.longest_battle_rounds = battle_record.total_rounds
    
    def get_detailed_records(self, battle_id: Optional[str] = None) -> List[CombatActionRecord]:
        """Возвращает детальные записи, опционально фильтруя по ID битвы"""
        if battle_id:
            return [record for record in self.detailed_records if record.battle_id == battle_id]
        return self.detailed_records.copy()
    
    def get_battle_summaries(self, player_victory: Optional[bool] = None) -> List[BattleSummaryRecord]:
        """Возвращает суммирующие записи, опционально фильтруя по результату"""
        if player_victory is not None:
            return [record for record in self.battle_summaries if record.player_victory == player_victory]
        return self.battle_summaries.copy()
    
    def get_current_game_totals(self) -> GameTotalsRecord:
        """Возвращает копию итоговой статистики"""
        return GameTotalsRecord(**self.game_totals.__dict__)
    
    def get_character_battle_stats(self, battle_id: str, character_name: str) -> Optional[CharacterBattleStats]:
        """Возвращает статистику конкретного персонажа в конкретной битве"""
        battle = next((b for b in self.battle_summaries if b.battle_id == battle_id), None)
        if battle and character_name in battle.character_stats:
            return battle.character_stats[character_name]
        return None
    
    def get_character_overall_stats(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает общую статистику по всем персонажам за все битвы"""
        character_stats = defaultdict(lambda: {
            'total_battles': 0,
            'total_damage_dealt': 0,
            'total_damage_taken': 0,
            'total_healing_done': 0,
            'total_healing_received': 0,
            'abilities_damage': defaultdict(int),
            'abilities_healing': defaultdict(int),
            'critical_hits': 0,
            'dodges': 0,
            'battles_won': 0
        })
        
        # Собираем статистику со всех битв
        for battle in self.battle_summaries:
            for char_name, char_stats in battle.character_stats.items():
                stats = character_stats[char_name]
                stats['total_battles'] += 1
                stats['total_damage_dealt'] += char_stats.total_damage_dealt
                stats['total_damage_taken'] += char_stats.total_damage_taken
                stats['total_healing_done'] += char_stats.total_healing_done
                stats['total_healing_received'] += char_stats.total_healing_received
                stats['critical_hits'] += char_stats.critical_hits
                stats['dodges'] += char_stats.dodges
                
                if battle.player_victory and char_name in battle.player_names:
                    stats['battles_won'] += 1
                
                # Суммируем урон и лечение по способностям
                for ability, damage in char_stats.abilities_damage.items():
                    stats['abilities_damage'][ability] += damage
                for ability, healing in char_stats.abilities_healing.items():
                    stats['abilities_healing'][ability] += healing
        
        return dict(character_stats)
    
    @classmethod
    def get_instance(cls) -> 'BattleStatistics':
        """Получить экземпляр singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Удобная функция для получения экземпляра статистики
def get_battle_statistics() -> BattleStatistics:
    """Получить singleton экземпляр BattleStatistics"""
    return BattleStatistics.get_instance()