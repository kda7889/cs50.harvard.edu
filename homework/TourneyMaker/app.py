
# Начальная структура проекта с использованием Flask для проведения турниров

# Импортируем необходимые модули
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_babel import Babel, gettext
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import secrets
from functools import wraps
import polib
import pycountry  # Для получения информации о флагах

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


@app.route('/tournament/<int:tournament_id>/next_stage', methods=['POST'])
@login_required
def next_stage(tournament_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем текущую стадию как число
    current_stage_query = '''
        SELECT MAX(stage) AS current_stage
        FROM matches
        WHERE tournament_id = ?
    '''
    current_stage_result = cursor.execute(current_stage_query, (tournament_id,)).fetchone()

    if current_stage_result['current_stage'] is None:
        flash('Ошибка: текущая стадия не найдена.', 'error')
        return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

    # Приводим текущую стадию к числу
    current_stage = int(current_stage_result['current_stage'])

    # Проверяем, что все матчи текущей стадии завершены
    matches_query = '''
        SELECT id, result
        FROM matches
        WHERE tournament_id = ? AND stage = ? AND result IS NULL
    '''
    incomplete_matches = cursor.execute(matches_query, (tournament_id, current_stage)).fetchall()

    if incomplete_matches:
        flash('Ошибка: не все матчи текущей стадии завершены.', 'error')
        return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

    # Получаем всех победителей текущей стадии
    winners_query = '''
        SELECT result
        FROM matches
        WHERE tournament_id = ? AND stage = ? AND result IS NOT NULL
    '''
    winners = [match['result'] for match in cursor.execute(winners_query, (tournament_id, current_stage)).fetchall()]

    # Если количество победителей нечетное, добавляем одного участника автоматически в следующий этап
    auto_advancing_participant = None
    if len(winners) % 2 != 0:
        auto_advancing_participant = winners.pop()
        flash(f'Участник {str(auto_advancing_participant)} автоматически проходит в следующий этап.', 'info')

    # Создаем матчи для следующего этапа
    new_stage = current_stage + 1
    for i in range(0, len(winners), 2):
        participant1 = winners[i]
        participant2 = winners[i + 1]

        # Вставляем новый матч в базу данных
        insert_match_query = '''
            INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(insert_match_query, (tournament_id, new_stage, participant1, participant2))

    # Если участник автоматически проходит в следующий этап, создаем для него матч без пары
    if auto_advancing_participant:
        cursor.execute('''
            INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id, result)
            VALUES (?, ?, ?, NULL, ?)
        ''', (tournament_id, new_stage, auto_advancing_participant, auto_advancing_participant))

    conn.commit()
    conn.close()

    flash('Следующий этап турнира успешно создан!', 'success')
    return redirect(url_for('tournament_bracket', tournament_id=tournament_id))



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
            type TEXT NOT NULL,
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
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id)
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
            stage INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
            FOREIGN KEY (participant1_id) REFERENCES participants (id),
            FOREIGN KEY (participant2_id) REFERENCES participants (id)
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

        # Пытаемся вставить новый турнир в базу данных
        try:
            cursor.execute('INSERT INTO tournaments (name, description) VALUES (?, ?)', (name, description))
            tournament_id = cursor.lastrowid  # Получаем ID только что созданного турнира

            # Добавление участников в базу данных
            for participant_name in participants:
                if participant_name.strip():  # Игнорируем пустые строки
                    cursor.execute('''
                        INSERT INTO participants (tournament_id, name)
                        VALUES (?, ?)
                    ''', (tournament_id, participant_name.strip()))

            conn.commit()
            flash('Турнир успешно создан и участники добавлены!', 'success')

        except sqlite3.IntegrityError as e:
            flash(f'Ошибка при создании турнира: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('tournament_details', tournament_id=tournament_id))

    # Отправляем форму для создания турнира
    return render_template('create_tournament.html')



# Функция для создания прямой турнирной сетки
# EN: Function for creating a single elimination tournament bracket
# FR: Fonction pour créer un tableau de tournoi à élimination directe
# ES: Función para crear un cuadro de torneo de eliminación directa
def create_single_elimination_bracket(tournament_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем всех участников турнира
    # participants = cursor.execute(
    #     'SELECT id FROM participants WHERE id IN (SELECT participant_id FROM tournament_participants WHERE tournament_id = ?)',
    #     (tournament_id,)
    # ).fetchall()
    participants = cursor.execute(
        'SELECT id FROM participants WHERE tournament_id = ?',
        (tournament_id,)
    ).fetchall()

    # Проверяем, что есть хотя бы 2 участника
    if len(participants) < 2:
        flash(gettext('Tournament must have at least two participants.'), 'error')
        return

    # Перемешиваем список участников и создаем матчи
    import random
    random.shuffle(participants)

    # Создание начальных матчей
    for i in range(0, len(participants), 2):
        if i + 1 < len(participants):
            participant1_id = participants[i][0]
            participant2_id = participants[i + 1][0]
            cursor.execute(
                'INSERT INTO matches (tournament_id, participant1_id, participant2_id, stage) VALUES (?, ?, ?, ?)',
                (tournament_id, participant1_id, participant2_id, 'Round 1')
            )
        else:
            # Если нечетное количество участников, один из них сразу переходит в следующий раунд
            participant1_id = participants[i][0]
            cursor.execute(
                'INSERT INTO matches (tournament_id, participant1_id, participant2_id, stage) VALUES (?, ?, ?, ?)',
                (tournament_id, participant1_id, None, 'Round 1')
            )

    conn.commit()
    conn.close()

    flash(gettext('Single elimination bracket created successfully!'), 'success')


def create_double_elimination_bracket(tournament_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем всех участников турнира
    # participants = cursor.execute(
    #     'SELECT id FROM participants WHERE id IN (SELECT participant_id FROM tournament_participants WHERE tournament_id = ?)',
    #     (tournament_id,)
    # ).fetchall()
    participants = cursor.execute(
        'SELECT id FROM participants WHERE tournament_id = ?',
        (tournament_id,)
    ).fetchall()

    # Проверяем, что есть хотя бы 2 участника
    if len(participants) < 2:
        flash(gettext('Tournament must have at least two participants.'), 'error')
        return

    # Перемешиваем список участников и создаем матчи
    import random
    random.shuffle(participants)

    conn.commit()
    conn.close()

    flash(gettext('Double elimination bracket created successfully!'), 'success')

# Маршрут для создания турнирной сетки
# EN: Route for creating a tournament bracket
# FR: Route pour créer un tableau de tournoi
# ES: Ruta para crear un cuadro de torneo
@app.route('/create_bracket/<int:tournament_id>', methods=['POST'])
@login_required
def create_bracket(tournament_id):
    try:
        # Вызов функции для создания прямой турнирной сетки
        create_single_elimination_bracket(tournament_id)
    except Exception as e:
        flash(gettext('Error creating bracket: ') + str(e), 'error')
    return redirect(url_for('index'))

@app.route('/tournament/<int:tournament_id>/bracket', methods=['GET'])
def tournament_bracket(tournament_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем все матчи данного турнира вместе с именами участников
    matches = cursor.execute('''
        SELECT matches.id, matches.stage, matches.result, matches.tournament_id,
               p1.name AS participant1_name, p2.name AS participant2_name
        FROM matches
        LEFT JOIN participants p1 ON matches.participant1_id = p1.id
        LEFT JOIN participants p2 ON matches.participant2_id = p2.id
        WHERE matches.tournament_id = ?
        ORDER BY matches.stage
    ''', (tournament_id,)).fetchall()

    # Преобразуем список sqlite3.Row в список словарей
    matches_dict = [
        {
            'id': match['id'],
            'stage': match['stage'],
            'result': match['result'],
            'tournament_id': match['tournament_id'],
            'participant1_name': match['participant1_name'],
            'participant2_name': match['participant2_name']
        }
        for match in matches
    ]

    conn.close()

    # Передаем преобразованный список словарей в шаблон
    return render_template('tournament_bracket.html', matches=matches_dict, tournament_id=tournament_id)





@app.route('/tournament_details/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def tournament_details(tournament_id):
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

        # Создаем турнирную сетку
        if tournament_type == 'single':
            create_single_elimination_bracket(tournament_id)
        elif tournament_type == 'double':
            # Здесь должна быть функция для создания обратной сетки
            create_double_elimination_bracket(tournament_id)

        flash('Турнирная сетка успешно создана!', 'success')
        return redirect(url_for('tournament_bracket', tournament_id=tournament_id))

    # Рассчитываем время для проведения турнира
    total_time = (num_participants - 1) * default_match_duration

    return render_template(
        'tournament_details.html',
        participants=participants,
        num_participants=num_participants,
        total_time=total_time,
        default_match_duration=default_match_duration,
        tournament_id=tournament_id  # Передаем tournament_id в шаблон
    )


def create_single_elimination_bracket(tournament_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем всех участников данного турнира
    participants = cursor.execute('''
        SELECT id, name FROM participants
        WHERE tournament_id = ?
    ''', (tournament_id,)).fetchall()

    # Список всех участников
    participant_ids = [participant['id'] for participant in participants]

    # Перемешаем участников случайным образом, чтобы создать пары случайным образом
    import random
    random.shuffle(participant_ids)

    # Создаем матчи первого раунда
    for i in range(0, len(participant_ids), 2):
        if i + 1 < len(participant_ids):
            participant1_id = participant_ids[i]
            participant2_id = participant_ids[i + 1]
            # Создаем матч между двумя участниками
            cursor.execute('''
                INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id)
                VALUES (?, ?, ?, ?)
            ''', (tournament_id, 1, participant1_id, participant2_id))
        else:
            # Если остался один участник без пары, он проходит в следующий раунд автоматически
            participant1_id = participant_ids[i]
            cursor.execute('''
                INSERT INTO matches (tournament_id, stage, participant1_id, participant2_id, result)
                VALUES (?, ?, ?, NULL, ?)
            ''', (tournament_id, 1, participant1_id, participant1_id))  # Результат указывает, что он автоматически проходит дальше

    conn.commit()
    conn.close()


@app.route('/update_match_result/<int:match_id>', methods=['POST'])
@login_required
def update_match_result(match_id):
    result = request.form['result']  # Получаем результат (имя победителя)
    tournament_id = request.form['tournament_id']  # Получаем ID турнира из формы

    conn = get_db_connection()
    cursor = conn.cursor()

    # Обновляем результат матча
    try:
        cursor.execute('''
            UPDATE matches SET result = ?
            WHERE id = ?
        ''', (result, match_id))
        conn.commit()
        flash('Результат матча успешно обновлён!', 'success')
    except sqlite3.Error as e:
        flash(f'Ошибка при обновлении результата: {str(e)}', 'error')
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