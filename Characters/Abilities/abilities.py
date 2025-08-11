# Characters/Abilities/ability_base.py - Базовые классы способностей

import os
import importlib.util
from Config.game_config import ABILITIES_PATH

class AbilityResult:
    """Простой класс для возврата результатов из способностей."""
    
    def __init__(self):
        # Универсальные свойства для всех способностей
        self.success = True
        self.ability_type = ""
        self.character = ""
        self.targets = []
        self.messages = []
        self.damage_dealt = 0
        self.heal_amount = 0
        self.energy_restored = 0
        self.is_critical = False
        self.total_damage = 0
        self.total_heal = 0
        self.reason = ""  # Причина неудачи
        self.details = {}  # Для дополнительной информации

class Ability:
    """Базовый класс для способностей"""
    
    def __init__(self, name, type=0, damage_scale=0.0, cooldown=1, energy_cost=0, description="", icon="", is_mass=False):
        """
        Инициализация способности.
        
        :param name: Название способности
        :param type: Тип способности - 0 - атака, 1 - лечение, 2 - отдых и т.д.
        :param damage_scale: Процент урона от атаки владельца
        :param cooldown: Количество раундов до восстановления способности
        :param energy_cost: Стоимость энергии для использования
        :param description: Описание способности
        :param icon: Иконка способности
        :param is_mass: Массовая способность
        """
        self.name = name
        self.type = type # Тип способности - 0 - атака, 1 - лечение, 2 - отдых и т.д.
        self.is_mass = is_mass
        self.damage_scale = damage_scale
        self.cooldown = cooldown # чтобы была задержка 1 ход - указываем 2
        self.current_cooldown = 0
        self.energy_cost = energy_cost
        self.description = description
        self.icon = icon
        
    
    def can_use(self, character, targets=None):
        """
        Проверяет, может ли персонаж использовать способность.
        
        :param character: Персонаж, который хочет использовать способность
        :param targets: Цели (опционально)
        :return: True, если можно использовать, иначе False
        """
        # Проверяем кулдаун
        if self.current_cooldown > 0:
            return False
            
        # Проверяем энергию
        if hasattr(character, 'energy') and character.energy < self.energy_cost:
            return False
            
        # Проверяем специфические условия для способности
        return self.check_specific_conditions(character, targets)
    
    def check_specific_conditions(self, character, targets):
        """
        Проверяет специфические условия для использования способности.
        Переопределяется в подклассах.
        """
        return True
    
    def use(self, character, targets, **kwargs):
        """
        Использует способность.
        
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
    
    def execute(self, character, targets, **kwargs):
        """
        Выполняет логику способности. Переопределяется в подклассах.
        """
        raise NotImplementedError("Метод execute должен быть реализован в подклассе")
    
    def update_cooldown(self):
        """Обновляет кулдаун способности в конце раунда."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    
    def on_use(self, character, targets, result):
        """
        Вызывается после использования способности.
        Можно использовать для обновления статистики и т.д.
        """
        pass
    
    def get_info(self):
        """Возвращает информацию о способности."""
        return {
            'name': self.name,
            'type': self.type,
            'damage_scale': self.damage_scale,
            'cooldown': self.cooldown,
            'current_cooldown': self.current_cooldown,
            'energy_cost': self.energy_cost,
            'description': self.description
        }

# === Singleton AbilityLoader ===

