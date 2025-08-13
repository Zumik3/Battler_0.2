# Characters/Abilities/ability.py - Базовые классы способностей

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from Characters.character import Character
    from Characters.Status_effects.status_effect import Status_effect  # Предполагаемый импорт для типизации

# ==================== Результат информации о способности ====================
@dataclass
class AbilityInfo:
    """Класс для возврата информации о способности."""
    name: str
    type: int
    description: str
    level: int
    # Для активных способностей
    damage_scale: Optional[float] = None
    energy_cost: Optional[int] = None
    is_mass: Optional[bool] = None
    cooldown: Optional[int] = None
    current_cooldown: Optional[int] = None


# ==================== Результат способности ====================
@dataclass
class AbilityResult:
    """Класс для возврата результатов из способностей."""
    
    # Универсальные свойства для всех способностей
    success: bool = True
    ability_type: str = ""
    character: Optional['Character'] = None
    targets: List['Character'] = field(default_factory=list)
    messages: List[Any] = field(default_factory=list)
    damage_dealt: int = 0
    heal_amount: int = 0
    energy_restored: int = 0
    is_critical: bool = False
    total_damage: int = 0
    total_heal: int = 0
    reason: str = ""  # Причина неудачи
    details: Dict[str, Any] = field(default_factory=dict)  # Для дополнительной информации


# ==================== Базовый класс способности ====================
class Ability(ABC):
    """Абстрактный базовый класс для способностей - нельзя создавать напрямую"""
    
    def __init__(self, name: str, type: int = 0, description: str = "", icon: str = "") -> None:
        """
        Инициализация способности.
        
        :param name: Название способности
        :param type: Тип способности - 0 - атака, 1 - лечение, 2 - отдых и т.д.
        :param description: Описание способности
        :param icon: Иконка способности
        """
        self.name: str = name
        self.type: int = type
        self.level: int = 0  # Уровень способности (0 = недоступна)
        self.description: str = description
        self.icon: str = icon
    
    # ==================== Управление уровнями ====================
    def level_up(self) -> int:
        """Повышает уровень способности на 1"""
        self.level += 1
        return self.level
    
    def set_level(self, level: int) -> int:
        """Устанавливает уровень способности"""
        self.level = max(0, level)  # Уровень не может быть меньше 0
        return self.level
    
    def is_available(self) -> bool:
        """Проверяет, доступна ли способность (уровень > 0)"""
        return self.level > 0
    
    # ==================== Информация ====================
    def get_info(self) -> AbilityInfo:
        """Возвращает информацию о способности."""
        return AbilityInfo(
            name=self.name,
            type=self.type,
            description=self.description,
            level=self.level
        )
    
    # ==================== Абстрактные методы ====================
    @abstractmethod
    def can_use(self, character: 'Character', targets: Optional[List['Character']] = None) -> bool:
        """Абстрактный метод проверки возможности использования"""
        pass
    
    @abstractmethod
    def use(self, character: 'Character', targets: List['Character'], **kwargs: Any) -> AbilityResult:
        """Абстрактный метод использования способности"""
        pass


