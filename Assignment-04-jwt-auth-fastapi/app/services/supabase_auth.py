"""Small server-side adapter for Supabase Auth's REST API."""

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, UnauthorizedError, ValidationError


def _request(path: str, method: str, payload: dict[str, Any] | None = None, access_token: str | None = None) -> dict[str, Any]:
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise ValidationError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY.")

    headers = {"apikey": settings.supabase_publishable_key}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if payload is not None:
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{settings.supabase_auth_url}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=12) as response:
            body = response.read().decode()
            return json.loads(body) if body else {}
    except HTTPError as error:
        detail = error.read().decode()
        if error.code in {400, 401, 403, 422}:
            if path.startswith("/token"):
                raise InvalidCredentialsError("Invalid email or password") from error
            raise UnauthorizedError("Supabase rejected the request") from error
        raise ValidationError(f"Supabase Auth request failed: {detail or error.reason}") from error
    except URLError as error:
        raise ValidationError("Could not reach Supabase Auth") from error


def sign_up(email: str, password: str, full_name: str) -> dict[str, Any]:
    return _request("/signup", "POST", {"email": email, "password": password, "data": {"full_name": full_name}})


def sign_in(email: str, password: str) -> dict[str, Any]:
    return _request("/token?grant_type=password", "POST", {"email": email, "password": password})


def sign_out(access_token: str) -> None:
    _request("/logout", "POST", access_token=access_token)


def get_user(access_token: str) -> dict[str, Any]:
    return _request("/user", "GET", access_token=access_token)
