# Characters/Abilities/ability_base.py - Базовые классы способностей

import os
import re
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from Config.game_config import ABILITIES_PATH


class AbilityResult:
    """Простой класс для возврата результатов из способностей."""
    
    def __init__(self) -> None:
        # Универсальные свойства для всех способностей
        self.success: bool = True
        self.ability_type: str = ""
        self.character: str = ""
        self.targets: List[str] = []
        self.messages: List[Any] = []
        self.damage_dealt: int = 0
        self.heal_amount: int = 0
        self.energy_restored: int = 0
        self.is_critical: bool = False
        self.total_damage: int = 0
        self.total_heal: int = 0
        self.reason: str = ""  # Причина неудачи
        self.details: Dict[str, Any] = {}  # Для дополнительной информации

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
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает информацию о способности."""
        return {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'level': self.level
        }
    
    @abstractmethod
    def can_use(self, character: Any, targets: Optional[List[Any]] = None) -> bool:
        """Абстрактный метод проверки возможности использования"""
        pass
    
    @abstractmethod
    def use(self, character: Any, targets: List[Any], **kwargs: Any) -> AbilityResult:
        """Абстрактный метод использования способности"""
        pass

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
    
    def can_use(self, character: Any, targets: Optional[List[Any]] = None) -> bool:
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
    
    def check_specific_conditions(self, character: Any, targets: List[Any]) -> bool:
        """
        Проверяет специфические условия для использования способности.
        Переопределяется в подклассах.
        """
        return True
    
    def use(self, character: Any, targets: List[Any], **kwargs: Any) -> AbilityResult:
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
            result.character = character.name if hasattr(character, 'name') else str(character)
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
    
    def execute(self, character: Any, targets: List[Any], **kwargs: Any) -> AbilityResult:
        """
        Выполняет логику способности. Переопределяется в подклассах.
        """
        raise NotImplementedError("Метод execute должен быть реализован в подклассе")
    
    def update_cooldown(self) -> None:
        """Обновляет кулдаун способности в конце раунда."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def on_use(self, character: Any, targets: List[Any], result: AbilityResult) -> None:
        """
        Вызывается после использования способности.
        Можно использовать для обновления статистики и т.д.
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает информацию о активной способности."""
        info = super().get_info()
        info.update({
            'damage_scale': self.damage_scale,
            'energy_cost': self.energy_cost,
            'is_mass': self.is_mass,
            'cooldown': self.cooldown,
            'current_cooldown': self.current_cooldown
        })
        return info

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
    
    def can_use(self, character: Any, targets: Optional[List[Any]] = None) -> bool:
        """
        Пассивные способности всегда доступны если имеют уровень > 0.
        Используются автоматически системой.
        """
        return self.is_available()
    
    def use(self, character: Any, targets: List[Any], **kwargs: Any) -> AbilityResult:
        """
        Пассивные способности не могут быть использованы напрямую.
        """
        result = AbilityResult()
        result.success = False
        result.reason = "Пассивные способности нельзя использовать напрямую"
        result.ability_type = self.__class__.__name__.lower()
        result.character = character.name if hasattr(character, 'name') else str(character)
        return result
    
    def apply_effect(self, character: Any, **kwargs: Any) -> Any:
        """
        Применяет эффект пассивной способности.
        Переопределяется в подклассах.
        """
        raise NotImplementedError("Метод apply_effect должен быть реализован в подклассе")

# === Singleton AbilityLoader ===

