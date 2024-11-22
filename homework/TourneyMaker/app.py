
# Начальная структура проекта с использованием Flask для проведения турниров

# Импортируем необходимые модули
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import Babel, gettext
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import secrets
from functools import wraps
import polib
import pycountry  # Для получения информации о флагах
import math
import random
import logging

# Настройка логирования для дебага
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему для доступа к этой странице.', 'warning')
            return redirect(url_for('login_user'))
        return f(*args, **kwargs)
    return decorated_function

# Путь к папке с переводами
TRANSLATIONS_PATH = 'translations'

# Функция для получения полного имени языка из .po файла
def get_language_name_from_po_file(po_file_path):
    try:
        po = polib.pofile(po_file_path)
        for entry in po:
            if entry.msgid == "Language":
                return entry.msgstr
    except Exception as e:
        print(f"Ошибка при чтении файла {po_file_path}: {e}")
    return None

# Функция для получения флага по коду языка
def get_flag_for_language(lang_code):
    try:
        country = pycountry.languages.get(alpha_2=lang_code)
        if country and hasattr(country, 'alpha_2'):
            # Используем Unicode для представления флага
            return chr(127462 + ord(country.alpha_2[0]) - ord('a')) + chr(127462 + ord(country.alpha_2[1]) - ord('a'))
    except Exception as e:
        print(f"Ошибка при определении флага для языка {lang_code}: {e}")
    return ""

# Функция для динамического определения поддерживаемых языков
def get_supported_languages():
    languages = {}
    # Проходим по всем подкаталогам в папке с переводами
    if os.path.exists(TRANSLATIONS_PATH):
        for root, dirs, files in os.walk(TRANSLATIONS_PATH):
            for dir_name in dirs:
                # Проверяем наличие подпапки LC_MESSAGES (стандартная структура для gettext)
                lc_messages_path = os.path.join(root, dir_name, 'LC_MESSAGES')
                if os.path.exists(lc_messages_path):
                    po_file_path = os.path.join(lc_messages_path, 'messages.po')
                    if os.path.exists(po_file_path):
                        language_name = get_language_name_from_po_file(po_file_path)
                        if language_name:
                            languages[dir_name] = {
                                'name': language_name,
                                'flag': get_flag_for_language(dir_name)
                            }
                        else:
                            languages[dir_name] = {
                                'name': dir_name.capitalize(),
                                'flag': get_flag_for_language(dir_name)
                            }  # Добавляем язык в словарь, если не удалось получить полное имя
    return languages

# Получаем список поддерживаемых языков
LANGUAGES = get_supported_languages()


# Создаем экземпляр приложения Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Генерация секретного ключа для сессий


def get_bebel_supported_languages():
    return list(LANGUAGES)

# Получаем список поддерживаемых языков для Flask-Babel
SUPPORTED_LANGUAGES = get_bebel_supported_languages()

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = SUPPORTED_LANGUAGES
babel = Babel(app)

def get_locale():
    # Сначала проверяем, есть ли язык, сохраненный в сессии
    if 'lang' in session:
        return session['lang']
    # Если нет, используем заголовок из браузера
    return request.accept_languages.best_match(LANGUAGES.keys())



# Изменение в функции next_stage для корректного отображения имени участника
# Исправленная функция next_stage для корректного отображения имени победителя
# Унификация функции перехода к следующей стадии турнира



def get_current_stage(tournament_id, cursor):
    """
    Получает текущую стадию турнира по ID.
    """
    current_stage_query = '''
        SELECT MAX(stage) AS current_stage
        FROM matches
        WHERE tournament_id = ?
    '''
    current_stage_result = cursor.execute(current_stage_query, (tournament_id,)).fetchone()

    if current_stage_result['current_stage'] is None:
        raise ValueError('Текущая стадия не найдена.')

    return int(current_stage_result['current_stage'])

def check_all_matches_completed(tournament_id, current_stage, cursor):
    """
    Проверяет, завершены ли все матчи текущей стадии.
    """
    matches_query = '''
        SELECT id, result
        FROM matches
        WHERE tournament_id = ? AND stage = ? AND result IS NULL
    '''
    incomplete_matches = cursor.execute(matches_query, (tournament_id, current_stage)).fetchall()
    if incomplete_matches:
        raise ValueError("Не все матчи текущей стадии завершены.")
    #return len(incomplete_matches) == 0  # Если есть незавершенные матчи, вернем False

    completed_matches = cursor.execute('''
        SELECT id, result
        FROM matches
        WHERE tournament_id = ? AND stage = ? AND result IS NOT NULL
    ''', (tournament_id, current_stage)).fetchall()
    logging.debug(f'Завершённые матчи стадии {current_stage}: {[match["id"] for match in completed_matches]}')

    return True  # Если нет незавершенных матчей, вернем True

def get_stage_winners(tournament_id, current_stage, cursor):
    """
    Получает победителей текущей стадии турнира.
    """
    winners_query = '''
        SELECT result_id, result
        FROM matches
        WHERE tournament_id = ? AND stage = ? AND result IS NOT NULL
    '''
    winners = cursor.execute(winners_query, (tournament_id, current_stage)).fetchall()
    return winners


import random
import logging


