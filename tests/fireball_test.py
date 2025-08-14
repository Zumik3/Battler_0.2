# tests/fireball_test.py

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Добавляем корневую директорию проекта в путь для корректных импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Characters.Abilities.Attack_abilities.fireball import Fireball
from Characters.Abilities.ability import AbilityResult
from Characters.character import Character

class TestFireball(unittest.TestCase):
    """Тесты для способности Огненный шар"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.fireball = Fireball()
        
        # Создаем мок для stats
        mock_stats = Mock()
        mock_stats.intelligence = 100
        
        # Создаем мок персонажа
        self.character = Mock(spec=Character)
        self.character.name = "Тестовый Маг"
        self.character.stats = mock_stats
        self.character.is_alive.return_value = True
        self.character.energy = 10  # Добавляем энергию для тестов
        
        # Создаем мок цель
        self.target = Mock(spec=Character)
        self.target.name = "Тестовый Враг"
        self.target.is_alive.return_value = True
        self.target.take_damage = Mock()
        self.target.status_manager = Mock()  # Добавляем status_manager
        self.target.status_manager.add_effect = Mock(return_value=Mock())  # Мок для add_effect
        
        # Создаем список целей
        self.targets = [self.target]
    
    def test_fireball_initialization(self):
        """Тест инициализации огненного шара"""
        self.assertEqual(self.fireball.name, "Огненный шар")
        self.assertEqual(self.fireball.damage_scale, 0.8)
        self.assertEqual(self.fireball.cooldown, 1)
        self.assertEqual(self.fireball.energy_cost, 5)
        self.assertEqual(self.fireball.icon, "🔥")
        
        # Проверяем, что эффект BurnEffect добавлен
        self.fireball.level = 1  # Устанавливаем уровень для проверки
        effects = self.fireball.get_effects_info()
        self.assertTrue(len(effects) > 0)
        # Проверяем, что есть эффект с именем, содержащим "Burn"
        effect_names = [effect.__name__ for effect in effects]
        self.assertTrue(any("Burn" in name for name in effect_names))
    
    def test_execute_no_targets(self):
        """Тест выполнения без целей"""
        result = self.fireball.execute(self.character, [])
        self.assertIsInstance(result, AbilityResult)
        self.assertFalse(result.success)
        self.assertEqual(result.reason, 'Нет цели для атаки')
    
    def test_execute_dead_target(self):
        """Тест выполнения с мертвой целью"""
        self.target.is_alive.return_value = False
        result = self.fireball.execute(self.character, [self.target])
        self.assertIsInstance(result, AbilityResult)
        self.assertFalse(result.success)
        self.assertEqual(result.reason, 'Нет цели для атаки')
    
    @patch('Battle.base_mechanics.GameMechanics.apply_all_mechanics')
    def test_execute_dodge_success(self, mock_apply_mechanics):
        """Тест выполнения при уклонении цели"""
        # Настраиваем мок механик
        mock_apply_mechanics.return_value = {
            'dodge_success': True,
            'dodge_message': 'Уклонение!',
            'final_damage': 0,
            'blocked_damage': 0,
            'critical_hit': False
        }
        
        result = self.fireball.execute(self.character, self.targets)
        
        self.assertIsInstance(result, AbilityResult)
        self.assertFalse(result.success)
        # Проверяем, что сообщения существуют
        self.assertTrue(len(result.messages) > 0)
    
    @patch('Battle.base_mechanics.GameMechanics.apply_all_mechanics')
    @patch('Battle.battle_logger.battle_logger.create_log_message')
    def test_execute_successful_hit(self, mock_create_message, mock_apply_mechanics):
        """Тест успешного попадания"""
        # Настраиваем моки
        mock_apply_mechanics.return_value = {
            'dodge_success': False,
            'dodge_message': '',
            'final_damage': 80,  # 100 * 0.8
            'blocked_damage': 10,
            'critical_hit': False
        }
        mock_create_message.return_value = "Тестовое сообщение"
        
        result = self.fireball.execute(self.character, self.targets)
        
        self.assertIsInstance(result, AbilityResult)
        self.assertTrue(result.success)
        self.assertEqual(result.total_damage, 80)
        # Проверяем, что урон был нанесен
        self.target.take_damage.assert_called_once_with(80)
    
    @patch('Battle.base_mechanics.GameMechanics.apply_all_mechanics')
    @patch('Battle.battle_logger.battle_logger.create_log_message')
    def test_execute_critical_hit(self, mock_create_message, mock_apply_mechanics):
        """Тест критического попадания"""
        # Настраиваем моки
        mock_apply_mechanics.return_value = {
            'dodge_success': False,
            'dodge_message': '',
            'final_damage': 160,  # 100 * 0.8 * 2 (крит)
            'blocked_damage': 0,
            'critical_hit': True
        }
        mock_create_message.return_value = "Критическое попадание!"
        
        result = self.fireball.execute(self.character, self.targets)
        
        self.assertIsInstance(result, AbilityResult)
        self.assertTrue(result.success)
        self.assertEqual(result.total_damage, 160)
        self.target.take_damage.assert_called_once_with(160)
    
    def test_check_specific_conditions(self):
        """Тест проверки специфических условий"""
        # Пока метод всегда возвращает True
        self.assertTrue(self.fireball.check_specific_conditions(self.character, self.targets))
        self.assertTrue(self.fireball.check_specific_conditions(self.character, []))
        self.assertTrue(self.fireball.check_specific_conditions(self.character, [self.target, self.target]))

if __name__ == '__main__':
    unittest.main()