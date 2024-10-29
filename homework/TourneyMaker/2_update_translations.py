import os
import requests
import polib
import logging
import re
import shutil
import time

def remove_old_and_mo_files(base_dir="translations"):
    """
    Функция для удаления всех файлов с суффиксом _old и файлов *.mo в указанной директории.
    """
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".mo") or "_old" in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                logging.info(f"Удален файл: {file_path}")

remove_old_and_mo_files()

# Настройка логирования
def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

# Включить или отключить режим отладки
DEBUG_MODE = False
setup_logging(debug=DEBUG_MODE)

# DeepL API Key (provided by user)
DEEPL_API_KEY = "dc65358a-25d6-4b59-b119-735d26f3fa13:fx"
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

# Список доступных языков для перевода
supported_languages = [
    {"language": "AR", "name": "Арабский"},
    {"language": "BG", "name": "Болгарский"},
    {"language": "CS", "name": "Чешский"},
    {"language": "DA", "name": "Датский"},
    {"language": "DE", "name": "Немецкий"},
    {"language": "EL", "name": "Греческий"},
    {"language": "EN", "name": "Английский"},
    {"language": "ES", "name": "Испанский"},
    {"language": "ET", "name": "Эстонский"},
    {"language": "FI", "name": "Финский"},
    {"language": "FR", "name": "Французский"},
    {"language": "HU", "name": "Венгерский"},
    {"language": "ID", "name": "Индонезийский"},
    {"language": "IT", "name": "Итальянский"},
    {"language": "JA", "name": "Японский"},
    {"language": "KO", "name": "Корейский"},
    {"language": "LT", "name": "Литовский"},
    {"language": "LV", "name": "Латышский"},
    {"language": "NB", "name": "Норвежский букмол"},
    {"language": "NL", "name": "Голландский"},
    {"language": "PL", "name": "Польский"},
    {"language": "PT", "name": "Португальский"},
    {"language": "RO", "name": "Румынский"},
    {"language": "RU", "name": "Русский"},
    {"language": "SK", "name": "Словацкий"},
    {"language": "SL", "name": "Словенский"},
    {"language": "SV", "name": "Шведский"},
    {"language": "TR", "name": "Турецкий"},
    {"language": "UK", "name": "Украинский"},
    {"language": "ZH", "name": "Китайский"}
]

# Проверка наличия файлов переводов
po_files_dir = "translations"
if not os.path.exists(po_files_dir):
    logging.error(f"Папка {po_files_dir} не существует. Убедитесь, что директория с переводами доступна.")
    exit(1)

# Функция для проверки и сохранения перевода с учетом наличия переменных
def translate_text(text, target_lang):
    logging.debug(f"Запуск функции translate_text для текста: '{text}' и языка: {target_lang}")
    # Проверка поддерживается ли язык
    if not any(lang['language'] == target_lang.upper() for lang in supported_languages):
        logging.error(f"Язык {target_lang} не поддерживается DeepL API.")
        return text

    # Проверка наличия переменных, как '%(username)s'
    placeholders = re.findall(r'%\([a-zA-Z_]+\)s', text)
    placeholder_map = {f"PLACEHOLDER_{i}": placeholder for i, placeholder in enumerate(placeholders)}
    for key, value in placeholder_map.items():
        text = text.replace(value, key)

    # Отправка запроса к DeepL
    try:
        logging.debug(f"Текст перед отправкой на перевод: '{text}' на язык {target_lang}")
        response = requests.post(DEEPL_API_URL, params={
            'auth_key': DEEPL_API_KEY,
            'text': text,
            'target_lang': target_lang
        }, timeout=10)

        # Логирование статуса ответа и тела ответа для отладки
        logging.debug(f"Код статуса ответа от DeepL: {response.status_code}")
        logging.debug(f"Тело ответа от DeepL: {response.text}")

        if response.status_code == 200:
            response_data = response.json()
            if 'translations' in response_data and len(response_data['translations']) > 0:
                translated_text = response_data['translations'][0].get('text', text)
                logging.debug(f"Переведенный текст: '{translated_text}'")
            else:
                logging.error(f"Ответ от DeepL не содержит переводов: {response.text}")
                return text

            # Восстановление переменных после перевода
            for key, value in placeholder_map.items():
                translated_text = translated_text.replace(key, value)

            return translated_text
        else:
            logging.error(f"Ошибка при обращении к DeepL API для языка {target_lang}: {response.text}")
            return text
    except requests.RequestException as e:
        logging.error(f"Ошибка сети при обращении к DeepL API для языка {target_lang}: {e}")
        return text

# Обновление всех файлов .po
for root, dirs, files in os.walk(po_files_dir):
    for file in files:
        if file.endswith('.po'):
            po_file_path = os.path.join(root, file)
            lang_code = os.path.basename(os.path.dirname(root)).upper()  # Извлечение языка из структуры директорий

            logging.info(f"Обработка файла перевода: {po_file_path}")

            # Создание резервной копии
            backup_file_path = f"{po_file_path}.bak"
            shutil.copy2(po_file_path, backup_file_path)

            po = polib.pofile(po_file_path)

            for entry in po:
                logging.info(f"  Перевод фразы: '{entry.msgid}' на язык {lang_code}")
                retries = 3
                for attempt in range(retries):
                    translated_text = translate_text(entry.msgid, lang_code)
                    if translated_text != entry.msgid:  # Если перевод отличается от оригинала
                        entry.msgstr = translated_text
                        logging.info(f"  Успешный перевод для '{entry.msgid}': '{translated_text}'")
                        break
                    else:
                        logging.warning(f"  Попытка {attempt + 1}: Перевод для '{entry.msgid}' не был выполнен. Повторная попытка...")
                        time.sleep(2 ** attempt)  # Экспоненциальная задержка

            # Сохранение обновлённого .po файла
            po.save(po_file_path)
            logging.info(f"  Файл {po_file_path} обновлён.")
