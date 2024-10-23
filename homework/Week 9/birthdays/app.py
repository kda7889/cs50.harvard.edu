# app.py: Flask-приложение для отслеживания дней рождения друзей
from flask import Flask, render_template, request, redirect
import sqlite3

# Создаем экземпляр Flask приложения
app = Flask(__name__)

# Маршрут для корневой страницы ('/')
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Проверяем, есть ли id, для добавления или обновления записи
        record_id = request.form.get("id")
        name = request.form.get("name")  # Получаем имя из формы
        month = request.form.get("month")  # Получаем месяц из формы
        day = request.form.get("day")  # Получаем день из формы

        # Подключение к базе данных и добавление или обновление записи
        conn = sqlite3.connect("birthdays.db")
        db = conn.cursor()
        if record_id:  # Если есть id, обновляем запись
            db.execute("UPDATE birthdays SET name = ?, month = ?, day = ? WHERE id = ?", (name, month, day, record_id))
        else:  # Иначе добавляем новую запись
            db.execute("INSERT INTO birthdays (name, month, day) VALUES (?, ?, ?)", (name, month, day))
        conn.commit()
        conn.close()

        # Перенаправление обратно на главную страницу через GET-запрос
        return redirect("/")
    else:
        # Обработка GET-запроса: отображение всех дней рождения
        conn = sqlite3.connect("birthdays.db")
        db = conn.cursor()
        db.execute("SELECT * FROM birthdays")  # Запрос всех записей из таблицы birthdays
        birthdays = db.fetchall()  # Извлечение всех данных
        conn.close()

        # Передача данных в шаблон index.html для отображения
        return render_template("index.html", birthdays=birthdays, edit_id=None, edit_birthday=None)

# Маршрут для удаления записи о дне рождения
@app.route("/delete", methods=["POST"])
def delete():
    # Получение идентификатора записи, которую нужно удалить
    id = request.form.get("id")

    # Подключение к базе данных и удаление записи
    conn = sqlite3.connect("birthdays.db")
    db = conn.cursor()
    db.execute("DELETE FROM birthdays WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    # Перенаправление обратно на главную страницу
    return redirect("/")

# Маршрут для редактирования записи о дне рождения
@app.route("/edit", methods=["POST"])
def edit():
    # Получение идентификатора записи, которую нужно отредактировать
    id = request.form.get("id")

    # Подключение к базе данных и получение записи
    conn = sqlite3.connect("birthdays.db")
    db = conn.cursor()
    db.execute("SELECT * FROM birthdays WHERE id = ?", (id,))
    birthday = db.fetchone()  # Извлечение данных записи
    conn.close()

    # Передача данных в шаблон index.html для редактирования
    return render_template("index.html", birthdays=get_all_birthdays(), edit_id=id, edit_birthday=birthday)

# Маршрут для обновления записи о дне рождения
@app.route("/update", methods=["POST"])
def update():
    # Обработка POST-запроса: обновление записи о дне рождения
    id = request.form.get("id")
    name = request.form.get("name")  # Получаем обновленное имя из формы
    month = request.form.get("month")  # Получаем обновленный месяц из формы
    day = request.form.get("day")  # Получаем обновленный день из формы

    # Подключение к базе данных и обновление записи
    conn = sqlite3.connect("birthdays.db")
    db = conn.cursor()
    db.execute("UPDATE birthdays SET name = ?, month = ?, day = ? WHERE id = ?", (name, month, day, id))
    conn.commit()
    conn.close()

    # Перенаправление обратно на главную страницу
    return redirect("/")

# Вспомогательная функция для получения всех записей из базы данных
def get_all_birthdays():
    conn = sqlite3.connect("birthdays.db")
    db = conn.cursor()
    db.execute("SELECT * FROM birthdays")
    birthdays = db.fetchall()
    conn.close()
    return birthdays

# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
