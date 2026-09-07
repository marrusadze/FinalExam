# EventHub

A web portal for posting and discovering local events, built with **Flask** as
the final exam project for the Python course at Tbilisi School of
Communication.

## Features

- Registration, login, logout (Flask-Login, hashed passwords)
- Guests can browse events and the About page only; logged-in users get
  "Add Event" and a profile menu
- Full CRUD on events, restricted so a user can only edit/delete their own
  events (authorization enforced server-side, not just hidden in the UI)
- Event list as cards (title, author, date, short description) with
  "Read More" for full details, filtering by category, search, and sorting
  by posted date / event date / price
- Clicking an author's name opens their public profile with all of their
  events
- Profile page: edit name/email and upload a profile picture
- Categories: Music, Tech, Art, Sport, Education, Other
- Live weather for each event's location via the OpenWeatherMap API
- JSON REST API (`/api/events`) with GET/POST/PUT/PATCH/DELETE and
  API-key authentication for the write endpoints
- Custom, styled 404 / 403 / 500 error pages
- CSRF protection on every form (Flask-WTF)
- File logging (`logs/app.log`) of successful/failed logins, event
  add/edit/delete, and API errors
- Pytest suite covering routes, auth, permissions, and the JSON API (20 tests)

## JSON API

Read endpoints are public; write endpoints require the header
`X-API-Key: <API_KEY from .env>`.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/events` | – | list events (`?category=`, `?q=`) |
| GET | `/api/events/<id>` | – | one event |
| POST | `/api/events` | key | create |
| PUT | `/api/events/<id>` | key | replace all fields |
| PATCH | `/api/events/<id>` | key | update sent fields only |
| DELETE | `/api/events/<id>` | key | delete |

```bash
curl http://localhost:5000/api/events

curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"title":"Demo","short_description":"s","full_description":"f",
       "location":"Tbilisi","event_date":"2030-01-01T10:00",
       "organizer":"me","category":"Tech"}'
```

The API is stateless and token-authenticated, so it is exempt from CSRF.

## Project structure

```
eventhub/
├── app/
│   ├── __init__.py        # app factory, error handlers
│   ├── extensions.py       # db, login_manager, csrf
│   ├── models.py           # User, Event
│   ├── forms.py             # Flask-WTF forms
│   ├── weather.py           # OpenWeatherMap wrapper
│   ├── logging_config.py    # logging setup
│   ├── routes/
│   │   ├── main.py          # /about
│   │   ├── auth.py          # register/login/logout
│   │   ├── events.py        # event CRUD, listing, author page
│   │   ├── profile.py       # profile view/edit
│   │   └── api.py           # JSON REST API (/api/events)
│   ├── templates/
│   └── static/
├── tests/                   # pytest suite
├── config.py                # Dev / Prod / Testing config
├── run.py                   # local dev entry point
├── wsgi.py                  # production entry point (gunicorn)
├── requirements.txt
├── Procfile                 # for Render / Heroku-style hosts
├── .env.example
└── logs/app.log             # created at runtime
```

## Local setup

1. **Clone/download the project**, then create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create your `.env` file** from the example and fill in the values:

   ```bash
   cp .env.example .env
   ```

   - `SECRET_KEY`: generate one with
     `python -c "import secrets; print(secrets.token_hex(32))"`
   - `OPENWEATHER_API_KEY`: sign up for a free key at
     https://openweathermap.org/api (Current Weather Data). If you leave
     this blank, the app still runs fine — the weather widget on the event
     page just won't show data.

3. **Run the app**:

   ```bash
   python run.py
   ```

   Visit http://localhost:5000 — the SQLite database (`eventhub.db`) and the
   uploads folder are created automatically on first run.

4. **Run the tests**:

   ```bash
   pytest -v
   ```

## Logging

All authentication events, event CRUD actions, and weather-API errors are
written to `logs/app.log` (rotated automatically at ~1 MB) as well as the
console, for example:

```
2026-09-06 08:48:32 INFO [app.routes.auth] Successful login: test@example.com (id=1)
2026-09-06 08:48:32 WARNING [app.routes.auth] Failed login attempt for email: test@example.com
2026-09-06 08:48:32 INFO [app.routes.events] Event added: 'My Test Event' (id=1) by user test@example.com
2026-09-06 08:48:32 INFO [app.weather] Weather lookup skipped for 'Tbilisi': no OPENWEATHER_API_KEY configured.
```

## Deploying: GitHub + a hosting provider

The assignment requires the project to be on GitHub and reachable at a live
URL. This project ships ready for that; you just need your own accounts to
push and deploy it.

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "EventHub Flask final project"
git branch -M main
git remote add origin https://github.com/<your-username>/eventhub.git
git push -u origin main
```

(`.env` and the SQLite file are already excluded via `.gitignore` — never
commit real secrets.)

### 2. Deploy — pick one free option

**Render.com** (simplest for Flask + Postgres/SQLite):

1. Create a new **Web Service**, connect your GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn wsgi:app`
4. Add environment variables in the Render dashboard: `SECRET_KEY`,
   `OPENWEATHER_API_KEY`, `FLASK_ENV=production`.
5. Deploy — Render gives you a URL like `https://eventhub-xxxx.onrender.com`.

**PythonAnywhere** (good if you prefer a classic PaaS):

1. Upload/clone the repo in a Bash console there.
2. Create a virtualenv and `pip install -r requirements.txt`.
3. In the **Web** tab, create a new web app (manual config, Flask), point
   the WSGI file to import `app` from `wsgi.py`.
4. Set the same environment variables under the app's "Environment
   variables" section (or load them from a `.env` file with python-dotenv,
   already wired into `config.py`).

**Railway.app**: connect the GitHub repo, it auto-detects the `Procfile`
and `requirements.txt`; add the same environment variables in its
dashboard.

Note: SQLite is fine for this assignment/demo, but on most hosts its file
storage is not persistent across deploys — if you need data to survive
redeploys, switch `DATABASE_URL` to a managed Postgres instance (the app
already reads it from an environment variable, so no code changes needed
beyond `pip install psycopg2-binary`).

## Test coverage

`tests/` contains four groups (20 tests total):

- `test_routes.py` — route/page-load tests (home, about, event detail, 404,
  auth-required redirect)
- `test_auth.py` — registration, successful login, failed login, logout
- `test_permissions.py` — a second user cannot edit or delete another
  user's event (403), while the owner can
- `test_api.py` — JSON API: list/detail responses, 404 as JSON, 401 without
  an API key, create/patch/delete with a key, bad-category rejection
