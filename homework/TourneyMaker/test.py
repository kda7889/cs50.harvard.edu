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

# Инициализация приложения Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


# Функция для выбора локали
def get_locale():
    # Сначала проверяем, есть ли язык, сохраненный в сессии
    if 'lang' in session:
        return session['lang']
    # Если нет, используем заголовок из браузера
    return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])

# Инициализация Babel для поддержки мультиязычности
babel = Babel()
babel.init_app(app, locale_selector=get_locale)

# Путь к папке с переводами
TRANSLATIONS_PATH = 'translations'

# Конфигурация локализации

# Декоратор для проверки авторизации пользователя
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему для доступа к этой странице.', 'warning')
            return redirect(url_for('login_user'))
        return f(*args, **kwargs)
    return decorated_function

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
    if os.path.exists(TRANSLATIONS_PATH):
        for root, dirs, files in os.walk(TRANSLATIONS_PATH):
            for file in files:
                if file.endswith('.po'):
                    lang_code = os.path.basename(root)
                    language_name = get_language_name_from_po_file(os.path.join(root, file))
                    if language_name:
                        languages[lang_code] = language_name
    return languages

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('tournament.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для создания базы данных и необходимых таблиц, если они не существуют
def init_db():
    conn = sqlite3.connect('tournament.db')
    cursor = conn.cursor()
    # Проверка и создание таблицы турниров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)
    # Проверка и создание таблицы участников
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT
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

# Маршрут для изменения языка
@app.route('/set_language/<language>')
def set_language(language):
    if language in app.config['SUPPORTED_LANGUAGES']:
        session['lang'] = language
    return redirect(request.referrer or url_for('index'))

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

# Маршрут для страницы регистрации участников
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        with get_db_connection() as conn:
            conn.execute('INSERT INTO participants (name, contact) VALUES (?, ?)', (name, contact))
            conn.commit()
        flash('Участник успешно зарегистрирован!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

# Маршрут для главной страницы
@app.route('/')
def index():
    conn = get_db_connection()
    tournaments = conn.execute('SELECT * FROM tournaments').fetchall()
    conn.close()
    return render_template('index.html', tournaments=tournaments)

# Маршрут для страницы регистрации пользователя
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, hashed_password))
                conn.commit()
                flash('Регистрация прошла успешно, войдите в систему.', 'success')
                return redirect(url_for('login_user'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким email уже существует.', 'danger')
    return render_template('register_user.html')

# Маршрут для страницы входа пользователя
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                flash('Вы успешно вошли в систему.', 'success')
                return redirect(url_for('index'))
            flash('Неверные учетные данные.', 'danger')
    return render_template('login.html')

# Маршрут для выхода пользователя
@app.route('/logout')
@login_required
def logout_user():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

# Маршрут для создания нового матча
@app.route('/create_match', methods=['GET', 'POST'])
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
            flash('Участники матча должны быть разными.', 'error')
            return render_template('create_match.html', tournaments=tournaments, participants=participants)

        with get_db_connection() as conn:
            conn.execute('INSERT INTO matches (tournament_id, participant1_id, participant2_id) VALUES (?, ?, ?)',
                         (tournament_id, participant1_id, participant2_id))
            conn.commit()
        flash('Матч успешно создан!', 'success')
        return redirect(url_for('index'))

    return render_template('create_match.html', tournaments=tournaments, participants=participants)

# Маршрут для создания нового турнира
@app.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        with get_db_connection() as conn:
            conn.execute('INSERT INTO tournaments (name, type) VALUES (?, ?)', (name, type))
            conn.commit()
        flash('Турнир успешно создан!', 'success')
        return redirect(url_for('index'))
    return render_template('create_tournament.html')

# Запуск приложения
if __name__ == '__main__':
    init_db()  # Инициализация базы данных перед запуском приложения
    app.config['SUPPORTED_LANGUAGES'] = get_supported_languages()
    app.run(debug=True)
