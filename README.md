# CRM Chatters Demo

A mini CRM module for chatters and teamleads, built as a monorepo with realtime chat and team monitoring.

## Planned stack

- **Backend:** Django, Django REST Framework, Django Channels
- **Frontend:** Vue 3 (Composition API), Pinia
- **Database:** PostgreSQL
- **Realtime:** Redis, WebSocket

## Documentation

- [Architecture](docs/architecture.md)
- [REST API](docs/api.md)
- [WebSocket events](docs/websocket-events.md)
- [Development plan](docs/development-plan.md)

## Architecture

_TBD — see [docs/architecture.md](docs/architecture.md)._

## Local setup

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Start all services:

```bash
docker compose up --build
```

3. Open the app:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api |
| Admin | http://localhost:8000/admin |
| Health check | http://localhost:8000/api/health/ |

Services started by Compose:

- **postgres** — PostgreSQL 16 on port 5432
- **redis** — Redis 7 on port 6379
- **backend** — Django ASGI via Daphne on port 8000
- **frontend** — Vite dev server on port 5173

## Test accounts

_TBD._

## Realtime testing

_TBD._

## Deployment

_TBD._
