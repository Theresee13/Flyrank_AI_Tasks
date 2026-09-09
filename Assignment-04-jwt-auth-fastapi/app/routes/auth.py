"""
Authentication routes: registration and login.

Route handlers stay thin — validation is handled by Pydantic schemas,
business logic lives in app.services.auth_service.
"""
from fastapi import APIRouter, Depends, Request, status

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import supabase_auth

router = APIRouter(tags=["auth"])


def as_user_response(user: dict) -> dict:
    return {
        "id": user["id"],
        "full_name": user.get("user_metadata", {}).get("full_name"),
        "email": user["email"],
        "created_at": user["created_at"],
    }


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def register(payload: UserCreate):
    """
    Register a new user.

    - 201: user created, returns the safe user representation
    - 400: validation error (handled automatically by Pydantic/FastAPI)
    - 409: email already registered
    """
    response = supabase_auth.sign_up(payload.email, payload.password, payload.full_name)
    return as_user_response(response["user"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """
    Authenticate a user and issue a JWT access token.

    - 200: returns the access token
    - 401: invalid email or password
    """
    token = supabase_auth.sign_in(payload.email, payload.password)
    return TokenResponse(access_token=token["access_token"], expires_in=token.get("expires_in"))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request):
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        from app.core.exceptions import UnauthorizedError
        raise UnauthorizedError("Authorization header must be in the form: Bearer <token>")
    supabase_auth.sign_out(parts[1])
