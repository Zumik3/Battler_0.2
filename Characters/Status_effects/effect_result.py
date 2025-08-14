# Characters/Status_effects/effect_result.py
from typing import List, Any, Dict
from Utils.types import LoggerMessageType

class EffectResult:
    """Результат применения эффекта статуса."""
    def __init__(self) -> None:
        self.success: bool = True
        self.messages: List[LoggerMessageType] = []
        self.details: Dict[str, Any] = {}

    def add_message(self, message: LoggerMessageType) -> None:
        """Добавляет сообщение в результат."""
        self.messages.append(message)
        
    def set_success(self, success: bool) -> None:
        """Устанавливает статус успеха."""
        self.success = success
        
    def add_detail(self, key: str, value: Any) -> None:
        """Добавляет деталь в результат."""
        self.details[key] = value

class ApplyEffectResult:
    def __init__(self, effect: str) -> None:
        self.effect: str = effect
        self.message: LoggerMessageType = None

    def add_message(self, message: LoggerMessageType) -> None:
        """Добавляет сообщение в результат."""
        self.message = message