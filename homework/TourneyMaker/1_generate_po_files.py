import os
import polib
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

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

# Директория для хранения файлов переводов
po_files_dir = "translations"

# Список примерных переводимых сообщений для заполнения .po файлов
messages_to_translate = [
    "You have successfully registered!",
    "A user with this email already exists.",
    "Welcome, %(username)s!",
    "Invalid email or password.",
    "You have been logged out.",
    "Subject: Password recovery\n\nYour new password is: %(new_password)s",
    "A new password has been sent to your email.",
    "Error sending email: %(error)s",
    "No user found with this email.",
    "Participant successfully registered!",
    "Participants in a match must be different.",
    "Match successfully created!",
    "Home",
    "Register Participant",
    "Create Tournament",
    "Create Match",
    "Register User",
    "Login",
    "Logout",
    "Language",
    "Recover Password"
]

# Создание директорий и .po файлов для каждого языка
for lang in supported_languages:
    lang_code = lang["language"].lower()
    lang_name = lang["name"]
    lang_dir = os.path.join(po_files_dir, lang_code, "LC_MESSAGES")

    # Создаем директорию для языка, если она не существует
    if not os.path.exists(lang_dir):
        os.makedirs(lang_dir)
        logging.info(f"Создана директория для языка: {lang_name} ({lang_code})")

    # Создаем или обновляем .po файл
    po_file_path = os.path.join(lang_dir, "messages.po")
    if not os.path.exists(po_file_path):
        po = polib.POFile()

        # Заполнение заголовков .po файла
        po.metadata = {
            'Project-Id-Version': 'TourneyMaker 1.0',
            'Report-Msgid-Bugs-To': 'd1kolesnikov@gmail.com',
            'POT-Creation-Date': '2024-10-28 12:00+0000',
            'PO-Revision-Date': '2024-10-28 12:00+0000',
            'Last-Translator': 'Automatically generated',
            'Language-Name': f'{lang_name}',
            'Language': lang_code,
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=UTF-8',
            'Content-Transfer-Encoding': '8bit',
        }

        # Добавление переводимых сообщений в .po файл
        for msgid in messages_to_translate:
            entry = polib.POEntry(msgid=msgid, msgstr="")
            po.append(entry)

        # Сохранение файла
        po.save(po_file_path)
        logging.info(f"Создан файл перевода: {po_file_path}")
    else:
        # Чтение существующего файла для сравнения
        existing_po = polib.pofile(po_file_path)
        new_po = polib.POFile()
        new_po.metadata = existing_po.metadata

        # Заполнение новыми сообщениями
        for msgid in messages_to_translate:
            if not existing_po.find(msgid):
                entry = polib.POEntry(msgid=msgid, msgstr="")
                existing_po.append(entry)
                logging.info(f"Добавлена новая строка: {msgid}")

        # Переименовать существующий файл с добавлением префикса _old и номера, если файл уже существует
        version = 1
        old_po_file_path = po_file_path.replace("messages.po", f"messages_old_v{version}.po")
        while os.path.exists(old_po_file_path):
            version += 1
            old_po_file_path = po_file_path.replace("messages.po", f"messages_old_v{version}.po")
        os.rename(po_file_path, old_po_file_path)
        logging.info(f"Старый файл перевода сохранен как: {old_po_file_path}")

        # Сохранить новый файл перевода
        existing_po.save(po_file_path)
        logging.info(f"Файл перевода обновлен: {po_file_path}")
