""" Основной файл приложения Flask для торговли акциями.

FR: Ce fichier est la base de l'application Flask permettant l'achat et la vente d'actions.
ES: Este archivo es la base de la aplicación Flask para la compra y venta de acciones.
EN: This file is the core of the Flask app for buying and selling stocks.
"""

from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import apology, login_required, lookup, usd
import sqlite3
from sqlalchemy import case, func

# Конфигурация приложения
app = Flask(__name__)

# Регистрация фильтра usd
app.jinja_env.filters["usd"] = usd

# Не кэшировать ответы, чтобы всегда получать актуальную версию
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Подключение к базе данных
db = SQL("sqlite:///finance.db")

# UNIQUE COMMENT START: ensure_transactions_table function
def ensure_transactions_table():
    """
    RU: Проверка и добавление таблицы transactions, если её нет.
    EN: Check and add the transactions table if it doesn't exist.
    FR: Vérifiez et ajoutez la table des transactions si elle n'existe pas.
    ES: Verifique y agregue la tabla de transacciones si no existe.
    """
    connection = sqlite3.connect("finance.db")
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
    table_exists = cursor.fetchone()
    if not table_exists:
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL,
                transacted DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        connection.commit()
    connection.close()
# UNIQUE COMMENT END: ensure_transactions_table function

# Проверка и добавление таблицы transactions, если её нет
ensure_transactions_table()

# UNIQUE COMMENT START: ensure_transacted_column function
def ensure_transacted_column():
    """
    RU: Проверка и добавление столбца transacted в таблицу transactions, если его нет.
    EN: Check and add the transacted column to the transactions table if it doesn't exist.
    FR: Vérifiez et ajoutez la colonne transacted à la table des transactions si elle n'existe pas.
    ES: Verifique y agregue la columna transacted a la tabla de transacciones si no existe.
    """
    connection = sqlite3.connect("finance.db")
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(transactions)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    if "transacted" not in column_names:
        cursor.execute("ALTER TABLE transactions ADD COLUMN transacted DATETIME")
        connection.commit()
    cursor.execute("UPDATE transactions SET transacted = datetime('now') WHERE transacted IS NULL")
    connection.commit()
    connection.close()
# UNIQUE COMMENT END: ensure_transacted_column function

# Проверка и добавление столбца transacted, если его нет
ensure_transacted_column()

# UNIQUE COMMENT START: index function
@app.route("/")
@login_required
def index():
    """
    RU: Главная страница, отображающая активы пользователя и его баланс.
    EN: The main page displaying user's assets and their balance.
    FR: La page principale affichant les actifs de l'utilisateur et son solde.
    ES: La página principal que muestra los activos del usuario y su saldo.
    """
    user_id = session["user_id"]
    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    # Получение всех акций, принадлежащих пользователю
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)

    # Обработка данных акций
    stock_data = []
    grand_total = user_cash
    max_shares_data = {}
    for stock in stocks:
        stock_info = lookup(stock["symbol"])
        if stock_info is None:
            return apology("stock lookup failed", 400)

        total_value = stock_info["price"] * stock["total_shares"]
        stock_data.append({
            "symbol": stock_info["symbol"],
            "name": stock_info["name"],
            "shares": stock["total_shares"],
            "price": stock_info["price"],
            "total": total_value
        })
        grand_total += total_value

        # Расчет максимального количества акций, которые можно купить для каждой акции
        if stock_info["price"] > 0:
            max_shares_data[stock_info["symbol"]] = user_cash // stock_info["price"]

    return render_template("index.html", stocks=stock_data, cash=user_cash, grand_total=grand_total, max_shares=max_shares_data)
# UNIQUE COMMENT END: index function

