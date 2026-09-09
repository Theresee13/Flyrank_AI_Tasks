"""
Reusable authentication dependency ("middleware").

This is the SINGLE place JWT validation happens. Any protected route
just declares `current_user: User = Depends(get_current_user)` and gets:
  - Authorization header presence check
  - "Bearer <token>" scheme check
  - Signature + expiration verification
  - The authenticated User loaded from the DB, attached to the request

No route or controller re-implements any of this logic.
"""
from fastapi import Request

from app.core.exceptions import UnauthorizedError
from app.services.supabase_auth import get_user


def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise UnauthorizedError("Missing Authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Authorization header must be in the form: Bearer <token>")

    token = parts[1]

    return get_user(token)