# ==================== Активная способность ====================
class ActiveAbility(Ability):
    """Активная способность - может быть использована игроком"""
    
    def __init__(self, name: str, type: int = 0, damage_scale: float = 0.0, cooldown: int = 1, 
                 energy_cost: int = 0, description: str = "", icon: str = "", is_mass: bool = False) -> None:
        """
        Инициализация активной способности.
        
        :param name: Название способности
        :param type: Тип способности - 0 - атака, 1 - лечение, 2 - отдых и т.д.
        :param damage_scale: Процент урона от атаки владельца
        :param cooldown: Количество раундов до восстановления способности
        :param energy_cost: Стоимость энергии для использования
        :param description: Описание способности
        :param icon: Иконка способности
        :param is_mass: Массовая способность
        """
        super().__init__(name, type, description, icon)
        self.damage_scale: float = damage_scale
        self.energy_cost: int = energy_cost
        self.is_mass: bool = is_mass
        self.cooldown: int = cooldown
        self.current_cooldown: int = 0
        self._applied_effects: Optional[List[Type['Status_effect']]] = None  # Ленивая инициализация
    
    # ==================== Управление эффектами ====================
    @property
    def applied_effects(self) -> List[Type['Status_effect']]:
        """Ленивое создание списка применяемых эффектов"""
        if self._applied_effects is None:
            self._applied_effects = []
        return self._applied_effects
    
    def add_effect(self, effect_class: Type['Status_effect']) -> None:
        """
        Добавляет эффект, который может быть применен этой способностью.
        
        :param effect_class: Класс эффекта
        """
        self.applied_effects.append(effect_class)
    
    def get_effects_info(self) -> List[Type['Status_effect']]:
        """Возвращает информацию о всех возможных эффектах способности"""
        if self._applied_effects is None:
            return []
        return self._applied_effects.copy()
    
    def clear_effects(self) -> None:
        """Очищает список применяемых эффектов"""
        if self._applied_effects is not None:
            self._applied_effects.clear()

    def add_effect_by_class_name(self, effect_class_name: str) -> bool:
        """
        Добавляет эффект в список применяемых эффектов по имени класса.
        
        :param effect_class_name: Имя класса эффекта
        :return: True если эффект добавлен, False если класс не найден
        """
        from Characters.Status_effects.status_manager import get_effect_class_by_name
        effect_class = get_effect_class_by_name(effect_class_name)
        if effect_class:
            self.applied_effects.append(effect_class)
            return True
        return False

    def add_effect_by_class(self, effect_class: type) -> None:
        """
        Добавляет эффект в список применяемых эффектов напрямую по классу.
        
        :param effect_class: Класс эффекта
        """
        self.applied_effects.append(effect_class)

    def get_effect_instances(self, **kwargs) -> List['Status_effect']:
        """
        Создает экземпляры всех применяемых эффектов.
        
        :param kwargs: Параметры для создания экземпляров эффектов
        :return: Список экземпляров эффектов
        """
        instances = []
        for effect_class in self.applied_effects:
            try:
                # Создаем экземпляр эффекта с переданными параметрами
                instance = effect_class(**kwargs)
                instances.append(instance)
            except Exception:
                # Если не удалось создать экземпляр, пропускаем
                continue
        return instances
    
    # ==================== Проверка возможности использования ====================
    def can_use(self, character: 'Character', targets: Optional[List['Character']] = None) -> bool:
        """
        Проверяет, может ли персонаж использовать активную способность.
        
        :param character: Персонаж, который хочет использовать способность
        :param targets: Цели (опционально)
        :return: True, если можно использовать, иначе False
        """
        # Проверяем уровень способности
        if self.level <= 0:
            return False
            
        # Проверяем кулдаун
        if self.current_cooldown > 0:
            return False
            
        # Проверяем энергию
        if hasattr(character, 'energy') and character.energy < self.energy_cost:
            return False
            
        # Проверяем специфические условия для способности
        return self.check_specific_conditions(character, targets or [])
    
    def check_specific_conditions(self, character: 'Character', targets: List['Character']) -> bool:
        """
        Проверяет специфические условия для использования способности.
        Переопределяется в подклассах.
        """
        return True
    
    # ==================== Использование способности ====================
    def use(self, character: 'Character', targets: List['Character'], **kwargs: Any) -> AbilityResult:
        """
        Использует активную способность.
        
        :param character: Персонаж, использующий способность
        :param targets: Список целей
        :param kwargs: Дополнительные параметры
        :return: Результат использования способности
        """
        if not self.can_use(character, targets):
            result = AbilityResult()
            result.success = False
            result.reason = "Невозможно использовать способность"
            result.ability_type = self.__class__.__name__.lower()
            result.character = character
            result.targets = targets
            return result
        
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
    
    def execute(self, character: 'Character', targets: List['Character'], **kwargs: Any) -> AbilityResult:
        """
        Выполняет логику способности. Переопределяется в подклассах.
        """
        raise NotImplementedError("Метод execute должен быть реализован в подклассе")
    
    # ==================== Управление кулдауном ====================
    def update_cooldown(self) -> None:
        """Обновляет кулдаун способности в конце раунда."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def on_use(self, character: 'Character', targets: List['Character'], result: AbilityResult) -> None:
        """
        Вызывается после использования способности.
        Можно использовать для обновления статистики и т.д.
        """
        pass
    
    # ==================== Информация ====================
    def get_info(self) -> AbilityInfo:
        """Возвращает информацию о активной способности."""
        base_info = super().get_info()
        return AbilityInfo(**base_info.__dict__ | {
            'damage_scale': self.damage_scale,
            'energy_cost': self.energy_cost,
            'is_mass': self.is_mass,
            'cooldown': self.cooldown,
            'current_cooldown': self.current_cooldown
        })


# ==================== Пассивная способность ====================
class PassiveAbility(Ability):
    """Пассивная способность - работает автоматически, не требует активации"""
    
    def __init__(self, name: str, type: int = 0, description: str = "", icon: str = "") -> None:
        """
        Инициализация пассивной способности.
        
        :param name: Название способности
        :param type: Тип способности
        :param description: Описание способности
        :param icon: Иконка способности
        """
        super().__init__(name, type, description, icon)
    
    # ==================== Использование способности ====================
    def can_use(self, character: 'Character', targets: Optional[List['Character']] = None) -> bool:
        """
        Пассивные способности всегда доступны если имеют уровень > 0.
        Используются автоматически системой.
        """
        return self.is_available()
    
    def use(self, character: 'Character', targets: List['Character'], **kwargs: Any) -> AbilityResult:
        """
        Пассивные способности не могут быть использованы напрямую.
        """
        result = AbilityResult()
        result.success = False
        result.reason = "Пассивные способности нельзя использовать напрямую"
        result.ability_type = self.__class__.__name__.lower()
        result.character = character
        result.targets = targets
        return result
    
    # ==================== Абстрактный метод ====================
    def apply_effect(self, character: 'Character', **kwargs: Any) -> Any:
        """
        Применяет эффект пассивной способности.
        Переопределяется в подклассах.
        """
        raise NotImplementedError("Метод apply_effect должен быть реализован в подклассе")