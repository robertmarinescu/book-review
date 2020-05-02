import os

from flask import Flask, session, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import *
from werkzeug.security import check_password_hash, generate_password_hash

import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return render_template("error.html", message="you must provide an username")

        # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                               {"username": username}).fetchone()

        # Check if username already exist
        if userCheck:
            return render_template("error.html", message="username already exist")

        # Ensure password was submitted
        elif not password:
            return render_template("error.html", message="you must provide a password")

        # Ensure confirmation was submitted
        elif not confirmation:
            return render_template("error.html", message="you must confirm your password")

        # Check passwords are equal
        elif not password == confirmation:
            return render_template("error.html", message="passwords didn't match")

        hash_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
                   {"username": username,
                    "password": hash_password})

        db.commit()
        flash('Account successfully created')

        # Redirect user to login page
        return redirect("/login")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login user """

    # Forget any user id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("error.html", message="You have to enter your username")
        elif not password:
            return render_template("error.html", message="You need to enter your password")

        # Query database to check the username exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user_check = rows.fetchone()

        if user_check is None or not check_password_hash(user_check[2], password):
            return render_template("error.html", message="Invalid username or password")

        # Remember users credentials
        session["user_id"] = user_check[0]
        session["user_name"] = user_check[1]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    """ Log out """
    session.clear()
    return redirect("/")


@app.route("/", methods=["GET"])
@login_required
def index():
    """ Display index page"""
    return render_template("index.html")


@app.route("/search", methods=["GET"])
@login_required
def search():
    """ Search for a book """

    book = request.args.get("book")
    if not book:
        return render_template("error.html", message="You must enter a valid book name or id or author")

    query = "%"+book+"%"
    query = query.title()

    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE "
                      "isbn LIKE :query OR title LIKE :query OR author LIKE :query", {"query": query})

    if rows.rowcount == 0:
        return render_template("error.html", message="There is no book with this credentials")

    books = rows.fetchall()
    logging.debug("BOOKS: " + str(books))

    return render_template("books.html", books=books)


if __name__ == "__main__":
    app.run(debug=True)
