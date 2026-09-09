from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_task_lifecycle() -> None:
    create_response = client.post(
        "/tasks",
        json={"title": "Write assignment evidence"},
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    assert client.get(f"/tasks/{user_id}").status_code == 200
    assert client.put(
        f"/tasks/{user_id}",
        json={"title": "Write assignment evidence", "done": True},
    ).status_code == 200
    assert client.delete(f"/tasks/{user_id}").status_code == 204
    assert client.get(f"/tasks/{user_id}").status_code == 404


def test_health_check() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_invalid_task_bodies_return_assignment_400_contract() -> None:
    assert client.post("/tasks", json={}).status_code == 400
    assert client.post("/tasks", json={"title": "   "}).status_code == 400
    created = client.post("/tasks", json={"title": "Keep testing"}).json()
    assert client.put(f"/tasks/{created['id']}", json={}).status_code == 400
    missing = client.get("/tasks/99999")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Task 99999 not found"}
