# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Spendly" — a Flask expense-tracker built as a **teaching scaffold**. Most application files are intentionally incomplete: they contain placeholder routes and stub modules labeled with "Step N" markers, meant to be implemented by a student in sequence. When a route returns a string like `"Add expense — coming in Step 7"` or a module is just a comment describing what to write, that is by design — it is the next exercise, not a bug to silently work around.

## Directory layout (important)

The actual project lives one level down, in a **nested** `expense-tracker/` folder. The outer folder (the working directory) also holds `venv/` and `chat.txt`.

```
expense-tracker/            <- working dir; venv lives here
└── expense-tracker/        <- ACTUAL project root + git repo root
    ├── app.py              <- Flask entry point
    ├── database/db.py      <- placeholder: get_db/init_db/seed_db to be written (Step 1)
    ├── templates/          <- Jinja2 templates extending base.html
    ├── static/css|js/      <- static assets
    └── requirements.txt
```

Because of this nesting, paths are a recurring footgun. Run project commands from inside the nested folder, e.g. `cd expense-tracker && pip install -r requirements.txt`. The git repository is initialized in the nested folder, not the outer one.

## Commands

All commands assume the venv is active and you are in the **nested** `expense-tracker/` folder.

```bash
# Activate venv (created in the OUTER folder) — from the nested project dir:
source ../venv/Scripts/activate    # Git Bash on Windows
# ../venv/Scripts/Activate.ps1     # PowerShell

pip install -r requirements.txt    # Flask, Werkzeug, pytest, pytest-flask

python app.py                      # dev server at http://localhost:5001 (debug=True)

pytest                             # run tests (none exist yet; pytest-flask is installed)
pytest path/to/test_file.py::test_name   # run a single test
```

Note: on this Windows machine `python3` is not available — use `python`.

## Architecture

Standard small Flask app, server-rendered:

- **`app.py`** — single module holding all routes and `app.run()`. Working routes render templates (`landing`, `register`, `login`, `terms`, `privacy`); auth and expense-CRUD routes (`logout`, `profile`, `expenses/add|edit|delete`) are placeholder stubs to be implemented.
- **`database/db.py`** — intended data layer (SQLite). The contract documented in the stub: `get_db()` returns a connection with `row_factory` and foreign keys enabled, `init_db()` does `CREATE TABLE IF NOT EXISTS`, `seed_db()` inserts dev data. The DB file `expense_tracker.db` is gitignored.
- **`templates/`** — all pages extend `base.html`, which defines the Spendly nav/footer chrome and `title`/`head`/`content`/`scripts` blocks. Static assets are referenced via `url_for('static', ...)`.

When implementing a "Step N" feature, wire it into these existing seams (replace the placeholder route body, fill in the documented `db.py` functions) rather than introducing new structure.
