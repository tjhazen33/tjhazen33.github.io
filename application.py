import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached --- Style 50 made me put two \n here


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Store the users current cash and make it accesible, while also adding the users cash to variable that will hold total value
    current_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
    cash1 = current_cash[0]
    cash2 = int(cash1["cash"])
    cash_plus_stocks = cash2

    # store the stocks and amount the user owns in rows, then iterate through those stocks and add their current price and total value
    rows = db.execute("SELECT stock, SUM(amount) FROM transactions WHERE id = :id GROUP BY stock", id=session["user_id"])
    for row in rows:
        stock_info = lookup(row["stock"])
        price = stock_info["price"]
        amount = row["SUM(amount)"]
        value = price * amount
        cash_plus_stocks = cash_plus_stocks + value
        row.update({"price": price})
        row.update({"value": value})
    return render_template("index.html", cash2=cash2, rows=rows, cash_plus_stocks=cash_plus_stocks)

@app.route("/googleea873698a8500dea.html")
def googleea873698a8500dea():
    """Show portfolio of stocks"""
    return render_template("googleea873698a8500dea.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide a stock symbol", 400)

        else:
            # make a dict with stock info, make sure then stock is valid
            stock_info = lookup(request.form.get("symbol"))

            if not stock_info:
                return apology("stock not valid", 400)

            # Ensure sufficient funds and that share was submitted as a positive int
            shares = request.form.get("shares")
            current_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
            current_cash_int = current_cash[0]
            stockprice = int(stock_info["price"])
            if not shares:
                return apology("Please provide a number of shares to purchase", 400)
            if not shares.isdigit():
                return apology("Please provide a digit number of shares", 400)
            shareint = int(shares)
            if shareint < 0:
                return apology("Please provide a positive number of shares", 400)
            if current_cash_int['cash'] < stockprice * shareint:
                return apology("insufficient funds", 400)

            # insert into database table transactions the transaction info
            else:
                insert = db.execute("INSERT INTO transactions (id, stock, amount, price) VALUES(:id, :stock, :amount, :price)",
                                    id=session["user_id"], stock=request.form.get("symbol"), amount=request.form.get("shares"), price=stock_info["price"])
                update = db.execute("UPDATE users SET cash = cash - :shares * :price WHERE id = :id",
                                    shares=shareint, price=stock_info["price"], id=session["user_id"])
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Query database for inputted username, and return jsonify(False) if username exists and jsonify(True) if username available
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.args.get("username"))
    if rows:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # store in rows the transaction information and update rows with whether bought or sold and making amount bought/sold a positive value
    rows = db.execute("SELECT * FROM transactions WHERE id = :id", id=session["user_id"])
    for row in rows:
        if row["amount"] > 0:
            row.update({"bought_or_sold": "Bought"})
        else:
            row.update({"bought_or_sold": "Sold"})
        row["amount"] = abs(row["amount"])
    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide an email", 400)

        # make a dict with quote info
        else:
            quote = lookup(request.form.get("symbol"))

            # confirm quote exists
            if not quote:
                return apology("stock not valid", 400)

            # If valid input, return page with quote information
            return render_template("quoted.html", quote=quote)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # store in rows user database username that matches the submitted form for username to confirm new username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must retype password", 400)

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Passwords do not match", 400)

        # Ensure username is not taken
        elif rows:
            return apology("username taken", 400)

        # If valid input, hash password and update databse with user info then redirect to homepage
        else:
            passwordhash = generate_password_hash(request.form.get("password"))
            insert = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                                username=request.form.get("username"), hash=passwordhash)
            session["user id"] = insert
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide a stock symbol", 403)

        # make a dict with stock info and make variables for checks below including users cash, the stock information and shares to sell
        else:
            rows = db.execute("SELECT stock, SUM(amount) FROM transactions WHERE id = :id GROUP BY stock", id=session["user_id"])
            stock_info = lookup(request.form.get("symbol"))
            current_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
            cash1 = current_cash[0]
            cash2 = int(cash1["cash"])
            price = int(stock_info["price"])
            shares = request.form.get("shares")

            # Confirming shares input is an integer and that the user owns as many stocks as they want to sell
            if not shares.isdigit():
                return apology("Please provide a digit number of shares", 400)
            shareint = int(shares)
            stockprice = int(stock_info["price"])
            for row in rows:
                amount = row["SUM(amount)"]
                if stock_info["symbol"].upper() == row["stock"].upper():
                    if shareint > amount:
                        return apology("You don't have that many stocks to sell", 400)

            # Ensure shares field was filled with a positive int, and that a valid stock was provided
            if not shares:
                return apology("Please provide a number of shares to purchase", 400)
            if shareint <= 0:
                return apology("Please provide a positive number of shares", 400)
            if not stock_info:
                return apology("stock not valid", 400)

            # updating transactions with transaction information and updating the users cash after the transaction
            else:
                insert = db.execute("INSERT INTO transactions (id, stock, amount, price) VALUES(:id, :stock, :amount, :price)",
                                    id=session["user_id"], stock=request.form.get("symbol"), amount=(0 - shareint), price=stock_info["price"])
                update = db.execute("UPDATE users SET cash = cash + :shares * :price WHERE id = :id",
                                    shares=shareint, price=price, id=session["user_id"])
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        rows = db.execute("SELECT stock, SUM(amount) FROM transactions WHERE id = :id GROUP BY stock", id=session["user_id"])
        return render_template("sell.html", rows=rows)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
