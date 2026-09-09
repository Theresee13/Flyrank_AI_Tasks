"""Assignment A7: durable report generation with FastAPI and Inngest."""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import inngest
import inngest.fast_api
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).with_name("reports.db")
client = inngest.Inngest(app_id="flyrank-background-reports")
app = FastAPI(title="Inngest Background Report API", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def request_validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": error.errors()})


class ReportRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=160)


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def setup() -> None:
    with db() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY, topic TEXT NOT NULL, status TEXT NOT NULL,
            content TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")


def report_or_404(report_id: str) -> dict:
    with db() as connection:
        row = connection.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return dict(row)


def update_report(report_id: str, **fields: str) -> None:
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    with db() as connection:
        connection.execute(f"UPDATE reports SET {assignments} WHERE id = ?", (*fields.values(), report_id))


def build_report(topic: str) -> str:
    if topic.lower() == "fail":
        raise RuntimeError("The report oven is broken!")
    return f"FlyRank background report for {topic}. Generated after durable queued processing."


@client.create_function(
    fn_id="generate-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def generate_report(ctx: inngest.Context) -> dict:
    report_id = ctx.event.data["report_id"]
    report = report_or_404(report_id)
    if report["status"] == "done":
        return {"report_id": report_id, "status": "done", "replayed": True}

    try:
        await ctx.step.run("mark-running", lambda: update_report(report_id, status="running"))
        await ctx.step.sleep("do-the-slow-work", timedelta(seconds=8))
        content = await ctx.step.run("build-report", lambda: build_report(report["topic"]))
        await ctx.step.run("mark-done", lambda: update_report(report_id, status="done", content=content))
        return {"report_id": report_id, "status": "done"}
    except Exception as error:
        await ctx.step.run("mark-failed", lambda: update_report(report_id, status="failed", error=str(error)))
        raise


@client.create_function(fn_id="report-heartbeat", trigger=inngest.TriggerCron(cron="* * * * *"))
async def report_heartbeat(ctx: inngest.Context) -> dict:
    def status_summary() -> dict[str, int]:
        with db() as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) AS count FROM reports GROUP BY status"
            ).fetchall()
        return {row["status"]: row["count"] for row in rows}

    summary = await ctx.step.run("summarize-report-statuses", status_summary)
    print(f"report heartbeat: {summary}")
    return summary


setup()
inngest.fast_api.serve(app, client, [generate_report, report_heartbeat])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(payload: ReportRequest) -> dict[str, str]:
    report_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with db() as connection:
        connection.execute(
            "INSERT INTO reports (id, topic, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (report_id, payload.topic.strip(), "pending", now, now),
        )
    await client.send(
        inngest.Event(name="report/requested", data={"report_id": report_id, "topic": payload.topic.strip()})
    )
    return {"id": report_id, "status": "pending", "status_url": f"/reports/{report_id}"}


@app.get("/reports/{report_id}")
async def get_report(report_id: str) -> dict:
    return report_or_404(report_id)
