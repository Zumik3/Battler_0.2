import os

# Список требуемых файлов
required_files = [
    './Characters/character.py',
    './Characters/base_mechanics.py',
    './Battle/battle_logic.py',
    './Battle/round_logic.py',
    './Characters/base_stats.py',
    './Battle/base_mechanics.py',
    './Characters/Abilities/abilities.py'
]

def export_files_to_single_file(output_filename="project_export.txt"):
    """Экспортирует содержимое файлов в один текстовый файл"""
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write("ЭКСПОРТ СОДЕРЖИМОГО ФАЙЛОВ ПРОЕКТА\n")
        output_file.write("="*60 + "\n\n")
        
        for i, file_path in enumerate(required_files, 1):
            output_file.write(f"[ФАЙЛ {i}/{len(required_files)}]\n")
            output_file.write(f"ПУТЬ: {file_path}\n")
            output_file.write("-" * 40 + "\n")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        output_file.write(content)
                        output_file.write("\n")
                except Exception as e:
                    output_file.write(f"ОШИБКА ЧТЕНИЯ ФАЙЛА: {e}\n")
            else:
                output_file.write("ФАЙЛ НЕ НАЙДЕН\n")
            
            output_file.write("-" * 40 + "\n")
            output_file.write(f"КОНЕЦ ФАЙЛА: {file_path}\n")
            output_file.write("="*60 + "\n\n")
    
    print(f"Экспорт завершен. Файл сохранен как: {output_filename}")

if __name__ == "__main__":
    export_files_to_single_file()