def handle_auto_advance(winners, cursor):
    """
    Обрабатывает случай, когда количество победителей нечетное.
    Возвращает обновлённый список победителей и список участников,
    которые автоматически проходят в следующую стадию.
    """
    logging.debug(f"Начало обработки авто-прохода. Текущие победители: {winners}")
    auto_advancing_participants = []

    # Пока количество победителей нечётное
    while len(winners) % 2 != 0:
        # Выбираем случайного участника для авто-прохода
        auto_advancing_participant_id = random.choice(winners)
        winners.remove(auto_advancing_participant_id)

        logging.info(f"Участник ID={auto_advancing_participant_id} выбран для автоматического прохода.")

        # Получаем имя участника из базы данных
        participant_query = '''
            SELECT name FROM participants WHERE id = ?
        '''
        try:
            participant_row = cursor.execute(participant_query, (auto_advancing_participant_id,)).fetchone()
            if participant_row is None:
                raise ValueError(f"Участник с ID={auto_advancing_participant_id} не найден в таблице participants.")

            participant_name = participant_row['name']
            logging.debug(f"Имя участника ID={auto_advancing_participant_id}: {participant_name}")

            # Обновляем данные в таблице matches
            match_update_query = '''
                UPDATE matches
                SET result = ?, result_id = ?
                WHERE participant1_id = ? AND participant2_id IS NULL
            '''
            cursor.execute(match_update_query,
                           (participant_name, auto_advancing_participant_id, auto_advancing_participant_id))
            logging.info(f"Участник ID={auto_advancing_participant_id} успешно обновлён в таблице matches: "
                         f"result={participant_name}, result_id={auto_advancing_participant_id}")

            # Добавляем участника в список авто-прохода
            auto_advancing_participants.append({
                'id': auto_advancing_participant_id,
                'name': participant_name
            })

        except Exception as e:
            logging.error(f"Ошибка при обработке авто-прохода для участника ID={auto_advancing_participant_id}: {e}")
            raise

    logging.debug(
        f"Авто-проход завершён. Оставшиеся победители: {winners}, авто-прошедшие участники: {auto_advancing_participants}")
    return winners, auto_advancing_participants


