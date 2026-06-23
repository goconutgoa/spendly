"""Database layer for Spendly (Step 1 — Database Setup).

Provides three functions:
    get_db()   — open a SQLite connection (Row factory + foreign keys on)
    init_db()  — create tables with CREATE TABLE IF NOT EXISTS
    seed_db()  — insert sample data for local development (once)

All SQL uses parameterized queries; no ORM and no string-formatted SQL.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# The DB file lives at the project root next to app.py, regardless of the
# current working directory. database/db.py -> database/ -> project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "expense_tracker.db")

# Fixed category list for expenses (spec §10).
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    """Return a SQLite connection.

    Rows come back as sqlite3.Row (dict-like, accessible by column name) and
    foreign key enforcement is turned on (it is off by default in SQLite).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not already exist. Safe to call repeatedly."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert sample development data once.

    If the users table already holds any rows, returns early so repeated runs
    never duplicate seed data.
    """
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        # 8 expenses covering all 7 categories (Food appears twice), with
        # YYYY-MM-DD dates spread across the current month.
        sample_expenses = [
            (user_id, 38.40, "Food", "Weekly groceries", "2026-06-03"),
            (user_id, 12.00, "Transport", "Metro top-up", "2026-06-05"),
            (user_id, 74.90, "Bills", "Electricity bill", "2026-06-08"),
            (user_id, 25.00, "Health", "Pharmacy", "2026-06-11"),
            (user_id, 18.50, "Entertainment", "Cinema ticket", "2026-06-14"),
            (user_id, 59.99, "Shopping", "New headphones", "2026-06-17"),
            (user_id, 9.20, "Other", "Misc", "2026-06-20"),
            (user_id, 6.75, "Food", "Lunch out", "2026-06-22"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print(f"Initialized and seeded database at {DB_PATH}")
