# Assignment A1: In-Memory Task API

A small FastAPI task API that keeps data in memory. Restarting the service clears all tasks by design; Assignment A2 moves the same API contract to SQLite.

## Run locally

```bash
cd Assignment-01-fastapi-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive documentation is available at `/docs` and `/redoc`.

## Endpoints

| Method | Endpoint | Description | Success code |
| --- | --- | --- | --- |
| GET | `/health` | Service health check | 200 |
| GET | `/` | API information | 200 |
| POST | `/tasks` | Create a task | 201 |
| GET | `/tasks` | List tasks | 200 |
| GET | `/tasks/{task_id}` | Fetch a task | 200 |
| PUT | `/tasks/{task_id}` | Update title and/or completion | 200 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 |

`title` is required. Invalid create or update requests return `400` with an `{ "error": "..." }` response. Missing task IDs return `404` with the same JSON error shape.

## Verified curl proof

The following local run exercised the full CRUD lifecycle on 2026-09-08:

```text
POST /tasks                         -> 201 Created
GET /tasks/1                        -> 200 OK
PUT /tasks/1 {"done": true}         -> 200 OK
DELETE /tasks/1                     -> 204 No Content
```

The created task response was:

```json
{"id":1,"title":"Capture assignment evidence","done":false}
```

Open `http://127.0.0.1:8000/docs` after starting the server to run the same lifecycle with Swagger UI. Capture that browser view locally before submitting; it is intentionally not represented by a fabricated image in this repository.

## Test

```bash
pytest
```

Latest local result: `3 passed`.
