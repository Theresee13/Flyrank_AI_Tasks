"""Assignment A2: the A1 Task API backed by a persistent SQLite database."""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

DATABASE_PATH = Path(__file__).with_name("tasks.db")
app = FastAPI(title="Task API - SQLite", version="1.0.0")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class Task(TaskCreate):
    id: int
    done: bool


def connection() -> sqlite3.Connection:
    """Open a row-aware connection to the local task database."""
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize_database() -> None:
    """Create the table and starter rows when the database is empty."""
    with connection() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, "
            "done INTEGER NOT NULL DEFAULT 0)"
        )
        if db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [("Learn SQLite", 0), ("Write a parameterized query", 0), ("Inspect tasks.db", 1)],
            )


def as_task(row: sqlite3.Row) -> dict[str, object]:
    """Convert SQLite's integer flag into the public boolean field."""
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def task_or_404(db: sqlite3.Connection, task_id: int) -> sqlite3.Row:
    """Load a task row or raise the API's standard not-found error."""
    row = db.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row


initialize_database()


@app.get("/")
def root() -> dict[str, object]:
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[dict[str, object]]:
    with connection() as db:
        return [as_task(row) for row in db.execute("SELECT id, title, done FROM tasks ORDER BY id")]


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> dict[str, object]:
    with connection() as db:
        return as_task(task_or_404(db, task_id))


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict[str, object]:
    with connection() as db:
        cursor = db.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (payload.title.strip(), 0))
        return as_task(db.execute("SELECT id, title, done FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone())


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> dict[str, object]:
    with connection() as db:
        current = task_or_404(db, task_id)
        title = payload.title.strip() if payload.title is not None else current["title"]
        done = payload.done if payload.done is not None else bool(current["done"])
        db.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, task_id))
        return as_task(db.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone())


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    with connection() as db:
        task_or_404(db, task_id)
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
