# Скрипт для компиляции файлов .po в .mo для всех поддерживаемых языков
# Используется для подготовки переводов к использованию в приложении Flask с Flask-Babel

import os
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Укажите путь к папке translations
translations_path = Path('translations')

# Проверка наличия папки translations
if not translations_path.exists():
    logging.error(f"Папка переводов '{translations_path}' не найдена. Проверьте правильность пути.")
    exit(1)

# Компиляция всех файлов .po в папке translations
for lang_path in translations_path.iterdir():
    lang_mo_path = lang_path / "LC_MESSAGES" / "messages.mo"
    lang_po_path = lang_path / "LC_MESSAGES" / "messages.po"

    if not lang_po_path.exists():
        logging.warning(f"Файл '{lang_po_path}' не найден. Пропускаем компиляцию для данного языка.")
        continue

    try:
        # Создание командной строки для компиляции .po в .mo
        compile_command = [
            "pybabel", "compile",
            "-i", str(lang_po_path),
            "-o", str(lang_mo_path)
        ]

        # Выполнение команды компиляции
        subprocess.run(compile_command, check=True)
        logging.info(f"Успешно скомпилирован файл '{lang_po_path}' в '{lang_mo_path}'")
    except subprocess.CalledProcessError as e:
        logging.error(f"Не удалось скомпилировать файл '{lang_po_path}': {e}")
    except Exception as e:
        logging.error(f"Произошла ошибка при компиляции файла '{lang_po_path}': {e}")

logging.info("Процесс компиляции завершен.")
