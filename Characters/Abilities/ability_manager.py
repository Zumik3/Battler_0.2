# Characters/Abilities/ability_manager.py
"""Система управления способностями персонажа"""

import os
import re
import importlib.util
from typing import Dict, List, Any, Optional, Union

from Config.game_config import ABILITIES_PATH
from Characters.Abilities.ability import ActiveAbility, PassiveAbility, AbilityResult


# ==================== Загрузчик способностей ====================
class AbilityLoader:
    """Singleton загрузчик способностей"""
    _instance: Optional['AbilityLoader'] = None
    _initialized: bool = False
    
    # ==================== Singleton ====================
    def __new__(cls, root_folder: Optional[str] = None) -> 'AbilityLoader':
        if cls._instance is None:
            cls._instance = super(AbilityLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, root_folder: Optional[str] = None) -> None:
        """Инициализация загрузчика способностей"""
        if not self._initialized:
            self.root_folder: str = root_folder or 'Characters/Abilities'
            self._class_map: Dict[str, type] = {}
            self._scan_abilities()
            self.__class__._initialized = True
    
    # ==================== Загрузка способностей ====================
    def _scan_abilities(self) -> None:
        """Сканирует все файлы способностей и сохраняет классы этих способностей"""
        base_path = os.path.normpath(ABILITIES_PATH)
        
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Root folder '{base_path}' not found")
        
        for dirpath, dirnames, filenames in os.walk(base_path):
            # Пропускаем корневую директорию
            if dirpath == base_path:
                continue

            for filename in filenames:
                # Исключаем служебные файлы
                if (filename.endswith('.py') and 
                    filename not in ['__init__.py', 'ability_base.py', 'abilities.py']):
                    full_path = os.path.join(dirpath, filename)
                    
                    # Загружаем класс сразу при сканировании
                    try:
                        class_name = self._get_class_name_from_file(full_path)
                        if class_name:
                            ability_class = self._load_class_from_file(full_path, class_name)
                            self._class_map[class_name] = ability_class
                    except Exception as e:
                        print(f"Warning: Failed to load ability class from '{full_path}': {str(e)}")
    
    def _get_class_name_from_file(self, file_path: str) -> Optional[str]:
        """Получает имя первого класса из файла Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем первую строку с определением класса
            match = re.search(r'^class\s+(\w+)', content, re.MULTILINE)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None

    def _load_class_from_file(self, file_path: str, class_name: str) -> type:
        """Загружает класс из файла"""
        spec = importlib.util.spec_from_file_location(class_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, class_name):
            raise AttributeError(f"Class '{class_name}' not found in module '{file_path}'")
            
        return getattr(module, class_name)
    
    # ==================== Публичный API ====================
    def get_class(self, class_name: str) -> type:
        """Получает класс способности по имени"""
        if class_name not in self._class_map:
            available_abilities = list(self._class_map.keys())
            raise FileNotFoundError(f"Ability class '{class_name}' not found. Available abilities: {available_abilities}")
        
        return self._class_map[class_name]
    
    def get_available_abilities(self) -> List[str]:
        """Возвращает список доступных имен способностей"""
        return list(self._class_map.keys())
    
    # ==================== Singleton management ====================
    @classmethod
    def get_instance(cls) -> 'AbilityLoader':
        """Получить экземпляр singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_ability_loader() -> AbilityLoader:
    """Удобная функция для получения AbilityLoader"""
    return AbilityLoader.get_instance()


