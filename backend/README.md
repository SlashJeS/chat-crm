# Backend

Django backend for CRM Chatters Demo.

## Stack

- Django
- Django REST Framework
- Django Channels
- Daphne (ASGI server)
- channels-redis (channel layer)
- django-cors-headers
- djangorestframework-simplejwt
- PostgreSQL (via dj-database-url)
- Redis (channel layer and presence TTL)

## Local run (later)

Once Docker Compose services are wired up:

```bash
docker compose up --build
```

For manual local development (from this directory):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Current endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health/` | No | Health check — returns `{"status": "ok"}` |
| GET | `/api/me/` | JWT | Current user — returns id, username, email, role (null for now) |
| POST | `/api/auth/token/` | No | Obtain JWT access/refresh tokens |
| POST | `/api/auth/token/refresh/` | No | Refresh JWT access token |

## Apps

| App | Purpose |
|-----|---------|
| `apps.accounts` | Authentication and user endpoints |
| `apps.model_accounts` | Model account domain (placeholder) |
| `apps.conversations` | Conversations and messages (placeholder) |
| `apps.realtime` | WebSocket consumers and event publishing (placeholder) |
| `apps.monitoring` | Teamlead monitor API and WebSocket (placeholder) |
| `apps.presence` | Presence heartbeat and TTL (placeholder) |
| `apps.demo` | Demo seed management command (placeholder) |
