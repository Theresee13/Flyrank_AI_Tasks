"""Assignment A8 API: query, render, store, then serve PDF reports by link."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from database import DATABASE_PATH, find_report_for_day, get_report_data, get_saved_report, initialize_database, save_report
from pdf_renderer import render_pdf

ROOT = Path(__file__).parent
REPORTS_DIRECTORY = ROOT / "reports"
app = FastAPI(title="PDF Report Generator", version="1.0.0")


class ReportOptions(BaseModel):
    force: bool = False


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def response_record(record: dict) -> dict:
    return {"id": record["id"], "file": f"/reports/{record['id']}/file", "created_at": record["created_at"]}


@app.post("/reports", status_code=201)
def create_report(options: ReportOptions | None = None) -> dict:
    options = options or ReportOptions()
    today = datetime.now(timezone.utc).date().isoformat()
    if not options.force:
        existing = find_report_for_day(today)
        if existing and Path(existing["path"]).is_file():
            return JSONResponse(status_code=200, content=response_record(existing))

    report_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    pdf_path = REPORTS_DIRECTORY / f"sales-report-{report_id}.pdf"
    render_pdf(get_report_data(), pdf_path)
    record = save_report(report_id, str(pdf_path), created_at)
    return response_record(record)


@app.get("/reports/{report_id}")
def get_report(report_id: str) -> dict:
    record = get_saved_report(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")
    return response_record(record)


@app.get("/reports/{report_id}/file")
def download_report(report_id: str) -> FileResponse:
    record = get_saved_report(report_id)
    if not record or not Path(record["path"]).is_file():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(record["path"], media_type="application/pdf", filename=Path(record["path"]).name)
