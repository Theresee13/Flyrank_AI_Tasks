"""HTTP application setup for the in-memory task API."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes.tasks import router as tasks_router

app = FastAPI(
    title="FlyRank Task API",
    description="An in-memory REST API for Assignment A1.",
    version="1.0.0",
)

app.include_router(tasks_router)


@app.exception_handler(RequestValidationError)
async def request_validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
    """Return the assignment's explicit 400 JSON validation contract."""
    first_error = error.errors()[0]
    return JSONResponse(status_code=400, content={"error": first_error["msg"]})


@app.exception_handler(StarletteHTTPException)
async def http_error(_: Request, error: StarletteHTTPException) -> JSONResponse:
    """Keep framework HTTP errors in the API's compact error shape."""
    return JSONResponse(status_code=error.status_code, content={"error": str(error.detail)})


@app.get("/", tags=["info"])
def api_info() -> dict[str, str | list[str]]:
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight health status for deployments and monitoring."""
    return {"status": "ok"}
