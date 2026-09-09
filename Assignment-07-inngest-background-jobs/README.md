# Assignment A7: Inngest Background Report API

An API that accepts a slow report request immediately and delegates an eight-second durable wait plus report generation to Inngest. Reports progress from `pending` to `running` to `done`.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:INNGEST_DEV = "1"
uvicorn main:app --reload
```

Start the local Inngest dev server in a second terminal:

```bash
inngest dev -u http://localhost:8000/api/inngest
```

## API

| Method | Endpoint | Result |
| --- | --- | --- |
| GET | `/health` | Health status |
| POST | `/reports` | Returns `202` and a pending report ID immediately |
| GET | `/reports/{id}` | Returns pending, running, done, or failed status |

`generate-report` uses durable `mark-running`, `do-the-slow-work`, `build-report`, and `mark-done` steps, with two retries. Sending `{ "topic": "fail" }` deliberately fails the build step so the dashboard shows all three attempts. `report-heartbeat` is an every-minute cron function that logs pending, done, and failed report totals.

Poll a returned `status_url`: a successful report is initially `pending`, then becomes `done` after roughly eight seconds. Invalid payloads are rejected before an event is sent. `0 8 * * *` runs daily at 08:00; `0 22 * * 0` runs every Sunday at 22:00.

## Live verification

Verified locally on 2026-09-09 with Inngest Dev Server v1.44.0:

```text
POST /reports {"topic":"cats"} -> 202 Accepted
id: 5760705b-9044-4cb2-89c7-5f59f6fd3013
initial status: pending
final status: done
result: FlyRank background report for cats. Generated after durable queued processing.
```

The completed `generate-report` run took `8.413s`. Its dashboard trace showed `mark-running`, `do-the-slow-work` (`8.000s`), `build-report`, and `mark-done`.

The deliberate failure path was also run:

```text
POST /reports {"topic":"fail"} -> 202 Accepted
id: 3ce7c774-5f82-4aa1-892c-c633cf9e0ffa
final status: failed
error: The report oven is broken!
```

The Dev Server recorded the failure after its retry window (`1m 29s`) and showed the durable sleep, `build-report`, `mark-failed`, and function error in its trace. Two completed `report-heartbeat` cron runs were visible one minute apart. Dashboard screenshots were captured during this verification; re-run the two documented commands above when a fresh local capture is required.
