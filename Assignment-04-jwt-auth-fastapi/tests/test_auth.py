from fastapi.testclient import TestClient

from app.main import app
from app.middleware import auth as auth_middleware
from app.services import supabase_auth

client = TestClient(app)


def sample_user() -> dict:
    return {
        "id": "a0560873-52d1-4475-8810-58c2182d3058",
        "email": "tester@example.com",
        "created_at": "2026-09-08T00:00:00+00:00",
        "user_metadata": {"full_name": "Test User"},
    }


def test_signup_delegates_to_supabase(monkeypatch) -> None:
    monkeypatch.setattr(supabase_auth, "sign_up", lambda *_args: {"user": sample_user()})

    response = client.post("/signup", json={
        "full_name": "Test User",
        "email": "tester@example.com",
        "password": "SecurePass1",
    })

    assert response.status_code == 201
    assert response.json()["email"] == "tester@example.com"


def test_login_returns_supabase_access_token(monkeypatch) -> None:
    monkeypatch.setattr(supabase_auth, "sign_in", lambda *_args: {"access_token": "supabase-token", "expires_in": 3600})

    response = client.post("/login", json={"email": "tester@example.com", "password": "SecurePass1"})

    assert response.status_code == 200
    assert response.json()["access_token"] == "supabase-token"


def test_me_requires_and_validates_bearer_token(monkeypatch) -> None:
    assert client.get("/me").status_code == 401
    monkeypatch.setattr(auth_middleware, "get_user", lambda _token: sample_user())

    response = client.get("/me", headers={"Authorization": "Bearer supabase-token"})

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test User"
