# Backend

Django backend for CRM Chatters Demo.

## Stack

- Django, DRF, Django Channels, Daphne
- PostgreSQL (via dj-database-url)
- Redis (Channels + presence TTL)

## Environment

Required variables are documented in the repo root [.env.example](../.env.example). Copy to `.env` before running:

```bash
cp ../.env.example ../.env
```

Settings load env from:

1. `<repo>/.env` (required for Docker and monorepo setup)
2. `backend/.env` (optional overrides when running Django on the host — ignored inside Docker containers)

When running Django on the host against Docker Postgres/Redis, use `localhost` in `backend/.env`:

```
DATABASE_URL=postgres://crm:crm@localhost:5432/crm
REDIS_URL=redis://127.0.0.1:6379/0
```

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret |
| `DJANGO_DEBUG` | Debug flag |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts (comma-separated) |
| `DATABASE_URL` | PostgreSQL URL |
| `REDIS_URL` | Redis URL |
| `RESPONSE_SLA_SECONDS` | SLA seconds |
| `PRESENCE_HEARTBEAT_INTERVAL_SECONDS` | Heartbeat interval |
| `PRESENCE_GRACE_SECONDS` | Presence TTL |
| `MONITOR_REFRESH_SECONDS` | Monitor refresh interval |
| `CORS_ALLOWED_ORIGINS` | CORS origins (comma-separated) |
| `FRONTEND_BASE_URL` | Invite link base URL |
| `DEMO_ACTIVITY_ENABLED` | In-process demo fan messages (`0` off, `1` on) |

## Live demo activity

Optional in-backend simulator for automatic incoming fan messages. Disabled by default.

```bash
# .env
DEMO_ACTIVITY_ENABLED=1
```

Restart the backend (Daphne/runserver). A daemon thread periodically calls `create_fan_message` so chat and monitor realtime updates behave normally. For local/demo use only.

One-shot test without enabling the loop:

```bash
python manage.py run_demo_activity_once
```

## Docker

Local development:

```bash
docker compose up --build
docker compose exec backend python manage.py seed_demo
```

Production-style deployment (build + run everything in Docker):

```bash
cp ../.env.production.example ../.env
docker compose -f docker-compose.prod.yml up --build -d
```

Frontend container listens on `127.0.0.1:3000`, backend on `127.0.0.1:8000`. Host nginx proxies to these ports.

Backend entrypoint runs `migrate`, `collectstatic`, and `ensure_demo_seed` before starting Daphne.

Production settings (`config.settings.production`) enable secure cookies and `SECURE_PROXY_SSL_HEADER` when `DJANGO_DEBUG=0`. Optional `CSRF_TRUSTED_ORIGINS` for Django admin behind HTTPS.

## Manual local development

From `backend/` with venv activated:

```bash
cp ../.env.example ../.env
# If Postgres/Redis run via Docker but Django runs on host, use localhost URLs in .env
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Smoke tests

```bash
python scripts/lead_api_smoke_test.py
python scripts/admin_user_invite_smoke_test.py
```

Scripts load root `.env` before Django starts.

## Demo data

Test accounts (password `password123`): `lead`, `chatter1`, `chatter2`, `chatter3`, `admin`.
