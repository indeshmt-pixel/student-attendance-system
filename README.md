# Student Attendance System

A Flask + SQLite student attendance web app that can also be installed on a phone as a PWA.

## Features

- Student add, search and delete
- Course and semester dropdowns
- Gmail/email field with server-side validation
- Duplicate roll number protection
- Duplicate email protection
- Attendance marking with today's date filled automatically
- Subject dropdown
- Same student + same date + same subject cannot be saved twice
- Attendance Present/Absent toggle
- Attendance delete
- Reports search, status and date filters
- Login system with hashed password
- Password change
- Animated dashboard counters
- Mobile responsive layout
- PWA install support for Android/iPhone-compatible browsers
- Render-ready Gunicorn configuration
- SQLite database

## Default login

Username: `admin`

Password: `admin123`

Change the password after the first login.

## Run locally

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Render

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
gunicorn app:app
```

Set a `SECRET_KEY` environment variable in Render for production.

### Important database note

This project uses SQLite. A Render Free web service uses an ephemeral filesystem, so SQLite data should **not** be treated as permanent production storage. For permanent data after redeploys/restarts, use a paid persistent disk or move the database to a managed PostgreSQL service.

## Install as an app

After the Render URL is working over HTTPS:

1. Open the site in Chrome on Android.
2. Use the browser menu and choose **Install app** / **Add to Home screen**.
3. The site will open like an app.

The project also contains a PWA manifest, icons and service worker.
