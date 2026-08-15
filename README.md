# Student Attendance System

Flask + SQLite attendance project with a red, blue and white premium UI.

Features: student management, duplicate roll protection, attendance marking, duplicate attendance protection, status toggle, delete, reports search/status filter, login, hashed password, password change, live clock/date, animated counters and mobile responsive design.

Default login: admin / admin123. Change it after first login.

Local:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py

Render build command: pip install -r requirements.txt
Render start command: gunicorn app:app

Note: SQLite is included. Render Free web services have an ephemeral filesystem, so permanent production persistence requires a persistent disk or external database.
