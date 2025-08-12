# Characters/Status_effects/status_manager.py
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import importlib

if TYPE_CHECKING:
    from Characters.character import Character
    from Characters.Status_effects.status_effect import StatusEffect

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
        
    def add_effect(self, effect) -> Dict[str, Any]:  # effect: StatusEffect
        """
        Добавляет эффект персонажу.
        
        :param effect: Экземпляр статус-эффекта
        :return: Результат применения эффекта
        """
        StatusEffect = self._get_status_effect_type()
        
        # Проверяем, есть ли уже такой эффект
        existing_effect = self.get_effect(effect.name)
        
        if existing_effect:
            # Если эффект уже есть, продляем его действие
            existing_effect.extend_duration(effect.duration)
            return {"message": f"Эффект {effect.name} продлен"}
        else:
            # Добавляем новый эффект
            self.active_effects.append(effect)
            return effect.tick(self.character)
    
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
    
    def get_effect(self, effect_name: str):  # -> Optional[StatusEffect]
        """
        Получает эффект по имени.
        
        :param effect_name: Имя эффекта
        :return: Экземпляр эффекта или None если не найден
        """
        for effect in self.active_effects:
            if effect.name == effect_name:
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