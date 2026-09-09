# Assignment A8: PDF Report Generator

This FastAPI project queries a small SQLite sales dataset, renders a multi-page PDF with Playwright, saves that file to disk, and serves it through a download link. It intentionally runs PDF generation inside the request so the visible delay illustrates when a background job would become appropriate.

## Setup and run

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python seed.py
uvicorn main:app --reload
```

The seed command clears then inserts exactly 200 deterministic orders, so it is safe to run twice. Visit `http://127.0.0.1:8000/docs` or run:

```powershell
curl -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d "{}"
curl -o sales-report.pdf http://127.0.0.1:8000/reports/<report-id>/file
```

## Aggregation SQL

```sql
SELECT COUNT(*) AS orders, COALESCE(SUM(amount), 0) AS revenue FROM orders;
SELECT product, SUM(amount) AS revenue, COUNT(*) AS order_count
FROM orders GROUP BY product ORDER BY revenue DESC LIMIT 5;
SELECT created_at AS day, COUNT(*) AS orders, SUM(amount) AS revenue
FROM orders GROUP BY created_at ORDER BY day DESC LIMIT 7;
```

The generated HTML includes `thead { display: table-header-group; }` and `tr { break-inside: avoid; }`, so report headers repeat and table rows are not split across PDF pages.

## API

| Method | Endpoint | Result |
| --- | --- | --- |
| GET | `/health` | Service health response. |
| POST | `/reports` | Generates a PDF and returns `201` with an ID and file link. |
| GET | `/reports/{id}` | Returns the report metadata and download link. |
| GET | `/reports/{id}/file` | Streams the stored PDF from disk. |

Calling `POST /reports` twice on the same UTC day returns the existing report instead of creating another file. Use `{ "force": true }` to intentionally generate a fresh report. This protects against a double-click causing duplicate expensive work; the analogous production risk is charging or emailing a customer twice.

For a larger report or a high-traffic endpoint, I would move rendering into the A7 background-job flow: users get a faster response, at the cost of status tracking and eventual consistency. `report.db` and generated `reports/` are deliberately ignored because the seed script is the reproducible recipe.
