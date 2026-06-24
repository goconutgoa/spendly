import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from database.db import get_db, init_db, seed_db, get_user_by_email, create_user

app = Flask(__name__)

# Secret key for session cookies and flash messages. Read from the environment
# in production; the dev fallback keeps local runs working out of the box.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Ensure the database schema and sample data are ready before serving requests.
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")
        if "@" not in email or "." not in email.split("@")[-1]:
            return render_template(
                "register.html", error="Please enter a valid email address."
            )
        if len(password) < 8:
            return render_template(
                "register.html", error="Password must be at least 8 characters."
            )
        if get_user_by_email(email) is not None:
            return render_template(
                "register.html", error="That email is already registered."
            )

        try:
            create_user(name, email, generate_password_hash(password))
        except sqlite3.IntegrityError:
            # Backstop for a race on the UNIQUE email constraint.
            return render_template(
                "register.html", error="That email is already registered."
            )

        flash("Account created — please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
