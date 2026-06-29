"""Pure query helpers for the profile page (Step 5 — Backend Connection).

No Flask imports. Each function opens its own connection via ``get_db()`` and
closes it before returning. Parameterised queries only — never string-format
values into SQL.
"""

from datetime import datetime

from database.db import get_db


def _format_member_since(created_at):
    """Format a stored 'YYYY-MM-DD HH:MM:SS' timestamp as 'Month YYYY'."""
    # created_at is written by SQLite's datetime('now') => 'YYYY-MM-DD HH:MM:SS'.
    dt = datetime.strptime(created_at[:10], "%Y-%m-%d")
    return dt.strftime("%B %Y")


def get_user_by_id(user_id):
    """Return dict with ``name``, ``email``, ``member_since`` — or None if missing."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": _format_member_since(row["created_at"]),
    }


# ===================================================================== #
# SUBAGENT 2 — SUMMARY STATS                                            #
# Implement get_summary_stats below. Replace the NotImplementedError.   #
# Contract: return dict with numeric ``total_spent``, int               #
# ``transaction_count``, str ``top_category``. When the user has no     #
# expenses return {"total_spent": 0, "transaction_count": 0,            #
# "top_category": "—"}.                                                 #
# ===================================================================== #
def get_summary_stats(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total_spent, "
            "COUNT(*) AS transaction_count "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        top = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? "
            "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()
    return {
        "total_spent": float(row["total_spent"]),
        "transaction_count": int(row["transaction_count"]),
        "top_category": top["category"] if top is not None else "—",
    }


# ===================================================================== #
# SUBAGENT 1 — TRANSACTION HISTORY                                      #
# Implement get_recent_transactions below. Replace the                  #
# NotImplementedError. Contract: list of dicts (newest date first),     #
# each with ``date``, ``description``, ``category``, numeric ``amount``.#
# Empty list when the user has no expenses.                             #
# ===================================================================== #
def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in rows
    ]


# ===================================================================== #
# SUBAGENT 3 — CATEGORY BREAKDOWN                                       #
# Implement get_category_breakdown below. Replace the                   #
# NotImplementedError. Contract: list of dicts ordered by ``amount``    #
# desc, each with ``name``, numeric ``amount``, int ``pct``. The pct    #
# values must sum to exactly 100 (largest category absorbs the rounding #
# remainder). Empty list when the user has no expenses.                 #
# ===================================================================== #
def get_category_breakdown(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS amount FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    total = sum(row["amount"] for row in rows)
    breakdown = [
        {
            "name": row["category"],
            "amount": float(row["amount"]),
            "pct": round(row["amount"] / total * 100),
        }
        for row in rows
    ]

    remainder = 100 - sum(item["pct"] for item in breakdown)
    breakdown[0]["pct"] += remainder

    return breakdown
