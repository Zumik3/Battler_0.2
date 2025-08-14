# character.py

from typing import TYPE_CHECKING, List, Dict, Any, Optional

from Characters.base_stats import DerivedStats, Stats
from Config.game_config import BASE_ENERGY_COST

if TYPE_CHECKING:
    from Characters.Abilities.ability import AbilityManager
    from Characters.Status_effects.status_manager import StatusEffectManager


class Character:
    """Базовый класс, представляющий персонажа в игре."""

    def __init__(self, name: str, role: str, level: int = 1, is_player: bool = False, can_heal: bool = False):
        self.name = name
        self.role = role
        self.is_player = is_player
        self.level = level
        self.alive = True
        self.can_heal = can_heal
        
        # Создаем объекты характеристик
        self.stats = Stats(self)
        self.derived_stats = DerivedStats(self.stats, self.role, self.level)
        
        # Инициализируем hp и энергию
        self.hp = self.derived_stats.max_hp
        self.energy = self.derived_stats.max_energy
        
        # Способности (ленивый импорт)
        self._ability_manager = None
        
        # Статус-эффекты (ленивый импорт)
        self._status_manager = None

    # ==================== Свойства ====================
    @property
    def ability_manager(self) -> 'AbilityManager':
        """Ленивое создание менеджера способностей"""
        if self._ability_manager is None:
            from Characters.Abilities.ability_manager import AbilityManager
            self._ability_manager = AbilityManager()
        return self._ability_manager

    @property
    def status_manager(self) -> 'StatusEffectManager':
        """Ленивое создание менеджера статус-эффектов"""
        if self._status_manager is None:
            from Characters.Status_effects.status_manager import StatusEffectManager
            self._status_manager = StatusEffectManager(self)
        return self._status_manager

    # ==================== Основные методы персонажа ====================
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.alive

    def get_level(self) -> int:
        """Возвращает уровень персонажа."""
        return self.level

    def on_death(self) -> None:
        """Вызывается при смерти персонажа. Очищает статус-эффекты и выводит сообщение."""
        # Очищаем все активные статус-эффекты
        if self._status_manager is not None:
            self.status_manager.clear_all_effects()
        
        # Выводим сообщение о смерти персонажа
        print(f"{self.name} погибает!")

    # ==================== Боевые методы ====================
    def take_damage(self, damage: int) -> bool:
        """Наносит урон персонажу, учитывая защиту."""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            if self.alive:  # Проверяем, чтобы не вызывать on_death дважды
                self.alive = False
                self.on_death()
        return True

    def take_heal(self, heal_amount: int) -> int:
        """Исцеляет персонажа и возвращает количество восстановленного HP."""
        old_hp = self.hp
        self.hp = min(self.derived_stats.max_hp, self.hp + int(heal_amount))
        return self.hp - old_hp

    # ==================== Энергия ====================
    def restore_energy(self, amount: Optional[int] = None, percentage: Optional[int] = None) -> None:
        """
        Восстанавливает энергию персонажа.
        :param amount: конкретное количество энергии для восстановления
        :param percentage: процент от максимальной энергии для восстановления
        """
        if percentage is not None:
            # Восстанавливаем указанный процент от максимальной энергии
            restore_amount = int(self.derived_stats.max_energy * (percentage / 100))
            self.energy = min(self.derived_stats.max_energy, self.energy + restore_amount)
        elif amount is not None:
            # Восстанавливаем конкретное количество энергии
            self.energy = min(self.derived_stats.max_energy, self.energy + amount)
        else:
            # Полное восстановление
            self.energy = self.derived_stats.max_energy

    def spend_energy(self, amount: int = BASE_ENERGY_COST) -> None:
        """Тратит энергию персонажа."""
        self.energy -= amount

    # ==================== Статистика ====================
    @staticmethod
    def scale_stats(base_stats: Dict[str, int], level: int, growth_rates: Dict[str, float]) -> Dict[str, int]:
        """Масштабирует характеристики в зависимости от уровня."""
        scaled_stats = {}
        for stat, base_value in base_stats.items():
            growth_rate = growth_rates.get(stat, 0.05)
            scaled_stats[stat] = int(base_value * (1 + (level - 1) * growth_rate))
        return scaled_stats

    # ==================== Способности ====================
    def add_ability(self, name: str, ability: Any) -> None:
        """Добавляет способность персонажу."""
        self.ability_manager.add_ability(name, ability)

    def get_available_abilities(self) -> List[str]:
        """Получает список доступных способностей."""
        return self.ability_manager.get_available_abilities(self)

    def use_ability(self, name: str, targets: List['Character'], **kwargs) -> Any:
        """Использует способность по имени."""
        return self.ability_manager.use_ability(name, self, targets, **kwargs)

    def update_ability_cooldowns(self) -> None:
        """Обновляет кулдауны способностей в конце раунда."""
        self.ability_manager.update_cooldowns()

    # ==================== Статус-эффекты ====================
    def add_status_effect(self, effect: Any) -> Dict[str, str]:
        """Добавляет статус-эффект персонажу."""
        return self.status_manager.add_effect(effect)

    def remove_status_effect(self, effect_name: str) -> bool:
        """Удаляет статус-эффект по имени."""
        return self.status_manager.remove_effect(effect_name)

    def update_status_effects(self) -> List[Dict[str, str]]:
        """Обновляет все активные статус-эффекты."""
        return self.status_manager.update_effects()

    def has_status_effect(self, effect_name: str) -> bool:
        """Проверяет, есть ли у персонажа определенный статус-эффект."""
        return self.status_manager.has_effect(effect_name)

    def get_active_status_effects(self) -> List[Any]:
        """Возвращает список всех активных статус-эффектов."""
        return self.status_manager.get_all_effects()