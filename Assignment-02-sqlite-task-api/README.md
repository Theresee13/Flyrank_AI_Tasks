# Assignment A2: SQLite Task API

This is the persistent version of Assignment A1. It preserves the same `/tasks` CRUD contract while storing data in `tasks.db` with parameterized SQLite queries. The database creates and seeds itself only when empty, so tasks survive a server restart.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to exercise the same `GET`, `POST`, `PUT`, and `DELETE /tasks` endpoints from A1. The generated `tasks.db` remains local and is intentionally ignored by Git.

## Database evidence

The SQLite database structure and `tasks` table are shown in [the DB Browser screenshot](docs/screenshots/a2-sqlite-database-viewer.png).