# UNIQUE COMMENT START: login function
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    RU: Авторизация пользователя.
    EN: User login.
    FR: Connexion de l'utilisateur.
    ES: Inicio de sesión del usuario.
    """
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")
# UNIQUE COMMENT END: login function

# UNIQUE COMMENT START: logout function
@app.route("/logout")
@login_required
def logout():
    """
    RU: Выход пользователя из системы.
    EN: User logout.
    FR: Déconnexion de l'utilisateur.
    ES: Cierre de sesión del usuario.
    """
    session.clear()
    return redirect("/login")
# UNIQUE COMMENT END: logout function

# UNIQUE COMMENT START: register function
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    RU: Регистрация нового пользователя.
    EN: Register a new user.
    FR: Enregistrer un nouvel utilisateur.
    ES: Registrar un nuevo usuario.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("passwords must match", 400)

        hash_password = generate_password_hash(password)

        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
        except ValueError:
            return apology("username already taken", 400)

        session["user_id"] = new_user_id
        return redirect("/")
    else:
        return render_template("register.html")
# UNIQUE COMMENT END: register function

# UNIQUE COMMENT START: change_password function
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """
    RU: Смена пароля текущего пользователя.
    EN: Change the current user's password.
    FR: Changer le mot de passe de l'utilisateur actuel.
    ES: Cambiar la contraseña del usuario actual.
    """
    if request.method == "POST":
        current_user_id = session["user_id"]
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Проверка, что поля заполнены
        if not old_password:
            return apology("must provide current password", 400)
        elif not new_password:
            return apology("must provide new password", 400)
        elif new_password != confirmation:
            return apology("passwords must match", 400)

        # Получаем информацию о текущем пользователе
        user_data = db.execute("SELECT * FROM users WHERE id = ?", current_user_id)
        if len(user_data) != 1 or not check_password_hash(user_data[0]["hash"], old_password):
            return apology("invalid current password", 400)

        # Генерация хэша для нового пароля
        new_hash_password = generate_password_hash(new_password)

        # Обновляем пароль в базе данных
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash_password, current_user_id)

        flash("Password changed successfully!", "success")
        return redirect("/")
    else:
        return render_template("change_password.html")
# UNIQUE COMMENT END: change_password function


# UNIQUE COMMENT START: quote function
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """
    RU: Получение информации о стоимости акции.
    EN: Get stock quote information.
    FR: Obtenez des informations sur le cours des actions.
    ES: Obtenga información sobre la cotización de las acciones.
    """
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide stock symbol", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")
# UNIQUE COMMENT END: quote function

# UNIQUE COMMENT START: history function
@app.route("/history")
@login_required
def history():
    """
    RU: Отображение истории транзакций пользователя.
    EN: Show history of transactions.
    FR: Affichage de l'historique des transactions.
    ES: Mostrar el historial de transacciones.
    """
    user_id = session["user_id"]

    # Выполнение запроса на получение транзакций
    transactions = db.execute(
        f"SELECT symbol, shares, price, transacted FROM transactions WHERE user_id = {user_id} ORDER BY transacted DESC")


    symbols = [transaction["symbol"] for transaction in transactions]
    unique_symbols = list(set(symbols))

    # Получаем названия акций для всех уникальных символов одним запросом
    symbol_names = {}
    for symbol in unique_symbols:
        stock_info = lookup(symbol)
        if stock_info:
            symbol_names[symbol] = stock_info["name"]
        else:
            symbol_names[symbol] = "Unknown"

    # Формируем окончательные данные для истории транзакций
    enhanced_transactions = []
    for transaction in transactions:
        symbol = transaction["symbol"]
        name = symbol_names.get(symbol, "Unknown")
        transaction_type = "Sell" if transaction["shares"] < 0 else "Buy"
        enhanced_transactions.append({
            "symbol": symbol,
            "name": name,
            "shares": abs(transaction["shares"]),
            "price": transaction["price"],
            "transacted": transaction["transacted"],
            "transaction_type": transaction_type
        })



    return render_template("history.html", transactions=enhanced_transactions)
# UNIQUE COMMENT END: history function





# UNIQUE COMMENT START: add_cash function
@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """
    RU: Добавление денег на счёт пользователя.
    EN: Adding cash to the user's account.
    FR: Ajouter de l'argent au compte de l'utilisateur.
    ES: Añadir dinero a la cuenta del usuario.
    """
    if request.method == "POST":
        amount = request.form.get("amount")

        if not amount or not amount.isdigit() or int(amount) <= 0:
            flash("Must provide a valid amount.", "error")
            return render_template("add_cash.html")

        user_id = session["user_id"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", int(amount), user_id)

        # Запись транзакции в таблицу transactions
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, datetime('now'))", user_id, "CASH", 0, int(amount))

        flash("Successfully added cash!", "success")
        return redirect("/")
    else:
        return render_template("add_cash.html")
# UNIQUE COMMENT END: add_cash function

# UNIQUE COMMENT START: buy function
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """
    RU: Покупка акций.
    EN: Buying stocks.
    FR: Achat d'actions.
    ES: Compra de acciones.
    """
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide stock symbol", 400)

        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("must provide a valid number of shares", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        user_id = session["user_id"]
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        total_cost = stock["price"] * int(shares)

        if user_cash < total_cost:
            return apology("cannot afford the requested number of shares", 400)

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, datetime('now'))",
                   user_id, stock["symbol"], shares, stock["price"])
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)
        flash("Successfully purchased shares!", "success")

        return redirect("/")
    else:
        return render_template("buy.html")
# UNIQUE COMMENT END: buy function

# UNIQUE COMMENT START: sell function
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """
    RU: Продажа акций.
    EN: Selling stocks.
    FR: Vente d'actions.
    ES: Venta de acciones.
    """
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide stock symbol", 400)
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("must provide a valid number of shares", 400)

        user_shares_data = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)
        if len(user_shares_data) == 0 or user_shares_data[0]["total_shares"] < int(shares):
            return apology("not enough shares", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, datetime('now'))",
                   user_id, stock["symbol"], -int(shares), stock["price"])
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                   stock["price"] * int(shares), user_id)
        flash("Successfully sold shares!", "success")

        return redirect("/")
    else:
        stocks = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)
        return render_template("sell.html", stocks=stocks)
# UNIQUE COMMENT END: sell function
