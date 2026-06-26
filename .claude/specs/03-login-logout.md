# Spec: Login and Logout

## Overview

Turn the existing `/login` page into a working sign-in flow and implement the
`/logout` placeholder. Right now `/login` only renders `login.html` on GET; the
form already POSTs `email` and `password` back to `/login`, but nothing handles
that submission, and `/logout` returns a "coming in Step 3" stub. This step adds
server-side authentication: look the user up by email, verify the submitted
password against the stored werkzeug hash, and on success establish a session
(`session["user_id"]`, `session["user_name"]`) and redirect; on failure re-render
the form with an error. `/logout` clears the session and redirects to the
landing page. The shared nav in `base.html` becomes auth-aware so signed-in
users see their name and a "Sign out" link instead of "Sign in / Get started".
This is the second authentication step in the Spendly roadmap: it depends on real
accounts from Registration (Step 2) and unblocks Profile (Step 4) and all
expense-CRUD steps, which need a logged-in user to scope data to.

## Depends on

- **Step 1 — Database Setup** (complete). `users` table and `get_db()` exist.
- **Step 2 — Registration** (complete). Provides real accounts to authenticate
  against, the `get_user_by_email(email)` data-layer helper (reused as-is here),
  and the central `flash` block already wired into `base.html`. The seeded
  `demo@spendly.com` / `demo123` account is a ready test login.

## Routes

- `GET /login` — render the empty sign-in form — **public**
  (already exists; will be extended to also accept POST).
- `POST /login` — validate input, authenticate with `check_password_hash`, set
  the session and `redirect` to `landing` on success, or re-render `login.html`
  with an `error` on failure — **public**.
- `GET /logout` — clear the session and `redirect` to `landing` — **logged-in**
  (replaces the current placeholder stub; harmless if hit while logged out).

> Implementation note: `GET /login` and `POST /login` are the **same** `login`
> view function extended to `methods=["GET", "POST"]`, not a second route —
> mirroring how `register` was done in Step 2.

## Database changes

No database changes. The `users` table (with `password_hash`) and the
`get_user_by_email()` helper already exist. Authentication uses
`werkzeug.security.check_password_hash` against the stored hash — no new columns,
tables, or constraints, and no new data-layer functions.

## Templates

- **Create:** none.
- **Modify:** `templates/base.html` — make the `.nav-links` block conditional on
  `session.user_id`: when signed in, show the user's name (`session.user_name`)
  and a "Sign out" link to `url_for('logout')`; when signed out, keep the current
  "Sign in" + "Get started" links. (`session` is available in Jinja by default.)
- `templates/login.html` — **unchanged**; it already POSTs (`email`, `password`)
  to `/login` and has the `{% if error %}` block for the failure message.

## Files to change

- `app.py` — extend the `login` view to `methods=["GET", "POST"]`: read +
  normalise `email` (strip + lowercase) and `password`, validate non-empty, look
  the user up with `get_user_by_email()`, verify with `check_password_hash`, and
  on success set `session["user_id"]` / `session["user_name"]`, `flash` a welcome
  message, and `redirect(url_for("landing"))`; on any failure re-render
  `login.html` with a single generic `error` ("Invalid email or password.").
  Implement the `logout` view to `session.clear()`, `flash` a goodbye message,
  and `redirect(url_for("landing"))`. Add imports `session` (Flask) and
  `check_password_hash` (`werkzeug.security`). `app.secret_key` is already set.
- `templates/base.html` — auth-aware nav (see Templates).
- `static/css/style.css` — only if needed for the new nav greeting (e.g. a
  `.nav-user` rule). CSS variables only — no hardcoded hex.

## Files to create

- None.

## New dependencies

No new dependencies. `werkzeug.security.check_password_hash` ships with Werkzeug,
which is already installed; Flask's `session` requires only the already-set
`app.secret_key`.

## Rules for implementation

- No SQLAlchemy or ORMs — use `sqlite3` via the existing `get_db()` /
  `get_user_by_email()` helpers.
- Parameterised queries only — never string-format values into SQL (the reused
  helper already does this).
- Passwords hashed with werkzeug — verify with `check_password_hash`; never
  compare plaintext and never log the password.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html` (`login.html` already does).
- Normalise email (strip + lowercase) before lookup, matching how Registration
  stored it, so casing never blocks a valid login.
- Return one **generic** error ("Invalid email or password.") for both an
  unknown email and a wrong password — do not reveal which field was wrong.
- Use the Post/Redirect/Get pattern: a successful POST redirects, it does not
  render a page directly.
- Store only `user_id` and `user_name` in the session — never the password or
  hash.
- A `login_required` decorator to protect pages is **out of scope** for this
  step; it belongs to Profile (Step 4), the first route that needs gating.

## Definition of done

- [ ] Visiting `/login` shows the form (GET still works).
- [ ] Submitting `demo@spendly.com` / `demo123` logs in: redirects to `/`
      (landing) with a welcome flash, and the nav now shows the user's name and a
      "Sign out" link instead of "Sign in / Get started".
- [ ] Submitting a wrong password, an unknown email, or empty fields re-renders
      `/login` with a visible generic "Invalid email or password." error and does
      **not** start a session.
- [ ] Email casing is ignored — `DEMO@SPENDLY.COM` / `demo123` logs in the same
      as the lowercase address.
- [ ] Visiting `/logout` clears the session, flashes a goodbye message, and
      redirects to `/`; the nav reverts to the signed-out links.
- [ ] No plaintext password comparison anywhere — auth goes through
      `check_password_hash`.
- [ ] App starts and the flow works end-to-end with `python app.py` at
      `http://localhost:5001`.