class AbilityLoader:
    _instance: Optional['AbilityLoader'] = None
    _initialized: bool = False
    
    def __new__(cls, root_folder: Optional[str] = None) -> 'AbilityLoader':
        if cls._instance is None:
            cls._instance = super(AbilityLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, root_folder: Optional[str] = None) -> None:
        # Инициализируем только один раз
        if not self._initialized:
            self.root_folder: str = root_folder or 'Characters/Abilities'
            self._class_map: Dict[str, type] = {}  # Теперь храним классы, а не пути
            self._scan_abilities()
            self.__class__._initialized = True
    
    def _scan_abilities(self) -> None:
        """Сканирует все файлы способностей и сохраняет классы этих способностей"""
        # Формируем путь к папке с способностями
        base_path = os.path.normpath(ABILITIES_PATH)
        
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Root folder '{base_path}' not found")
        
        for dirpath, dirnames, filenames in os.walk(base_path):
            # Пропускаем корневую директорию (где лежит abilities.py)
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
            
            # Ищем первую строку с определением класса (только если class в начале строки)
            match = re.search(r'^class\s+(\w+)', content, re.MULTILINE)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None

    def _load_class_from_file(self, file_path: str, class_name: str) -> type:

        spec = importlib.util.spec_from_file_location(class_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, class_name):
            raise AttributeError(f"Class '{class_name}' not found in module '{file_path}'")
            
        return getattr(module, class_name)
    
    def get_class(self, class_name: str) -> type:
        """Получает класс способности по имени"""
        if class_name not in self._class_map:
            available_abilities = list(self._class_map.keys())
            raise FileNotFoundError(f"Ability class '{class_name}' not found. Available abilities: {available_abilities}")
        
        return self._class_map[class_name]
    
    def get_available_abilities(self) -> List[str]:
        """Возвращает список доступных имен способностей"""
        return list(self._class_map.keys())
    
    @classmethod
    def get_instance(cls) -> 'AbilityLoader':
        """Получить экземпляр singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# === Система управления способностями персонажа ===

class AbilityManager:
    """Менеджер способностей персонажа"""
    
    def __init__(self) -> None:
        # Разделяем активные и пассивные способности
        self.active_abilities: Dict[str, ActiveAbility] = {}  # {name: ActiveAbility instance}
        self.passive_abilities: Dict[str, PassiveAbility] = {}  # {name: PassiveAbility instance}
        # Получаем singleton instance AbilityLoader
        self.ability_loader: AbilityLoader = AbilityLoader.get_instance()
        # Добавляем базовые способности по умолчанию
        self.add_ability_by_name('Attack')
        self.add_ability_by_name('Rest')
    
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
    
    def get_available_abilities(self, character: Any) -> List[ActiveAbility]:
        """
        Возвращает список ссылок на активные способности, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список доступных способностей (ActiveAbility instances)
        """
        return [ability for ability in self.active_abilities.values() if ability.can_use(character)]
    
    def get_available_ability_names(self, character: Any) -> List[str]:
        """
        Возвращает список имен активных способностей, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список имен доступных способностей
        """
        return [name for name, ability in self.active_abilities.items() if ability.can_use(character)]
    
    def get_available_passive_abilities(self, character: Any) -> List[PassiveAbility]:
        """
        Возвращает список ссылок на пассивные способности, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список доступных пассивных способностей (PassiveAbility instances)
        """
        return [ability for ability in self.passive_abilities.values() if ability.is_available()]
    
    def use_ability(self, ability: Optional[ActiveAbility], character: Any, 
                   targets: List[Any], **kwargs: Any) -> AbilityResult:
        """Использует активную способность напрямую."""
        if ability and isinstance(ability, ActiveAbility) and ability.can_use(character, targets):
            return ability.use(character, targets, **kwargs)
        result = AbilityResult()
        result.success = False
        result.reason = "Способность недоступна или не является активной"
        return result
    
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
    
    def create_ability_by_name(self, ability_name: str) -> Optional[Union[ActiveAbility, PassiveAbility]]:
        """
        Создает экземпляр способности по имени через AbilityLoader.
        
        :param ability_name: Имя способности (должно совпадать с именем класса)
        :return: Экземпляр способности или None, если не найдена
        """
        try:
            ability_class = self.ability_loader.get_class(ability_name)
            return ability_class()
        except (FileNotFoundError, ImportError, AttributeError) as e:
            print(f"Ошибка при создании способности '{ability_name}': {e}")
            return None
    
    def add_ability_by_name(self, ability_name: str) -> bool:
        """
        Добавляет способность по имени.
        
        :param ability_name: Имя способности для добавления
        :return: True, если успешно добавлена, False в случае ошибки
        """
        ability_instance = self.create_ability_by_name(ability_name)
        if ability_instance:
            # Используем имя файла (в нижнем регистре) как ключ
            name_key = ability_name.lower()
            return self.add_ability(name_key, ability_instance)
        return False
    
    def level_up_ability(self, ability_name: str) -> int:
        """
        Повышает уровень способности на 1.
        
        :param ability_name: Имя способности
        :return: Новый уровень способности или -1 если способность не найдена
        """
        ability = self.get_ability(ability_name)
        if ability:
            return ability.level_up()
        return -1
    
    def set_ability_level(self, ability_name: str, level: int) -> int:
        """
        Устанавливает уровень способности.
        
        :param ability_name: Имя способности
        :param level: Новый уровень
        :return: Новый уровень способности или -1 если способность не найдена
        """
        ability = self.get_ability(ability_name)
        if ability:
            return ability.set_level(level)
        return -1

# Удобная функция для получения AbilityLoader
def get_ability_loader() -> AbilityLoader:
    """Получить singleton экземпляр AbilityLoader"""
    return AbilityLoader.get_instance()