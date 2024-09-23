import asyncio
import aiofiles
import shutil
import os
from pathlib import Path
import argparse
import logging

# Налаштування логування
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Асинхронна функція для копіювання файлу в підпапку на основі розширення
async def copy_file(file_path: Path, output_folder: Path):
    try:
        # Отримуємо розширення файлу та створюємо відповідну підпапку
        ext = file_path.suffix[1:]  # Без крапки на початку
        target_folder = output_folder / ext
        
        # Створюємо підпапку, якщо вона не існує
        target_folder.mkdir(parents=True, exist_ok=True)

        # Копіюємо файл до підпапки
        target_path = target_folder / file_path.name
        async with aiofiles.open(file_path, 'rb') as fsrc:
            async with aiofiles.open(target_path, 'wb') as fdst:
                await fdst.write(await fsrc.read())

        print(f"Копіювання завершено: {file_path} -> {target_path}")

    except Exception as e:
        logging.error(f"Error copying file {file_path}: {e}")

# Асинхронна функція для читання файлів у вихідній папці
async def read_folder(source_folder: Path, output_folder: Path):
    try:
        # Проходимо по всіх файлах та папках у вихідній директорії
        for root, dirs, files in os.walk(source_folder):
            tasks = []
            for file_name in files:
                file_path = Path(root) / file_name
                tasks.append(copy_file(file_path, output_folder))

            # Чекаємо завершення копіювання всіх файлів у поточному каталозі
            await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f"Error reading folder {source_folder}: {e}")

# Головна функція
async def main():
    # Створюємо парсер аргументів командного рядка
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширеннями")
    
    # Додаємо аргументи для вихідної та цільової директорії
    parser.add_argument('source_folder', type=str, help='Шлях до вихідної папки')
    parser.add_argument('output_folder', type=str, help='Шлях до папки призначення')

    # Парсимо аргументи
    args = parser.parse_args()

    # Ініціалізуємо шляхи для вихідної та цільової папок
    source_folder = Path(args.source_folder)
    output_folder = Path(args.output_folder)

    # Перевіряємо, чи існують вихідна та цільова папки
    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(f"Source folder {source_folder} does not exist or is not a directory.")
        return
    
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    # Запускаємо асинхронну обробку папок
    await read_folder(source_folder, output_folder)

if __name__ == "__main__":
    # Запускаємо головну асинхронну функцію
    asyncio.run(main())
    
# для запуску з команндного рядка: python task_1.py /шлях/до/вихідної/папки /шлях/до/цільової/папки
