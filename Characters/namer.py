# namer.py
import random

class EnemyNamer:
    """Генератор имен для врагов."""
    
    # Базовые списки для генерации имен
    ADJECTIVES = [
        "Грязный", "Гнилой", "Кровавый", "Яростный", "Мерзкий",
        "Зловонный", "Свирепый", "Хищный", "Мрачный", "Злобный",
        "Костяной", "Пылающий", "Ледяной", "Теневой", "Ядовитый",
        "Голодный", "Бешеный", "Могильный", "Проклятый", "Древний",
        "Скользкий", "Паразитный", "Гнойный", "Колючий", "Странный",
        "Искаженный", "Порочный", "Чумной", "Мертвенный", "Смердящий"
    ]
    
    BASE_NAMES = [
        "Гоблин", "Орк", "Скелет", "Волшебник", "Тролль",
        "Кобольд", "Гремлин", "Бандит", "Головорез", "Мутант",
        "Слизень", "Жук", "Паук", "Крыса", "Ворон",
        "Варвар", "Некромант", "Шаман", "Берсерк", "Ассасин",
        "Крысолюд", "Полукровка", "Изгнанник", "Отступник", "Мерзавец",
        "Демон", "Бес", "Имп", "Вампир", "Призрак",
        "Элементаль", "Гуль", "Лич", "Банши", "Оборотень"
    ]
    
    @staticmethod
    def generate_name():
        """
        Генерирует короткое имя для врага (2-3 слова).
        """
        # 90% шанс на 2 слова, 10% шанс на 3 слова
        if random.random() < 0.9:
            # 2 слова: Прилагательное + Базовое имя
            adjective = random.choice(EnemyNamer.ADJECTIVES)
            base_name = random.choice(EnemyNamer.BASE_NAMES)
            return f"{adjective} {base_name}"
        else:
            # 3 слова: Прилагательное + Базовое имя + Уточнение
            adjective = random.choice(EnemyNamer.ADJECTIVES)
            base_name = random.choice(EnemyNamer.BASE_NAMES)
            
            # Варианты третьего слова
            third_word_options = [
                "Старший", "Младший", "Великий", "Могучий", "Ужасный",
                "Бес", "Повелитель", "Страж", "Охотник", "Мститель",
                "из Тьмы", "из Ада", "Крови", "Смерти", "Хаоса"
            ]
            
            third_word = random.choice(third_word_options)
            
            # Если это место, добавляем "из"
            if third_word in ["Тьмы", "Ада", "Крови", "Смерти", "Хаоса"]:
                return f"{adjective} {base_name} из {third_word}"
            else:
                return f"{adjective} {base_name} {third_word}"
    
    @staticmethod
    def generate_simple_name():
        """Генерирует очень простое имя (обычно 1-2 слова)"""
        if random.random() < 0.3:
            # 30% шанс на одно слово
            return random.choice(EnemyNamer.BASE_NAMES)
        else:
            # 70% шанс на два слова
            adjective = random.choice(EnemyNamer.ADJECTIVES)
            base_name = random.choice(EnemyNamer.BASE_NAMES)
            return f"{adjective} {base_name}"