def create_matches_for_next_stage(tournament_id, current_stage, winners, auto_advancing_participants, cursor):
    """
    Создает матчи для следующего этапа турнира.

    Аргументы:
        tournament_id (int): ID турнира.
        current_stage (int): Текущая стадия турнира.
        winners (list): Список победителей текущей стадии.
        auto_advancing_participants (list): Список участников, проходящих автоматически.
        cursor (sqlite3.Cursor): Курсор базы данных.
    """
    logging.info(f'Начинаем создание матчей для следующей стадии турнира ID={tournament_id}.')
    new_stage = current_stage + 1

    logging.info(f'Текущая стадия: {current_stage}, создаётся следующая стадия: {new_stage}.')
    logging.debug(f'Победители текущей стадии: {[winner["result_id"] for winner in winners]}')
    logging.debug(f'Участники, проходящие автоматически: {[p["result_id"] for p in auto_advancing_participants]}')

    # Создаем матчи для пар участников
    for i in range(0, len(winners), 2):
        if i + 1 < len(winners):
            participant1_id = winners[i]['result_id']
            participant2_id = winners[i + 1]['result_id']

            try:
                insert_match_query = '''
                    INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id)
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(insert_match_query, (tournament_id, new_stage, participant1_id, participant2_id))
                logging.debug(f'Создан матч: stage={new_stage}, tournament_id={tournament_id}, '
                              f'participant1_id={participant1_id}, participant2_id={participant2_id}')
            except Exception as e:
                logging.error(f'Ошибка при создании матча для участников {participant1_id} и {participant2_id}: {str(e)}')
        else:
            logging.warning(f'Остался участник без пары: ID={winners[i]["result_id"]} на стадии {current_stage}.')

    # Создаем матчи для участников, проходящих автоматически
    for auto_participant in auto_advancing_participants:
        participant_id = auto_participant['result_id']
        participant_name = auto_participant['result']

        try:
            cursor.execute('''
                INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id, result, result_id)
                VALUES (?, ?, ?, NULL, ?, ?)
            ''', (tournament_id, new_stage, participant_id, participant_name, participant_id))
            logging.debug(f'Участник {participant_name} (ID={participant_id}) автоматически проходит в следующий этап '
                          f'(stage={new_stage}, tournament_id={tournament_id}).')
        except Exception as e:
            logging.error(f'Ошибка при создании матча для автоматически проходящего участника ID={participant_id}: {str(e)}')

    logging.info(f'Стадия {new_stage} турнира ID={tournament_id} успешно создана.')


@app.route('/tournament/<int:tournament_id>/proceed_stage', methods=['POST'])
@login_required
def proceed_stage(tournament_id):
    """
    Обрабатывает переход к следующей стадии турнира.
    Учитывает победителей текущей стадии, а также участников, не участвовавших в стадии play-in (stage 0).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    logging.info(f'--- Начало перехода к следующей стадии турнира ID={tournament_id} ---')

    try:
        # Получаем текущую стадию
        current_stage_query = '''
            SELECT MAX(stage) AS current_stage
            FROM matches
            WHERE tournament_id = ?
        '''
        current_stage_result = cursor.execute(current_stage_query, (tournament_id,)).fetchone()

        if current_stage_result['current_stage'] is None:
            logging.error(f'Ошибка: текущая стадия турнира ID={tournament_id} не найдена.')
            flash('Ошибка: текущая стадия не найдена.', 'error')
            return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

        current_stage = int(current_stage_result['current_stage'])
        logging.info(f'Текущая стадия турнира ID={tournament_id}: {current_stage}')

        # Проверяем, что все матчи текущей стадии завершены
        matches_query = '''
            SELECT id, result
            FROM matches
            WHERE tournament_id = ? AND stage = ? AND result IS NULL
        '''
        incomplete_matches = cursor.execute(matches_query, (tournament_id, current_stage)).fetchall()
        if incomplete_matches:
            logging.warning(f'Не все матчи стадии {current_stage} турнира ID={tournament_id} завершены.')
            flash('Ошибка: не все матчи текущей стадии завершены.', 'error')
            return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

        # Получаем победителей текущей стадии
        winners_query = '''
            SELECT result_id
            FROM matches
            WHERE tournament_id = ? AND stage = ? AND result IS NOT NULL
        '''
        winners = [row['result_id'] for row in cursor.execute(winners_query, (tournament_id, current_stage)).fetchall()]
        logging.info(f'Победители стадии {current_stage} турнира ID={tournament_id}: {winners}')

        # Если стадия 0 (play-in), добавляем участников, не участвовавших в матчах play-in
        if current_stage == 0:
            logging.info('Добавляем участников, не участвовавших в стадии play-in.')
            remaining_participants_query = '''
                SELECT id
                FROM participants
                WHERE tournament_id = ? AND id NOT IN (
                    SELECT participant1_id FROM matches WHERE tournament_id = ?
                    UNION
                    SELECT participant2_id FROM matches WHERE tournament_id = ?
                )
            '''
            remaining_participants = [row['id'] for row in cursor.execute(remaining_participants_query, (tournament_id, tournament_id, tournament_id)).fetchall()]
            logging.debug(f'Оставшиеся участники турнира ID={tournament_id}, не участвовавшие в play-in: {remaining_participants}')
            winners.extend(remaining_participants)

        # Если остался только один победитель, завершаем турнир
        if len(winners) == 1:
            winner_id = winners[0]
            participant_query = '''
                SELECT name FROM participants WHERE id = ?
            '''
            winner_name = cursor.execute(participant_query, (winner_id,)).fetchone()['name']
            cursor.execute('''
                UPDATE tournaments
                SET winner_id = ?, winner_name = ?
                WHERE id = ?
            ''', (winner_id, winner_name, tournament_id))
            conn.commit()
            logging.info(f'Турнир ID={tournament_id} завершён. Победитель: ID={winner_id}, {winner_name}.')
            flash(f'Турнир завершён! Победитель: {winner_name}.', 'success')
            return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

        # Создаём матчи для следующей стадии
        new_stage = current_stage + 1
        logging.info(f'Создаём матчи для стадии {new_stage} турнира ID={tournament_id}.')
        auto_advancing_participant = None

        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                # Формируем матч между двумя участниками
                participant1_id = winners[i]
                participant2_id = winners[i + 1]
                cursor.execute('''
                    INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id)
                    VALUES (?, ?, ?, ?)
                ''', (tournament_id, new_stage, participant1_id, participant2_id))
                logging.debug(
                    f'Создан матч: stage={new_stage}, tournament_id={tournament_id}, participant1_id={participant1_id}, participant2_id={participant2_id}')
            else:
                # Участник без пары автоматически проходит в следующий этап
                auto_advancing_participant = winners[i]

                # Получаем имя участника из базы данных
                participant_query = '''
                    SELECT name FROM participants WHERE id = ?
                '''
                participant_row = cursor.execute(participant_query, (auto_advancing_participant,)).fetchone()
                if participant_row is None:
                    logging.error(f"Участник с ID={auto_advancing_participant} не найден в таблице participants.")
                    raise ValueError(f"Участник с ID={auto_advancing_participant} не найден.")

                participant_name = participant_row['name']
                logging.debug(f'Имя участника ID={auto_advancing_participant}: {participant_name}')

                # Вставляем матч с автоматическим проходом
                cursor.execute('''
                    INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id, result, result_id)
                    VALUES (?, ?, ?, NULL, ?, ?)
                ''', (
                tournament_id, new_stage, auto_advancing_participant, participant_name, auto_advancing_participant))
                logging.debug(
                    f'Участник ID={auto_advancing_participant} автоматически проходит в следующий этап (stage={new_stage}). '
                    f'Результат: {participant_name}, result_id={auto_advancing_participant}')

        # Фиксируем изменения
        conn.commit()
        logging.info(f'Стадия {new_stage} турнира ID={tournament_id} успешно создана.')

        # Возвращаем JSON-ответ
        return jsonify({'success': True, 'message': 'Следующий этап турнира успешно создан!'})

    except Exception as e:
        logging.error(f'Ошибка при переходе к следующей стадии турнира ID={tournament_id}: {str(e)}')
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        conn.close()
        logging.info(f'--- Завершение перехода к следующей стадии турнира ID={tournament_id} ---')



# Маршрут для изменения языка
@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session['lang'] = language
    return redirect(request.referrer or url_for('index'))

babel.init_app(app, locale_selector=get_locale)

# Добавляем контекстный процессор для получения текущей локали
# EN: Adding context processor to get the current locale
# FR: Ajout d'un processeur de contexte pour obtenir la locale actuelle
# ES: Añadir un procesador de contexto para obtener la configuración regional actual
@app.context_processor
def inject_globals():
    return {
        'locale': get_locale(),
        'LANGUAGES': LANGUAGES,
        'current_language': get_locale()
    }

# Функция для подключения к базе данных
# EN: Function for connecting to the database
# FR: Fonction pour se connecter à la base de données
# ES: Función para conectarse a la base de datos
DATABASE = 'tournament.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Функция для создания базы данных и необходимых таблиц, если они не существуют
# EN: Function for creating the database and necessary tables if they do not exist
# FR: Fonction pour créer la base de données et les tables nécessaires si elles n'existent pas
# ES: Función para crear la base de datos y las tablas necesarias si no existen
# Функция для создания базы данных и необходимых таблиц, если они не существуют
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Проверка и создание таблицы турниров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            winner_name TEXT,
            winner_id INTEGER,
            description TEXT
        )
    """)
    # Проверка и создание таблицы участников
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            tournament_id INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
            UNIQUE (name, tournament_id)
        )
    """)
    # Проверка и создание таблицы матчей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            participant1_id INTEGER,
            participant2_id INTEGER,
            result TEXT,
            result_id INTEGER,
            stage INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
            FOREIGN KEY (participant1_id) REFERENCES participants (id),
            FOREIGN KEY (participant2_id) REFERENCES participants (id),
            FOREIGN KEY (result_id) REFERENCES participants (id)
        )
    """)
    # Проверка и создание таблицы пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()



# Регистрация нового пользователя
# EN: Registering a new user
# FR: Enregistrement d'un nouvel utilisateur
# ES: Registro de un nuevo usuario
@app.route('/register_user', methods=('GET', 'POST'))
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                         (username, email, password_hash))
            conn.commit()
            flash(gettext('You have successfully registered!'), 'success')
        except sqlite3.IntegrityError:
            flash(gettext('A user with this email already exists.'), 'error')
        finally:
            conn.close()
        return redirect(url_for('login_user'))

    return render_template('register_user.html')

# Логин пользователя
# EN: User login
# FR: Connexion utilisateur
# ES: Inicio de sesión de usuario
@app.route('/login', methods=('GET', 'POST'))
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash(gettext('Welcome, %(username)s!', username=user['username']), 'success')
            return redirect(url_for('index'))
        else:
            flash(gettext('Invalid email or password.'), 'error')

    return render_template('login.html')

# Логаут пользователя
# EN: User logout
# FR: Déconnexion utilisateur
# ES: Cierre de sesión del usuario
@app.route('/logout')
@login_required
def logout_user():
    session.pop('user_id', None)
    flash(gettext('You have been logged out.'), 'success')
    return redirect(url_for('login_user'))

# Восстановление пароля
# EN: Password recovery
# FR: Récupération de mot de passe
# ES: Recuperación de contraseña
@app.route('/recover_password', methods=('GET', 'POST'))
def recover_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user:
            new_password = secrets.token_hex(8)
            password_hash = generate_password_hash(new_password)
            conn = get_db_connection()
            conn.execute('UPDATE users SET password_hash = ? WHERE email = ?', (password_hash, email))
            conn.commit()
            conn.close()

            # Отправка письма с новым паролем (пример)
            try:
                server = smtplib.SMTP('smtp.example.com', 587)
                server.starttls()
                server.login('your_email@example.com', 'your_email_password')
                message = gettext('Subject: Password recovery\n\nYour new password is: %(new_password)s') % {'new_password': new_password}
                server.sendmail('your_email@example.com', email, message)
                server.quit()
                flash(gettext('A new password has been sent to your email.'), 'success')
            except Exception as e:
                flash(gettext('Error sending email: %(error)s', error=str(e)), 'error')
        else:
            flash(gettext('No user found with this email.'), 'error')

    return render_template('recover_password.html')

# Страница для регистрации участников
# EN: Participant registration page
# FR: Page d'inscription des participants
# ES: Página de registro de participantes
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']

        conn = get_db_connection()
        conn.execute('INSERT INTO participants (name, contact) VALUES (?, ?)', (name, contact))
        conn.commit()
        conn.close()
        flash(gettext('Participant successfully registered!'), 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

# Главная страница - список всех турниров
# EN: Main page - list of all tournaments
# FR: Page d'accueil - liste de tous les tournois
# ES: Página principal - lista de todos los torneos
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    tournaments = conn.execute('SELECT * FROM tournaments').fetchall()
    conn.close()
    return render_template('index.html', tournaments=tournaments)

# Страница для создания нового матча
# EN: Page for creating a new match
# FR: Page pour créer un nouveau match
# ES: Página para crear un nuevo partido
@app.route('/create_match', methods=('GET', 'POST'))
@login_required
def create_match():
    conn = get_db_connection()
    tournaments = conn.execute('SELECT * FROM tournaments').fetchall()
    participants = conn.execute('SELECT * FROM participants').fetchall()
    conn.close()

    if request.method == 'POST':
        tournament_id = request.form['tournament_id']
        participant1_id = request.form['participant1_id']
        participant2_id = request.form['participant2_id']

        if participant1_id == participant2_id:
            flash(gettext('Participants in a match must be different.'), 'error')
            return render_template('create_match.html', tournaments=tournaments, participants=participants)

        conn = get_db_connection()
        conn.execute('INSERT INTO matches (tournament_id, participant1_id, participant2_id) VALUES (?, ?, ?)',
                     (tournament_id, participant1_id, participant2_id))
        conn.commit()
        conn.close()
        flash(gettext('Match successfully created!'), 'success')
        return redirect(url_for('index'))

    return render_template('create_match.html', tournaments=tournaments, participants=participants)

# Страница для создания нового турнира
# EN: Page for creating a new tournament
# FR: Page pour créer un nouveau tournoi
# ES: Página para crear un nuevo torneo
@app.route('/create_tournament', methods=('GET', 'POST'))
@login_required
def create_tournament():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Считывание данных о турнире
        name = request.form['name']
        description = request.form.get('description', '')
        participants = request.form.get('participants', '').splitlines()  # Получаем участников, каждый на новой строке

        # Логирование введенных имен участников
        logging.debug(f"Получены имена участников: {participants}")

        # Проверка уникальности имен участников в пределах одного турнира
        participant_names = [participant.strip() for participant in participants if participant.strip()]
        unique_participants = set(participant_names)

        # Логирование количества уникальных и всех введенных имен участников
        logging.debug(
            f"Количество уникальных имен участников: {len(unique_participants)}, общее количество имен: {len(participant_names)}")

        if len(unique_participants) != len(participant_names):
            duplicate_names = [name for name in participant_names if participant_names.count(name) > 1]
            flash(f'Ошибка: Найдены дублирующиеся имена участников: {", ".join(set(duplicate_names))}.', 'danger')
            logging.error(f"Найдены дублирующиеся имена участников в турнире '{name}': {participant_names}")
            conn.close()  # Закрываем соединение перед выходом

            # Передаем уже введенные данные обратно в шаблон
            return render_template('create_tournament.html', name=name, description=description,
                                   participants="\n".join(participant_names))

        # Пытаемся вставить новый турнир в базу данных
        try:
            # Вставляем турнир
            cursor.execute('INSERT INTO tournaments (name, description) VALUES (?, ?)', (name, description))
            tournament_id = cursor.lastrowid  # Получаем ID только что созданного турнира

            # Логирование успешной вставки турнира
            logging.info(f"Турнир '{name}' успешно создан с ID: {tournament_id}")

            # Добавление участников в базу данных
            for participant_name in unique_participants:
                try:
                    cursor.execute('''
                        INSERT INTO participants (tournament_id, name)
                        VALUES (?, ?)
                    ''', (tournament_id, participant_name))
                    # Логирование добавления каждого участника
                    logging.info(f"Участник '{participant_name}' успешно добавлен в турнир ID: {tournament_id}")
                except sqlite3.IntegrityError:
                    logging.error(f"Ошибка уникальности при добавлении участника '{participant_name}' в турнир ID={tournament_id}")
                    flash(f'Ошибка: Участник с именем "{participant_name}" уже существует в этом турнире.', 'error')

            conn.commit()
            flash('Турнир успешно создан и участники добавлены!', 'success')

            # Переходим на страницу деталей турнира только в случае успешного создания
            return redirect(url_for('tournament_details', tournament_id=tournament_id))

        except sqlite3.IntegrityError as e:
            # Логирование ошибки вставки турнира или участников
            logging.error(f"Ошибка при создании турнира: {e}")
            flash(f'Ошибка при создании турнира: {str(e)}', 'error')

        except Exception as e:
            # Логирование других ошибок
            logging.error(f"Непредвиденная ошибка: {e}")
            flash(f'Непредвиденная ошибка: {str(e)}', 'error')

        finally:
            conn.close()  # Закрываем соединение в блоке finally

    # Отправляем пустую форму для создания турнира
    return render_template('create_tournament.html', name="", description="", participants="")



# Функция для создания прямой турнирной сетки
# EN: Function for creating a single elimination tournament bracket
# FR: Fonction pour créer un tableau de tournoi à élimination directe
# ES: Función para crear un cuadro de torneo de eliminación directa
def create_single_elimination_bracket(tournament_id):
    """
    Создаёт турнирную сетку по системе single elimination.
    """
    logging.debug(f'Начинаем создание турнирной сетки для турнира ID={tournament_id}')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Получаем всех участников турнира
        participants = cursor.execute('''
            SELECT id, name FROM participants
            WHERE tournament_id = ?
        ''', (tournament_id,)).fetchall()
        logging.debug(f'Участники турнира ID={tournament_id} успешно получены. Количество участников: {len(participants)}')

        # Формируем список ID и словарь имен участников
        participant_ids = [participant['id'] for participant in participants]
        participant_names = {participant['id']: participant['name'] for participant in participants}

        # Перемешиваем участников случайным образом
        random.shuffle(participant_ids)

        # Проверяем степень двойки, чтобы определить необходимость play-in матчей
        total_participants = len(participant_ids)
        next_power_of_two = 1
        while next_power_of_two < total_participants:
            next_power_of_two *= 2

        stage = 0  # Инициализируем stage для play-in этапов
        if total_participants < next_power_of_two:
            required_matches = next_power_of_two - total_participants
            logging.debug(f'Добавляем play-in матчи: требуется дополнительных матчей: {required_matches}')

            for _ in range(required_matches):
                if len(participant_ids) >= 2:
                    participant1_id = participant_ids.pop()
                    participant2_id = participant_ids.pop()

                    # Создаём play-in матч
                    try:
                        cursor.execute('''
                            INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id)
                            VALUES (?, ?, ?, ?)
                        ''', (tournament_id, stage, participant1_id, participant2_id))
                        conn.commit()
                        logging.debug(f'Добавляем в базу play-in матч: stage={stage}, ID1={participant1_id}, ID2={participant2_id}, в tournament_id={tournament_id}. Оставшиеся участники: {participant_ids}')

                        matches_info = cursor.execute("SELECT * FROM matches").fetchall()
                        formatted_matches = [dict(row) for row in matches_info]  # Преобразование в словарь
                        logging.debug(f'Состояние таблицы matches: {formatted_matches}')

                    except sqlite3.Error as e:
                        logging.error(f'Ошибка при добавлении play-in матча в базу: {e}')
                        conn.close()
                        return

        # Проверяем завершение всех play-in матчей перед созданием основного этапа
        incomplete_play_in_matches = cursor.execute('''
            SELECT id FROM matches
            WHERE tournament_id = ? AND stage = 0 AND result IS NULL
        ''', (tournament_id,)).fetchall()

        if incomplete_play_in_matches:
            logging.debug(f'Матчи play-in не завершены для турнира ID={tournament_id}.')
            conn.close()
            return

        # Переходим к основному этапу
        stage += 1  # Увеличиваем stage для основного этапа
        for i in range(0, len(participant_ids), 2):
            if i + 1 < len(participant_ids):
                participant1_id = participant_ids[i]
                participant2_id = participant_ids[i + 1]

                # Создаём матч
                try:
                    cursor.execute('''
                        INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id)
                        VALUES (?, ?, ?, ?)
                    ''', (tournament_id, stage, participant1_id, participant2_id))
                    conn.commit()
                    logging.debug(f'Добавляем в базу матч: stage={stage}, ID1={participant1_id}, ID2={participant2_id}, в tournament_id={tournament_id}')
                except sqlite3.Error as e:
                    logging.error(f'Ошибка при добавлении матча: {e}')
                    conn.close()
                    return
            else:
                # Обработка участника без пары
                participant1_id = participant_ids[i]
                participant_name = participant_names[participant1_id]

                try:
                    cursor.execute('''
                        INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id, result, result_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (tournament_id, stage, participant1_id, -1, participant_name, participant1_id))
                    conn.commit()
                    logging.debug(f'Участник {participant_name} (ID={participant1_id}) проходит автоматически.')
                except sqlite3.Error as e:
                    logging.error(f'Ошибка при автопрохождении участника: {e}')
                    conn.close()
                    return

        # Сохраняем изменения
        conn.commit()
        logging.debug(f'Турнирная сетка для турнира ID={tournament_id} успешно создана.')

    except Exception as e:
        logging.error(f'Ошибка при создании турнирной сетки: {e}')

    finally:
        conn.close()


