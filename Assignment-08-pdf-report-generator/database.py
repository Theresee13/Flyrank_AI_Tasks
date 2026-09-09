"""SQLite storage and aggregation queries for the sales report."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
DATABASE_PATH = ROOT / "report.db"


def connection() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize_database() -> None:
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer TEXT NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def get_report_data() -> dict:
    with connection() as db:
        totals = db.execute("SELECT COUNT(*) AS orders, COALESCE(SUM(amount), 0) AS revenue FROM orders").fetchone()
        products = db.execute(
            """
            SELECT product, ROUND(SUM(amount), 2) AS revenue, COUNT(*) AS order_count
            FROM orders GROUP BY product ORDER BY revenue DESC LIMIT 5
            """
        ).fetchall()
        daily = db.execute(
            """
            SELECT created_at AS day, COUNT(*) AS orders, ROUND(SUM(amount), 2) AS revenue
            FROM orders GROUP BY created_at ORDER BY day DESC LIMIT 7
            """
        ).fetchall()
        all_orders = db.execute(
            "SELECT customer, product, amount, created_at FROM orders ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return {
        "total_orders": totals["orders"],
        "total_revenue": round(totals["revenue"], 2),
        "top_products": [dict(row) for row in products],
        "daily_orders": [dict(row) for row in daily],
        "orders": [dict(row) for row in all_orders],
    }


def find_report_for_day(day: str) -> dict | None:
    with connection() as db:
        row = db.execute("SELECT * FROM reports WHERE created_at LIKE ? ORDER BY created_at DESC LIMIT 1", (f"{day}%",)).fetchone()
    return dict(row) if row else None


def save_report(report_id: str, path: str, created_at: str) -> dict:
    with connection() as db:
        db.execute("INSERT INTO reports (id, path, created_at) VALUES (?, ?, ?)", (report_id, path, created_at))
    return {"id": report_id, "path": path, "created_at": created_at}


def get_saved_report(report_id: str) -> dict | None:
    with connection() as db:
        row = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    return dict(row) if row else None