class AbilityLoader:
    _instance = None
    _initialized = False
    
    def __new__(cls, root_folder=None):
        if cls._instance is None:
            cls._instance = super(AbilityLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, root_folder=None):
        # Инициализируем только один раз
        if not self._initialized:
            self.root_folder = root_folder or 'Characters/Abilities'
            self._class_map = {}  # Теперь храним классы, а не пути
            self._scan_abilities()
            self.__class__._initialized = True
    
    def _scan_abilities(self):
        """Сканирует все файлы способностей и сохраняет классы этих способностей"""
        # Формируем путь к папке с способностями
        base_path = os.path.normpath(ABILITIES_PATH)
        
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Root folder '{base_path}' not found")
        
        for dirpath, dirnames, filenames in os.walk(base_path):
            for filename in filenames:
                # Исключаем служебные файлы
                if (filename.endswith('.py') and 
                    filename not in ['__init__.py', 'ability_base.py']):
                    # Получаем имя класса (имя файла с большой буквы)
                    class_name = filename[:-3].capitalize()
                    full_path = os.path.join(dirpath, filename)
                    
                    # Загружаем класс сразу при сканировании
                    try:
                        ability_class = self._load_class_from_file(class_name, full_path)
                        self._class_map[class_name] = ability_class
                    except Exception as e:
                        print(f"Warning: Failed to load ability class '{class_name}' from '{full_path}': {str(e)}")
    
    def _load_class_from_file(self, class_name, file_path):
        """Загружает класс способности из файла"""
        module_name = f"ability_{class_name.lower()}"
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, class_name):
            raise AttributeError(f"Class '{class_name}' not found in module '{file_path}'")
            
        return getattr(module, class_name)
    
    def get_class(self, class_name):
        """Получает класс способности по имени"""
        if class_name not in self._class_map:
            available_abilities = list(self._class_map.keys())
            raise FileNotFoundError(f"Ability class '{class_name}' not found. Available abilities: {available_abilities}")
        
        return self._class_map[class_name]
    
    def get_available_abilities(self):
        """Возвращает список доступных имен способностей"""
        return list(self._class_map.keys())
    
    @classmethod
    def get_instance(cls):
        """Получить экземпляр singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# === Система управления способностями персонажа ===

class AbilityManager:
    """Менеджер способностей персонажа"""
    
    def __init__(self):
        # Один словарь, хранящий отдельные экземпляры способностей для каждого персонажа
        self.abilities = {}  # {name: Ability instance}
        # Получаем singleton instance AbilityLoader
        self.ability_loader = AbilityLoader.get_instance()
        # Добавляем базовые способности по умолчанию
        self.add_ability_by_name('attack')
        self.add_ability_by_name('rest')
    
    def add_ability(self, name, ability_instance):
        """Добавляет способность персонажу."""
        try:
            # Создаем копию способности для каждого персонажа
            if hasattr(ability_instance, '__class__'):
                new_ability = ability_instance.__class__()
                # Копируем все атрибуты
                for attr, value in ability_instance.__dict__.items():
                    setattr(new_ability, attr, value)
                self.abilities[name] = new_ability
            else:
                self.abilities[name] = ability_instance
            return True
        except Exception as e:
            print(f"Error adding ability '{name}': {e}")
            return False
    
    def remove_ability(self, name):
        """Удаляет способность по имени."""
        if name in self.abilities:
            del self.abilities[name]
            return True
        return False
    
    def clear_abilities(self):
        """Удаляет все способности."""
        self.abilities.clear()
    
    def get_ability(self, name):
        """Получает способность по имени."""
        return self.abilities.get(name)
    
    def get_all_abilities(self):
        """Возвращает все способности персонажа."""
        return list(self.abilities.values())
    
    def get_all_ability_names(self):
        """Возвращает имена всех способностей персонажа."""
        return list(self.abilities.keys())
    
    def get_available_abilities(self, character):
        """
        Возвращает список ссылок на способности, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список доступных способностей (Ability instances)
        """
        return [ability for ability in self.abilities.values() if ability.can_use(character)]
    
    def get_available_ability_names(self, character):
        """
        Возвращает список имен способностей, которые сейчас доступны.
        :param character: Персонаж для проверки условий
        :return: Список имен доступных способностей
        """
        return [name for name, ability in self.abilities.items() if ability.can_use(character)]
    
    def use_ability(self, ability, character, targets, **kwargs):
        """Использует способность напрямую."""
        if ability and ability.can_use(character, targets):
            return ability.use(character, targets, **kwargs)
        result = AbilityResult()
        result.success = False
        result.reason = "Способность недоступна"
        return result
    
    def update_cooldowns(self):
        """Обновляет кулдауны всех способностей в конце раунда."""
        for ability in self.abilities.values():
            ability.update_cooldown()

    def reset_all_cooldowns(self):
        """Сбрасывает все кулдауны способностей до 0."""
        for ability in self.abilities.values():
            ability.current_cooldown = 0
    
    def create_ability_by_name(self, ability_name):
        """
        Создает экземпляр способности по имени через AbilityLoader.
        
        :param ability_name: Имя способности (должно совпадать с именем класса)
        :return: Экземпляр способности или None, если не найдена
        """
        try:
            # Преобразуем имя способности в имя класса (первая буква заглавная)
            class_name = ability_name.capitalize()
            ability_class = self.ability_loader.get_class(class_name)
            return ability_class()
        except (FileNotFoundError, ImportError, AttributeError) as e:
            print(f"Ошибка при создании способности '{ability_name}': {e}")
            return None
    
    def add_ability_by_name(self, ability_name):
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

# Удобная функция для получения AbilityLoader
def get_ability_loader():
    """Получить singleton экземпляр AbilityLoader"""
    return AbilityLoader.get_instance()