from Config.game_config import EQUIPMENT_SLOT_TYPES


class EquipmentSlot:
    """Класс для представления слота экипировки."""
    
    def __init__(self, name, slot_type):
        self.name = name          # Имя слота (для отображения)
        self.slot_type = slot_type # Тип слота (для идентификации)
        self.item = None          # Предмет в слоте
    
    def equip(self, item):
        """Экипировать предмет в слот."""
        if not hasattr(item, 'name'):
            raise ValueError("Предмет должен иметь атрибут 'name'")
        
        old_item = self.item
        self.item = item
        return old_item  # Возвращаем старый предмет, если был
    
    def unequip(self):
        """Снять предмет со слота."""
        old_item = self.item
        self.item = None
        return old_item
    
    def is_empty(self):
        """Проверить, пуст ли слот."""
        return self.item is None
    
    def get_item(self):
        """Получить предмет из слота."""
        return self.item


class EquipmentMixin:
    """Миксин для работы с экипировкой."""
    
    def equip_item(self, item, slot_type):
        """Экипировать предмет в указанный слот."""
        if slot_type not in self.equipment_slots:
            print(f"Неверный тип слота: {slot_type}. Доступные слоты: {', '.join(EQUIPMENT_SLOT_TYPES)}")
            return False
        
        try:
            slot = self.equipment_slots[slot_type]
            old_item = slot.equip(item)
            
            if old_item:
                print(f"Снят предмет: {old_item.name} со слота {slot.name}")
            
            print(f"{item.name} экипирован в слот {slot.name}")
            return True
            
        except ValueError as e:
            print(f"Ошибка экипировки: {e}")
            return False
    
    def unequip_item(self, slot_type):
        """Снять предмет из указанного слота."""
        if slot_type not in self.equipment_slots:
            print(f"Неверный тип слота: {slot_type}. Доступные слоты: {', '.join(EQUIPMENT_SLOT_TYPES)}")
            return None
        
        slot = self.equipment_slots[slot_type]
        item = slot.unequip()
        
        if item:
            print(f"Снят предмет: {item.name} со слота {slot.name}")
            return item
        else:
            print(f"Слот {slot.name} пуст")
            return None
    
    def unequip_item_by_name(self, item_name):
        """Снять предмет по имени."""
        for slot_type, slot in self.equipment_slots.items():
            if slot.item and hasattr(slot.item, 'name') and slot.item.name == item_name:
                item = slot.unequip()
                print(f"Снят предмет: {item_name} со слота {slot.name}")
                return item
        print(f"Предмет {item_name} не найден в экипировке")
        return None
    
    def show_equipment(self):
        """Показать всю экипировку."""
        print(f"Экипировка {self.name}:")
        for slot in self.equipment_slots.values():
            if slot.item:
                print(f"  {slot.name}: {slot.item.name}")
            else:
                print(f"  {slot.name}: пусто")
    
    def get_equipped_item(self, slot_type):
        """Получить предмет из указанного слота."""
        if slot_type in self.equipment_slots:
            return self.equipment_slots[slot_type].get_item()
        return None
    
    def get_all_equipped_items(self):
        """Получить список всех экипированных предметов."""
        return [slot.item for slot in self.equipment_slots.values() if not slot.is_empty()]
    
    def is_slot_empty(self, slot_type):
        """Проверить, пуст ли указанный слот."""
        if slot_type in self.equipment_slots:
            return self.equipment_slots[slot_type].is_empty()
        return True
    
    def get_empty_slots(self):
        """Получить список типов пустых слотов."""
        return [slot_type for slot_type, slot in self.equipment_slots.items() if slot.is_empty()]
    
    def get_occupied_slots(self):
        """Получить список типов занятых слотов."""
        return [slot_type for slot_type, slot in self.equipment_slots.items() if not slot.is_empty()]