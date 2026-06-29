import functools
import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

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
# Auth helpers                                                        #
# ------------------------------------------------------------------ #

def login_required(view):
    """Gate a view behind a logged-in session.

    Redirects anonymous visitors (no ``user_id`` in the session) to the login
    page with a flash; otherwise calls the wrapped view. ``functools.wraps``
    keeps the view's name so ``url_for`` still resolves it. Reused by every
    protected route from here on.
    """
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # One generic message for every failure mode (empty fields, unknown
        # email, wrong password) so we never reveal which part was wrong.
        if not email or not password:
            return render_template("login.html", error="Invalid email or password.")

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/profile")
@login_required
def profile():
    # Step 4 is UI-first: every value below is hardcoded so the layout can be
    # validated in isolation. Step 5 will replace this with real queries scoped
    # to session["user_id"]. The numbers mirror the seeded demo data.
    user = {
        "name": session.get("user_name", "Demo User"),
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "June 2026",
    }
    summary = {
        "total_spent": "244.74",
        "transaction_count": 8,
        "top_category": "Bills",
    }
    transactions = [
        {"date": "2026-06-22", "description": "Lunch out", "category": "Food", "amount": "6.75"},
        {"date": "2026-06-20", "description": "Misc", "category": "Other", "amount": "9.20"},
        {"date": "2026-06-17", "description": "New headphones", "category": "Shopping", "amount": "59.99"},
        {"date": "2026-06-14", "description": "Cinema ticket", "category": "Entertainment", "amount": "18.50"},
        {"date": "2026-06-11", "description": "Pharmacy", "category": "Health", "amount": "25.00"},
        {"date": "2026-06-08", "description": "Electricity bill", "category": "Bills", "amount": "74.90"},
        {"date": "2026-06-05", "description": "Metro top-up", "category": "Transport", "amount": "12.00"},
        {"date": "2026-06-03", "description": "Weekly groceries", "category": "Food", "amount": "38.40"},
    ]
    categories = [
        {"name": "Bills", "total": "74.90", "pct": 31},
        {"name": "Shopping", "total": "59.99", "pct": 25},
        {"name": "Food", "total": "45.15", "pct": 18},
        {"name": "Health", "total": "25.00", "pct": 10},
        {"name": "Entertainment", "total": "18.50", "pct": 8},
        {"name": "Transport", "total": "12.00", "pct": 5},
        {"name": "Other", "total": "9.20", "pct": 4},
    ]
    return render_template(
        "profile.html",
        user=user,
        summary=summary,
        transactions=transactions,
        categories=categories,
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

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
