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


@app.route("/")
@login_required
def index():
    """Главная страница, отображающая активы пользователя и его баланс."""
    user_id = session["user_id"]
    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    # Получение всех акций, принадлежащих пользователю
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)

    # Обработка данных акций
    stock_data = []
    grand_total = user_cash
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
    max_shares_data = {}
    for stock in stock_data:
        if stock["price"] > 0:
            max_shares_data[stock["symbol"]] = user_cash // stock["price"]

    return render_template("index.html", stocks=stock_data, cash=user_cash, grand_total=grand_total, max_shares=max_shares_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Авторизация пользователя."""
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


@app.route("/logout")
def logout():
    """Выход пользователя из системы."""
    session.clear()
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Регистрация нового пользователя."""
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Получение информации о стоимости акции."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            flash("Must provide stock symbol.", "error")
            return render_template("quote.html")

        stock = lookup(symbol)
        if stock is None:
            flash("Invalid stock symbol.", "error")
            return render_template("quote.html")

        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")


@app.route("/history", methods=["GET"])
@login_required
def history():
    """Отображение истории транзакций пользователя."""
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT symbol, shares, price FROM transactions WHERE user_id = ?", user_id)
    return render_template("history.html", transactions=transactions)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """
    RU: Добавление денег на счёт пользователя.
    EN: Adding cash to the user's account.
    """
    if request.method == "POST":
        amount = request.form.get("amount")

        if not amount or not amount.isdigit() or int(amount) <= 0:
            flash("Must provide a valid amount.", "error")
            return render_template("add_cash.html")

        user_id = session["user_id"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", int(amount), user_id)

        # Запись транзакции в таблицу transactions
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, "CASH", 0, int(amount))

        flash("Successfully added cash!", "success")
        return redirect("/")
    else:
        return render_template("add_cash.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Покупка акций."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            flash("Must provide stock symbol.", "error")
            return render_template("buy.html")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            flash("Must provide a valid number of shares.", "error")
            return render_template("buy.html")

        stock = lookup(symbol)
        if stock is None:
            flash("Invalid stock symbol.", "error")
            return render_template("buy.html")

        user_id = session["user_id"]
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        total_cost = stock["price"] * int(shares)

        if user_cash < total_cost:
            flash("Cannot afford the requested number of shares.", "error")
            return render_template("buy.html")

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, stock["symbol"], shares, stock["price"])
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)
        flash("Successfully purchased shares!", "success")

        return redirect("/")
    else:
        # При GET запросе показываем форму покупки и вычисляем максимальное количество акций, которые можно купить
        symbol = request.args.get("symbol")
        if symbol:
            stock = lookup(symbol)
            if stock is None:
                flash("Invalid stock symbol.", "error")
                return redirect("/")

            user_id = session["user_id"]
            user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
            max_shares = user_cash // stock["price"]

            return render_template("buy.html", stock=stock, max_shares=max_shares)
        return render_template("buy.html", stock=None, max_shares=None)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            flash("Must provide stock symbol.", "error")
            return redirect("/sell")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            flash("Must provide a valid number of shares.", "error")
            return redirect("/sell")

        user_shares_data = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)
        if len(user_shares_data) == 0 or user_shares_data[0]["total_shares"] < int(shares):
            flash("Not enough shares.", "error")
            return redirect("/sell")

        stock = lookup(symbol)
        if stock is None:
            flash("Invalid stock symbol.", "error")
            return redirect("/sell")

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, stock["symbol"], -int(shares), stock["price"])
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                   stock["price"] * int(shares), user_id)
        flash("Successfully sold shares!", "success")

        return redirect("/")
    else:
        # Получение всех акций, принадлежащих пользователю для отображения в select меню
        stocks = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)
        return render_template("sell.html", stocks=stocks)
