# Characters/Status_effects/status_manager.py
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from Characters.Status_effects.status_effect import StackableStatusEffect
from Utils.types import IApplyEffectResult

if TYPE_CHECKING:
    from Characters.character import Character
    from Characters.Status_effects.status_effect import StatusEffect

# Глобальный реестр эффектов
_EFFECT_REGISTRY = {}

def register_effect(effect_class):
    """Регистрирует класс эффекта в глобальном реестре"""
    _EFFECT_REGISTRY[effect_class.__name__] = effect_class
    return effect_class

def get_effect_class_by_name(effect_class_name: str) -> Optional[type]:
    """Получает класс эффекта по имени класса из реестра"""
    return _EFFECT_REGISTRY.get(effect_class_name)

class StatusEffectManager:
    """Менеджер статус-эффектов для персонажа."""
    
    def __init__(self, character: 'Character'):
        self.character = character
        self.active_effects: List = []  # List[StatusEffect] - тип будет проверен позже
        
    def _get_status_effect_type(self):
        """Ленивый импорт класса StatusEffect"""
        if not hasattr(self, '_status_effect_class'):
            from Characters.Status_effects.status_effect import StatusEffect
            self._status_effect_class = StatusEffect
        return self._status_effect_class
        
    def add_effect(self, effect, target) -> IApplyEffectResult:  # effect: StatusEffect
        """
        Добавляет эффект персонажу.
        
        :param effect: Экземпляр статус-эффекта
        """
        # Проверяем, есть ли уже такой эффект
        existing_effect = self.get_effect(effect)
 
        if existing_effect:
            # Если эффект уже есть, продляем его действие
            existing_effect.extend_duration()
        else:
            # Добавляем новый эффект
            self.active_effects.append(effect)
            existing_effect = effect

        if isinstance(effect, StackableStatusEffect):
            existing_effect.add_stack()

        return effect.apply_effect(target)

    
    def remove_effect(self, effect_name: str) -> bool:
        """
        Удаляет эффект по имени.
        
        :param effect_name: Имя эффекта для удаления
        :return: True если эффект удален, False если не найден
        """
        for i, effect in enumerate(self.active_effects):
            if effect.name == effect_name:
                effect.remove_effect(self.character)
                del self.active_effects[i]
                return True
        return False
    
    def get_effect(self, effect: 'StatusEffect') -> Optional['StatusEffect']:
        """
        Получает эффект.
        :return: Экземпляр эффекта или None если не найден
        """
        for active_effect in self.active_effects:
            if active_effect.__class__ == effect.__class__:
                return effect
        return None
    
    def update_effects(self) -> List[Dict[str, Any]]:
        """
        Обновляет все активные эффекты в начале/конце раунда.
        
        :return: Список результатов обновления эффектов
        """
        results = []
        expired_effects = []
        
        # Обновляем все эффекты
        for effect in self.active_effects:
            result = effect.tick(self.character)
            results.append(result)
            
            # Проверяем, истек ли эффект
            if effect.is_expired():
                expired_effects.append(effect)
        
        # Удаляем истекшие эффекты
        for effect in expired_effects:
            if effect in self.active_effects:
                self.active_effects.remove(effect)
            
        return results
    
    def has_effect(self, effect_name: str) -> bool:
        """
        Проверяет, есть ли у персонажа определенный эффект.
        
        :param effect_name: Имя эффекта
        :return: True если эффект есть, False если нет
        """
        return any(effect.name == effect_name for effect in self.active_effects)
    
    def get_all_effects(self) -> List:  # List[StatusEffect]
        """
        Возвращает список всех активных эффектов.
        
        :return: Список активных эффектов
        """
        return self.active_effects.copy()
    
    def clear_all_effects(self) -> List[Dict[str, Any]]:
        """
        Удаляет все активные эффекты.
        
        :return: Список результатов удаления эффектов
        """
        results = []
        for effect in self.active_effects.copy():
            result = effect.remove_effect(self.character)
            results.append(result)
        self.active_effects.clear()
        return results
    
    def get_effect_class_by_name(self, effect_class_name: str) -> Optional[type]:
        """
        Возвращает класс эффекта по имени класса.
        
        :param effect_class_name: Имя класса эффекта
        :return: Класс эффекта или None если не найден
        """
        return get_effect_class_by_name(effect_class_name)