# Маршрут для создания турнирной сетки
# EN: Route for creating a tournament bracket
# FR: Route pour créer un tableau de tournoi
# ES: Ruta para crear un cuadro de torneo
@app.route('/create_bracket/<int:tournament_id>', methods=['POST'])
@login_required
def create_bracket(tournament_id):
    try:
        logging.debug(f'Вызов создания турнирной сетки для турнира ID={tournament_id}')
        # Вызов функции для создания прямой турнирной сетки
        create_single_elimination_bracket(tournament_id)
        flash('Турнирная сетка успешно создана!', 'success')
    except Exception as e:
        logging.error(f'Ошибка при создании турнирной сетки для турнира ID={tournament_id}: {e}')
        flash(gettext('Error creating bracket: ') + str(e), 'error')
    return redirect(url_for('index'))


@app.route('/tournament/<int:tournament_id>/bracket', methods=['GET'])
@login_required
def tournament_bracket(tournament_id):
    logging.info(f'Начинаем загрузку турнирной сетки для турнира ID={tournament_id}')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем информацию о турнире
    tournament = cursor.execute('''
        SELECT * FROM tournaments
        WHERE id = ?
    ''', (tournament_id,)).fetchone()

    if tournament is None:
        flash('Ошибка: Турнир не найден.', 'error')
        return redirect(url_for('index'))

    # Получаем все матчи данного турнира вместе с именами участников
    matches = cursor.execute('''
        SELECT matches.id, matches.stage, matches.result, matches.result_id, matches.tournament_id,
               matches.participant1_id, matches.participant2_id,
               COALESCE(p1.name, 'Автоматический проход') AS participant1_name,
               COALESCE(p2.name, 'Нет участника') AS participant2_name
        FROM matches
        LEFT JOIN participants p1 ON matches.participant1_id = p1.id
        LEFT JOIN participants p2 ON matches.participant2_id = p2.id
        WHERE matches.tournament_id = ?
        ORDER BY matches.stage
    ''', (tournament_id,)).fetchall()

    # Логирование для отладки, проверяем, сколько матчей получено
    logging.debug(f'Получено {len(matches)} матчей для турнира ID={tournament_id}')

    # Преобразуем список матчей в структуру, организованную по стадиям
    stages = {}
    for match in matches:
        logging.debug(f"Матч ID={match['id']}, участники: {match['participant1_name']} против {match['participant2_name']}, результат: {match['result']}, result_id: {match['result_id']}")
        # Проверяем корректность данных матчей
        if match['participant1_id'] is None and match['participant2_id'] is None:
            logging.error(f"Найдены некорректные данные матча: ID={match['id']}")
            continue

        # Логирование случаев, когда один из участников отсутствует
        if match['participant2_id'] is None:
            logging.warning(f"Матч ID={match['id']} имеет только одного участника (ID={match['participant1_id']})")

        # Логирование информации о матче
        logging.debug(f"Матч ID={match['id']}, participant1_id={match['participant1_id']}, participant2_id={match['participant2_id']}")

        # Используем -1 для отсутствующих участников, вместо "error_id1" и "error_id2"
        participant1_id = match['participant1_id'] if match['participant1_id'] is not None else -1
        participant2_id = match['participant2_id'] if match['participant2_id'] is not None else -1

        participant1_name = match['participant1_name']
        participant2_name = match['participant2_name']

        stage = match['stage']
        if stage not in stages:
            stages[stage] = []
        stages[stage].append({
            'id': match['id'],
            'participant1_name': participant1_name,
            'participant2_name': participant2_name,
            'participant1_id': participant1_id,
            'participant2_id': participant2_id,
            'result': match['result'],
            'result_id': match['result_id']
        })

        # Логирование данных о текущем матче и его стадии
        logging.debug(f"Матч ID={match['id']} на стадии {stage}: {participant1_name} против {participant2_name}, результат: {match['result']}")

    conn.close()

    logging.info(f'Турнирная сетка для турнира ID={tournament_id} успешно загружена и передана в шаблон')
    print(f'--- Турнирная сетка для турнира ID={tournament_id} успешно загружена и передана в шаблон ---')
    for match in matches:
        print(
            f"Match ID: {match['id']}, Stage: {match['stage']}, Participant1: {match['participant1_name']}, Participant2: {match['participant2_name']}, result: {match['result']}, result_id: {match['result_id']}")
    # Передаем стадии и tournament_id в шаблон
    return render_template('tournament_bracket.html', stages=stages, tournament_id=tournament_id, tournament=tournament)

