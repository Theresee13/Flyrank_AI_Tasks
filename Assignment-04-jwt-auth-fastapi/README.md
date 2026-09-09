# Assignment A4: Supabase Auth API

A FastAPI authentication API backed by Supabase Auth. Supabase stores identities and issues JWTs; this service provides documented signup, login, logout, and protected-profile routes.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Set these local values in `.env` from Supabase **Settings -> API**:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_your_key
```

The API runs at `http://127.0.0.1:8000`; interactive Swagger documentation is at `/docs`.

## API

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/signup` | No | Create an account through Supabase Auth |
| POST | `/login` | No | Exchange credentials for a Supabase access token |
| POST | `/logout` | Bearer token | End the active Supabase session |
| GET | `/me` | Bearer token | Validate the JWT through Supabase and return the profile |
| GET | `/health` | No | Service health check |

`POST /register` remains as a hidden compatibility alias for `/signup`.

## Token flow

1. Send email, password, and full name to `POST /signup`.
2. Send email and password to `POST /login`.
3. Use the response's `access_token` as `Authorization: Bearer <token>` for `/me` and `/logout`.

The service does not issue its own tokens or keep passwords in a local database. `app/services/supabase_auth.py` is the only module that calls the Supabase Auth REST API, and `app/middleware/auth.py` is the single protected-route dependency.
