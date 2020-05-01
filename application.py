import os

from flask import Flask, session, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import *
from werkzeug.security import check_password_hash, generate_password_hash

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
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="you must provide an username")

        # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                               {"username": request.form.get("username")}).fetchone()

        # Check if username already exist
        if userCheck:
            return render_template("error.html", message="username already exist")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="you must provide a password")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="you must confirm your password")

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="passwords didn't match")

        hash_password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
                   {"username": request.form.get("username"),
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
    return render_template("login.html")


@app.route("/")
@login_required
def index():
    return "Project 1: TODO"


if __name__ == "__main__":
    app.run(debug=True)
