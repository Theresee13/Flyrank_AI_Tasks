"""CRUD routes and in-memory state for Assignment A1."""

from fastapi import APIRouter, HTTPException, Response, status

from app.models import Task
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])
_tasks: list[Task] = []
_next_task_id = 1


def get_task_or_404(task_id: int) -> Task:
    """Find a task by id or raise the API's standard not-found response."""
    task = next((item for item in _tasks if item.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.get("", response_model=list[TaskResponse], summary="List tasks")
def list_tasks() -> list[Task]:
    """Return all tasks in insertion order."""
    return _tasks


@router.get("/{task_id}", response_model=TaskResponse, summary="Get one task")
def get_task(task_id: int) -> Task:
    """Return one task after applying the shared not-found check."""
    return get_task_or_404(task_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a task")
def create_task(payload: TaskCreate) -> Task:
    """Create and store a task using the next in-memory identifier."""
    global _next_task_id
    task = Task(id=_next_task_id, title=payload.title.strip())
    _tasks.append(task)
    _next_task_id += 1
    return task


@router.put("/{task_id}", response_model=TaskResponse, summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    """Apply the supplied partial update to an existing task."""
    task = get_task_or_404(task_id)
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Provide title and/or done to update a task")
    if payload.title is not None:
        task.title = payload.title.strip()
    if payload.done is not None:
        task.done = payload.done
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int) -> Response:
    """Remove one task and return the documented empty response."""
    task = get_task_or_404(task_id)
    _tasks.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