# ==================== Менеджер способностей ====================
class AbilityManager:
    """Менеджер способностей персонажа"""
    
    def __init__(self) -> None:
        """Инициализация менеджера способностей"""
        # Разделяем активные и пассивные способности
        self.active_abilities: Dict[str, ActiveAbility] = {}
        self.passive_abilities: Dict[str, PassiveAbility] = {}
        
        # Получаем singleton instance AbilityLoader
        self.ability_loader: AbilityLoader = AbilityLoader.get_instance()
        
        # Добавляем базовые способности по умолчанию
        self.add_ability_by_name('Attack')
        self.add_ability_by_name('Rest')
    
    # ==================== Добавление и удаление способностей ====================
    def add_ability(self, name: str, ability_instance: Union[ActiveAbility, PassiveAbility]) -> bool:
        """Добавляет способность персонажу."""
        try:
            # Создаем копию способности для каждого персонажа
            if hasattr(ability_instance, '__class__'):
                new_ability = ability_instance.__class__()
                # Копируем все атрибуты
                for attr, value in ability_instance.__dict__.items():
                    setattr(new_ability, attr, value)
            else:
                new_ability = ability_instance
                
            # Добавляем в соответствующий словарь
            if isinstance(new_ability, PassiveAbility):
                self.passive_abilities[name] = new_ability
            elif isinstance(new_ability, ActiveAbility):
                self.active_abilities[name] = new_ability
            return True
        except Exception as e:
            print(f"Error adding ability '{name}': {e}")
            return False
    
    def add_ability_by_name(self, ability_name: str) -> bool:
        """Добавляет способность по имени."""
        ability_instance = self.create_ability_by_name(ability_name)
        if ability_instance:
            name_key = ability_name.lower()
            return self.add_ability(name_key, ability_instance)
        return False
    
    def remove_ability(self, name: str) -> bool:
        """Удаляет способность по имени."""
        if name in self.active_abilities:
            del self.active_abilities[name]
            return True
        elif name in self.passive_abilities:
            del self.passive_abilities[name]
            return True
        return False
    
    def clear_abilities(self) -> None:
        """Удаляет все способности."""
        self.active_abilities.clear()
        self.passive_abilities.clear()
    
    # ==================== Получение способностей ====================
    def get_ability(self, name: str) -> Optional[Union[ActiveAbility, PassiveAbility]]:
        """Получает способность по имени."""
        if name in self.active_abilities:
            return self.active_abilities[name]
        elif name in self.passive_abilities:
            return self.passive_abilities[name]
        return None
    
    def get_active_ability(self, name: str) -> Optional[ActiveAbility]:
        """Получает активную способность по имени."""
        return self.active_abilities.get(name)
    
    def get_passive_ability(self, name: str) -> Optional[PassiveAbility]:
        """Получает пассивную способность по имени."""
        return self.passive_abilities.get(name)
    
    def get_all_abilities(self) -> List[Union[ActiveAbility, PassiveAbility]]:
        """Возвращает все способности персонажа."""
        return list(self.active_abilities.values()) + list(self.passive_abilities.values())
    
    def get_active_abilities(self) -> List[ActiveAbility]:
        """Возвращает все активные способности персонажа."""
        return list(self.active_abilities.values())
    
    def get_passive_abilities(self) -> List[PassiveAbility]:
        """Возвращает все пассивные способности персонажа."""
        return list(self.passive_abilities.values())
    
    def get_all_ability_names(self) -> List[str]:
        """Возвращает имена всех способностей персонажа."""
        return list(self.active_abilities.keys()) + list(self.passive_abilities.keys())
    
    def get_active_ability_names(self) -> List[str]:
        """Возвращает имена всех активных способностей персонажа."""
        return list(self.active_abilities.keys())
    
    def get_passive_ability_names(self) -> List[str]:
        """Возвращает имена всех пассивных способностей персонажа."""
        return list(self.passive_abilities.keys())
    
    # ==================== Доступные способности ====================
    def get_available_abilities(self, character: Any) -> List[ActiveAbility]:
        """Возвращает список доступных активных способностей."""
        return [ability for ability in self.active_abilities.values() if ability.can_use(character)]
    
    def get_available_ability_names(self, character: Any) -> List[str]:
        """Возвращает имена доступных активных способностей."""
        return [name for name, ability in self.active_abilities.items() if ability.can_use(character)]
    
    def get_available_passive_abilities(self, character: Any) -> List[PassiveAbility]:
        """Возвращает список доступных пассивных способностей."""
        return [ability for ability in self.passive_abilities.values() if ability.is_available()]
    
    # ==================== Использование способностей ====================
    def use_ability(self, ability: Optional[ActiveAbility], character: Any, 
                   targets: List[Any], **kwargs: Any) -> AbilityResult:
        """Использует активную способность напрямую."""
        if ability and isinstance(ability, ActiveAbility) and ability.can_use(character, targets):
            return ability.use(character, targets, **kwargs)
        result = AbilityResult()
        result.success = False
        result.reason = "Способность недоступна или не является активной"
        return result
    
    # ==================== Управление кулдаунами ====================
    def update_cooldowns(self) -> None:
        """Обновляет кулдауны всех активных способностей в конце раунда."""
        for ability in self.active_abilities.values():
            if hasattr(ability, 'update_cooldown'):
                ability.update_cooldown()

    def reset_all_cooldowns(self) -> None:
        """Сбрасывает все кулдауны активных способностей до 0."""
        for ability in self.active_abilities.values():
            if hasattr(ability, 'current_cooldown'):
                ability.current_cooldown = 0
    
    # ==================== Создание способностей ====================
    def create_ability_by_name(self, ability_name: str) -> Optional[Union[ActiveAbility, PassiveAbility]]:
        """Создает экземпляр способности по имени через AbilityLoader."""
        try:
            ability_class = self.ability_loader.get_class(ability_name)
            return ability_class()
        except (FileNotFoundError, ImportError, AttributeError) as e:
            print(f"Ошибка при создании способности '{ability_name}': {e}")
            return None
    
    # ==================== Управление уровнями ====================
    def level_up_ability(self, ability_name: str) -> int:
        """Повышает уровень способности на 1."""
        ability = self.get_ability(ability_name)
        if ability:
            return ability.level_up()
        return -1
    
    def set_ability_level(self, ability_name: str, level: int) -> int:
        """Устанавливает уровень способности."""
        ability = self.get_ability(ability_name)
        if ability:
            return ability.set_level(level)
        return -1