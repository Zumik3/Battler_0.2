#Игровые
MAX_ROUNDS = 30
MAX_ROOMS = 10
BASE_ENERGY_COST = 10
BASE_ENERGY_RECOVERY = 30 #процент восстановления энегрии после битвы
RESTORE_ENERGY_AMOUNT = 25

# Базовые коэффициенты наград
EXP_BASE = 10
GOLD_BASE = 5
EXP_VARIANCE = 2
GOLD_VARIANCE = 3

# Типы слотов экипировки
SLOT_TYPE_WEAPON = 'weapon'
SLOT_TYPE_ARMOR = 'armor'
SLOT_TYPE_ACCESSORY = 'accessory'
SLOT_TYPE_CONSUMABLE = 'consumable'
EQUIPMENT_SLOT_TYPES = [SLOT_TYPE_WEAPON, SLOT_TYPE_ARMOR, SLOT_TYPE_ACCESSORY, SLOT_TYPE_CONSUMABLE]

# Названия слотов для отображения
SLOT_NAME_WEAPON = 'Оружие'
SLOT_NAME_ARMOR = 'Броня'
SLOT_NAME_ACCESSORY = 'Аксессуар'
SLOT_NAME_CONSUMABLE = 'Расходник'

#Визуальные
INPUT_PROMPT = "❱ "
PROGRESS_BAR_CHARS = "■□"
PROGRESS_BORDER_CHARS = "[]"
DAMAGE_LIST_ICON = "🔸"

PLAYER_NAME_COLUMN_WIDTH = 12  # Для выравнивания баров (6 имя + 6 остальное)
MONSTER_NAME_COLUMN_WIDTH = 25  # Для выравнивания баров

#Служебные
BASE_DELAY_MS = 400  # Задержка между действиями
ROUND_DELAY_MS = 1200  # Пауза между раундами
LOG_MAX_LINES = 200
MIN_TOP_HEIGHT = 10

HP_BAR_COLORS = {2, 6, 1}
HP_BAR_WIDTH = 10
ENERGY_BAR_WIDTH = 4
ENERGY_BAR_COLORS = {1, 1, 1}

ABILITIES_PATH = "Characters/Abilities"