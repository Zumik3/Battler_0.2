import os
import sys

def count_lines_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for line in f)
    except Exception as e:
        print(f"Ошибка при чтении файла {filepath}: {e}")
        return 0

def count_lines_in_py_files(root_dir='.'):
    total_lines = 0
    py_files = []
    current_script = os.path.abspath(sys.argv[0])
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                abs_filepath = os.path.abspath(filepath)
                
                # Пропускаем файл, из которого запускается программа
                if abs_filepath == current_script:
                    print(f"Пропущен файл: {filepath} (текущий скрипт)")
                    continue
                
                lines = count_lines_in_file(filepath)
                py_files.append((filepath, lines))
                total_lines += lines
    
    py_files.sort(key=lambda x: os.path.abspath(x[0]))
    
    for filepath, lines in py_files:
        print(f"{filepath}: {lines} строк")
    
    return total_lines

if __name__ == "__main__":
    total = count_lines_in_py_files()
    print(f"\nОбщее количество строк во всех .py файлах: {total}")