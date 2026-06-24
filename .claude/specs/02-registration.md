# Spec: Registration

## Overview

Turn the existing `/register` page into a working sign-up flow. Right now the
route only renders `register.html` on GET; the form already POSTs name, email,
and password back to `/register`, but nothing handles that submission. This step
adds server-side handling: validate the input, hash the password with werkzeug,
insert a new row into the `users` table, and redirect to the login page on
success (re-rendering the form with an error message on failure). It is the
first authentication step in the Spendly roadmap and unblocks Login (Step 3),
which needs real user accounts to authenticate against.

## Depends on

- **Step 1 — Database Setup** (complete). The `users` table
  (`id, name, email UNIQUE, password_hash, created_at`) and the `get_db()`
  helper already exist in `database/db.py`.

## Routes

- `GET /register` — render the empty registration form — **public**
  (already exists; will be extended to also accept POST).
- `POST /register` — validate input, create the user, redirect to `/login` on
  success or re-render `register.html` with an `error` on failure — **public**.

> Implementation note: this is the **same** `register` view function extended to
> `methods=["GET", "POST"]`, not a second route.

## Database changes

No schema changes. The `users` table and its `UNIQUE(email)` constraint already
exist from Step 1. Two thin, parameterised data-layer helpers were **added** to
`database/db.py` (no ORM, reusing `get_db()`):

- `get_user_by_email(email)` → returns the `sqlite3.Row` or `None` (duplicate
  check now; reused by Step 3 Login).
- `create_user(name, email, password_hash)` → inserts the row and returns
  `lastrowid`; raises `sqlite3.IntegrityError` on a duplicate email.

## Templates

- **Create:** none.
- **Modify:** `templates/base.html` — added a central
  `get_flashed_messages(with_categories=true)` block above `{% block content %}`
  so flashed messages render on every page (the registration success banner
  surfaces on `/login` with no edit to `login.html`).
- `templates/register.html` — **unchanged**; it already has the POST form
  (`name`, `email`, `password`) and the `{% if error %}` block used for
  validation messages.

## Files to change

- `app.py` — extend the `register` view to `methods=["GET", "POST"]`: read +
  normalise form fields, validate, hash with `generate_password_hash`, create
  the user via `create_user()`, then `flash(...)` + `redirect(url_for("login"))`
  on success or re-render with `error` on failure. Added imports `request,
  redirect, url_for, flash` (Flask), `generate_password_hash`
  (`werkzeug.security`), `os`, `sqlite3`, and `get_user_by_email, create_user`
  (`database.db`). Set `app.secret_key = os.environ.get("SECRET_KEY",
  "dev-secret-change-me")` — required for `flash`/sessions, env-driven with a
  dev fallback.
- `database/db.py` — add `get_user_by_email` and `create_user` (see above).
- `templates/base.html` — add the flash-rendering block (see above).
- `static/css/style.css` — add `.flash`, `.flash-success`
  (`var(--accent-light)` / `var(--accent)`) and `.flash-error`
  (`var(--danger-light)` / `var(--danger)`); CSS variables only, no hardcoded
  hex.

## Files to create

- None.

## New dependencies

No new dependencies. `werkzeug.security.generate_password_hash` ships with
Werkzeug, which is already installed.

## Rules for implementation

- No SQLAlchemy or ORMs — use `sqlite3` via the existing `get_db()` helper.
- Parameterised queries only — never string-format values into SQL.
- Passwords hashed with werkzeug (`generate_password_hash`) — never store
  plaintext.
- Use CSS variables — never hardcode hex values (no styling work is expected,
  but honour this if any is added).
- All templates extend `base.html` (`register.html` already does).
- Validate before inserting: name/email/password non-empty, email contains
  `@`, password at least 8 characters (the form placeholder promises this).
- Handle the duplicate-email case gracefully: either pre-check with a `SELECT`
  or catch `sqlite3.IntegrityError` and re-render with a friendly error rather
  than letting the app 500.
- Normalise email (strip + lowercase) before storing and checking.
- Always `conn.close()` the connection (use try/finally to match `db.py` style).
- On success, redirect (PRG pattern) to `login` — do not render a page directly
  from the POST.

## Definition of done

- [ ] Visiting `/register` shows the form (GET still works).
- [ ] Submitting valid new details creates exactly one row in `users` with a
      hashed (non-plaintext) `password_hash`, then redirects to `/login`.
- [ ] Submitting an email that already exists (e.g. `demo@spendly.com`) re-renders
      the form with a visible error and does **not** create a duplicate row.
- [ ] Submitting empty fields, a malformed email, or a password under 8
      characters re-renders the form with a visible error and creates no row.
- [ ] The stored `password_hash` verifies against the entered password with
      `check_password_hash` (confirming werkzeug hashing was used).
- [ ] App starts and the flow works end-to-end with `python app.py` at
      `http://localhost:5001`.