@app.route('/set_final_winner', methods=['POST'])
@login_required
def set_final_winner():
    try:
        tournament_id = request.form['tournament_id']
        winner_id = request.form['winner_id']
        winner_name = request.form['winner_name']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Обновляем запись о турнире с ID и именем победителя
        cursor.execute('''
            UPDATE tournaments
            SET winner_id = ?, winner_name = ?
            WHERE id = ?
        ''', (winner_id, winner_name, tournament_id))
        conn.commit()

        logging.info(f'Турнир ID={tournament_id} завершен, победитель: {winner_name}, ID {winner_id}')
        flash(f'Турнир завершен! Победитель: {winner_name}, ID {winner_id}.', 'success')

    except Exception as e:
        logging.error(f'Ошибка при определении победителя турнира ID={tournament_id}: {str(e)}')
        return "Ошибка на сервере", 500

    finally:
        conn.close()

    return redirect(url_for('tournament_bracket', tournament_id=tournament_id))


@app.route('/tournament_details/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def tournament_details(tournament_id):
    logging.info(f'Загружаем турнирную сетку для турнира ID={tournament_id}')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем участников турнира
    participants = cursor.execute('''
        SELECT name FROM participants
        WHERE tournament_id = ?
    ''', (tournament_id,)).fetchall()
    conn.close()

    num_participants = len(participants)
    default_match_duration = 2  # Время одного матча по умолчанию - 2 минуты

    if request.method == 'POST':
        match_duration = int(request.form.get('match_duration', default_match_duration))
        tournament_type = request.form['tournament_type']

        # Обновляем тип турнира в базе данных
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE tournaments
                SET type = ?
                WHERE id = ?
            ''', (tournament_type, tournament_id))
            conn.commit()
            logging.info(f'Тип турнира для турнира ID={tournament_id} успешно обновлен на {tournament_type}')
        except Exception as e:
            logging.error(f'Ошибка при обновлении типа турнира для турнира ID={tournament_id}: {e}')
        finally:
            conn.close()

        # Создаем турнирную сетку
        if tournament_type == 'single':
            logging.info(f'Создаем прямую сетку (Single Elimination) для турнира ID={tournament_id}')
            create_single_elimination_bracket(tournament_id)
        elif tournament_type == 'double':
            logging.info(f'Создаем обратную сетку (Double Elimination) для турнира ID={tournament_id}')
            create_double_elimination_bracket(tournament_id)

        flash('Турнирная сетка успешно создана!', 'success')
        return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

    # Рассчитываем время для проведения турнира
    total_time = (num_participants - 1) * default_match_duration

    try:
        logging.debug(f'Получено {len(participants)} участников для турнира ID={tournament_id}')
    except Exception as e:
        logging.error(f'Ошибка при получении участников для турнира ID={tournament_id}: {e}')

    return render_template(
        'tournament_details.html',
        participants=participants,
        num_participants=num_participants,
        total_time=total_time,
        default_match_duration=default_match_duration,
        tournament_id=tournament_id  # Передаем tournament_id в шаблон
    )

@app.route('/set_winner', methods=['POST'])
@login_required
def set_winner():
    match_id = request.form.get('match_id')
    winner_name = request.form.get('winner_name')
    winner_id = request.form.get('winner_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем имя победителя по его ID
        winner_query = '''
            SELECT name FROM participants WHERE id = ?
        '''
        winner = cursor.execute(winner_query, (winner_id,)).fetchone()

        if winner:
            winner_name = winner['name']

            # Обновляем матч с установкой имени победителя
            update_query = '''
                UPDATE matches
                SET result = ?, result_id = ?
                WHERE id = ?
            '''
            cursor.execute(update_query, (winner_name, winner_id, match_id))
            logging.debug(f'Победитель для матча ID={match_id} успешно сохранен в базе данных: победитель {winner_name}, ID={winner_id}')

        conn.commit()

    except Exception as e:
        logging.error(f'Ошибка при установке победителя для матча ID={match_id}: {str(e)}')
        return "Ошибка на сервере", 500

    finally:
        conn.close()

    return jsonify({"status": "success"})


@app.route('/update_match_result/<int:match_id>', methods=['POST'])
@login_required
def update_match_result(match_id):
    result = request.form['result']  # Получаем результат (имя победителя)
    tournament_id = request.form['tournament_id']  # Получаем ID турнира из формы

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Находим ID участника по его имени
        participant_query = '''
            SELECT id FROM participants WHERE name = ?
        '''
        participant_result = cursor.execute(participant_query, (result,)).fetchone()

        if participant_result is None:
            flash(f'Ошибка: Участник с именем {result} не найден.', 'error')
            logging.error(f'Ошибка: Участник с именем {result} не найден.')
            conn.close()
            return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

        result_id = participant_result['id']

        # Обновляем результат матча, включая имя победителя и его ID
        cursor.execute('''
            UPDATE matches SET result = ?, result_id = ?
            WHERE id = ?
        ''', (result, result_id, match_id))
        conn.commit()
        flash('Результат матча успешно обновлён!', 'success')
        logging.debug(f'Обновлён результат матча ID={match_id}: победитель={result} (ID={result_id})')
    except sqlite3.Error as e:
        flash(f'Ошибка при обновлении результата: {str(e)}', 'error')
        logging.error(f'Ошибка при обновлении результата матча ID={match_id}: {e}')
    finally:
        conn.close()

    return redirect(url_for('tournament_bracket', tournament_id=tournament_id))



@app.route('/participants')
@login_required
def participants():
    conn = get_db_connection()
    cursor = conn.cursor()
    participants = cursor.execute('SELECT * FROM participants').fetchall()
    conn.close()
    return render_template('participants.html', participants=participants)


@app.route('/delete_tournament/<int:tournament_id>', methods=['POST'])
@login_required
def delete_tournament(tournament_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаление участников, связанных с турниром
        cursor.execute('DELETE FROM participants WHERE tournament_id = ?', (tournament_id,))

        # Удаление матчей, связанных с турниром
        cursor.execute('DELETE FROM matches WHERE tournament_id = ?', (tournament_id,))

        # Удаление самого турнира
        cursor.execute('DELETE FROM tournaments WHERE id = ?', (tournament_id,))

        conn.commit()
        flash('Турнир успешно удален!', 'success')
    except sqlite3.Error as e:
        flash(f'Ошибка при удалении турнира: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/delete_participant/<int:participant_id>', methods=['POST'])
@login_required
def delete_participant(participant_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаление участника
        cursor.execute('DELETE FROM participants WHERE id = ?', (participant_id,))
        conn.commit()
        flash('Участник успешно удалён!', 'success')
    except sqlite3.Error as e:
        flash(f'Ошибка при удалении участника: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('participants'))


@app.route('/delete_all_participants', methods=['POST'])
@login_required
def delete_all_participants():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаление всех участников
        cursor.execute('DELETE FROM participants')
        conn.commit()
        flash('Все участники успешно удалены!', 'success')
    except sqlite3.Error as e:
        flash(f'Ошибка при удалении всех участников: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('participants'))


# Запуск приложения
# EN: Application launch
# FR: Lancement de l'application
# ES: Inicio de la aplicación
if __name__ == '__main__':
    init_db()  # Инициализация базы данных перед запуском приложения
    app.run(debug=True)