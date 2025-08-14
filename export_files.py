# collect_py_files.py

import os
from pathlib import Path

# Файлы, которые НЕ нужно включать
EXCLUDED_FILES = {"collect_py_files.py", "lines_counter.py"}

def should_include(path: Path) -> bool:
    """
    Проверяет, должен ли файл быть включён в сборку.
    Пропускает:
    - файлы из списка EXCLUDED_FILES
    - файлы в папках, начинающихся на '.'
    - любые __pycache__ папки (на всякий случай)
    """
    # Проверяем компоненты пути: если любая папка начинается с '.', игнорируем
    for part in path.parts:
        if part.startswith(".") and len(part) > 1:  # исключаем '.' как текущую папку
            return False

    # Исключаем конкретные файлы
    if path.name in EXCLUDED_FILES:
        return False

    return True

def main():
    root_dir = Path.cwd()
    output_file = root_dir / "output.txt"

    with open(output_file, "w", encoding="utf-8") as outfile:
        # Ищем все .py файлы рекурсивно
        for py_file in root_dir.rglob("*.py"):
            if py_file.is_file() and should_include(py_file):
                try:
                    # Относительный путь
                    rel_path = py_file.relative_to(root_dir)

                    # Записываем путь
                    outfile.write(f"- {rel_path}\n")

                    # Читаем и записываем содержимое
                    with open(py_file, "r", encoding="utf-8") as infile:
                        content = infile.read()
                        outfile.write(content)

                    # Отступ между файлами
                    outfile.write("\n\n")
                except Exception as e:
                    outfile.write(f"[Ошибка чтения файла: {e}]\n\n")

    print(f"✅ Сборка завершена! Все файлы записаны в {output_file}")

if __name__ == "__main__":
    main()