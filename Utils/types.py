"""Определение общих протоколов и типов для проекта."""

from typing import Protocol, List, Any, Dict, Optional, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Characters.character import Character

# Предполагая, что сообщения логгера могут быть строками или специальными кортежами/объектами
# Как видно из battle_logger.create_log_message и использования в round_logic.log_result
LoggerMessageType = Union[str, Any] 

class IResult(Protocol):
    """
    Протокол для результата действия (способности, эффекта статуса и т.д.).
    Определяет минимальный интерфейс, необходимый для обработки результатов в боевой системе.
    """
    success: bool
    messages: List[LoggerMessageType]
    details: Dict[str, Any]

    # Хотя details определен как атрибут, наличие методов доступа к нему
    # может быть полезным для реализации. Однако для протокола достаточно атрибута.
    # Если бы требовался метод, он был бы определен здесь.
    # Например: def get_detail(self, key: str) -> Any: ...

# Альтернативно, если details не обязателен на старте, можно сделать его опциональным
# или опустить, добавив позже. Но судя по структуре AbilityResult, он там есть.

class IAbilityResult(IResult, Protocol):
    """
    Протокол для результата применения активной способности.
    Расширяет IResult специфичными полями для способностей.
    """
    # Базовые поля способности
    ability_type: str
    character: Optional['Character']
    targets: List['Character']
    
    # Статистика применения
    damage_dealt: int
    heal_amount: int
    energy_restored: int
    is_critical: bool
    total_damage: int
    total_heal: int
    
    # Дополнительная информация
    reason: str  # Причина неудачи
    
    # Методы могут быть добавлены при необходимости
    # def add_target(self, target: 'Character') -> None: ...

class IEffectResult(IResult, Protocol):
    """
    Протокол для результата применения эффекта статуса.
    Расширяет IResult специфичными полями для эффектов.
    """
    # Идентификация эффекта
    effect: str
    
    # Статистика эффекта
    total_damage: int
    
    # Дополнительные эффекты (например, шанс наложить другой эффект)
    additional_effects: List[Dict[str, Any]]
    
    # Методы могут быть добавлены при необходимости
    # def add_additional_effect(self, effect_data: Dict[str, Any]) -> None: ...

class IApplyEffectResult(IResult, Protocol):
    """
    Протокол для результата наложения эффекта статуса.
    Расширяет IResult специфичными полями для эффектов.
    """
    # Идентификация эффекта
    effect: str
    message: list[tuple[str, int]]

class IPassiveAbilityResult(IResult, Protocol):
    """
    Протокол для результата срабатывания пассивной способности.
    Расширяет IResult специфичными полями для пассивных способностей.
    """
    # Идентификация способности
    ability_name: str
    
    # Условие срабатывания
    trigger_condition: str
    
    # Методы могут быть добавлены при необходимости

# Протоколы для других потенциальных типов можно добавить сюда позже