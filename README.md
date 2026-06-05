# CRM Chatters Demo

Mini CRM module for chatters and teamleads with realtime chat, fan dialog management, SLA monitoring, and WebSocket updates.

**Stack:** Django · DRF · Channels · Vue 3 · Pinia · PostgreSQL · Redis · Docker

---

## Live Demo

### App

**URL:** [http://3.107.70.58/](http://3.107.70.58/)

| Role | Username | Password |
|------|----------|----------|
| Teamlead | `lead` | `password123` |
| Chatter | `chatter1` | `password123` |
| Chatter | `chatter2` | `password123` |
| Chatter | `chatter3` | `password123` |

**Routes after login**

| Role | Page | Path |
|------|------|------|
| Chatter | Workspace | `/chatter` |
| Teamlead | Monitor | `/teamlead` |
| Teamlead | Dialog assignment | `/lead/dialogs` |
| Admin | User management | `/admin/users` |

### Django Admin

**URL:** [http://3.107.70.58/admin](http://3.107.70.58/admin)

| Username | Password |
|----------|----------|
| `admin` | `password123` |

---

## What is implemented

### Chatter workspace

- Assigned fan dialogs with model name, last message preview, timestamp, and unread counter
- Chat window with full message history
- Realtime incoming and outgoing messages over WebSocket
- REST message history with cursor pagination
- Load older messages on scroll up
- Send regular text messages
- Send PPV paid messages with price (pricelist button)
- Unread counter resets when a dialog is opened
- WebSocket reconnect with REST resync for missed messages
- Duplicate message protection via `client_message_id`

### Teamlead monitor

- Online / offline presence per chatter
- Active dialog count per chatter
- Waiting fans count per chatter
- Overdue fans count per chatter
- Realtime workload updates over WebSocket
- Presence heartbeat and configurable grace period

### SLA / response timing

- Fan message starts the response timer (`waiting_since`)
- Chatter reply stops the timer and records response time
- Overdue dialogs are highlighted in chatter, monitor, and lead views
- SLA threshold configurable via `RESPONSE_SLA_SECONDS`

### Admin / lead operations

- Lead dialog assignment (`/lead/dialogs`)
- Chatter workload view on the lead page
- Admin users list (`/admin/users`)
- Invite link creation for new team members
- Invite registration page (`/invite/<token>`)

### Demo mode

- Developer REST endpoint to simulate incoming fan messages
- Optional in-process demo activity via `DEMO_ACTIVITY_ENABLED`
- Manual one-shot demo message: `python manage.py run_demo_activity_once`

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Django, DRF, Channels, Daphne |
| Frontend | Vue 3, Composition API, Pinia, Vite |
| Realtime | WebSocket, Redis channel layer |
| Database | PostgreSQL |
| Deployment | Docker, Docker Compose, host Nginx reverse proxy |

---

## Architecture

REST and WebSocket responsibilities are separated:

- **REST** — authentication, snapshots, lists, message history, pagination, reconnect sync
- **WebSocket** — live events only (new messages, read state, presence, monitor updates)
- **PostgreSQL** — source of truth for all persistent data
- **Redis** — Django Channels layer and presence TTL
- **Events** — published after DB commit using `transaction.on_commit`

```
┌─────────────┐     REST /api      ┌──────────────────┐
│  Vue 3 SPA  │◄──────────────────►│  Django ASGI     │
│  (Pinia)    │     WebSocket /ws  │  DRF + Channels  │
└─────────────┘◄──────────────────►└────────┬─────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                        PostgreSQL                      Redis
                     (persistent data)            (channels + presence)
```

On reconnect, clients resync via REST and re-subscribe to WebSocket rooms.

Further reading: [docs/architecture.md](docs/architecture.md) · [docs/api.md](docs/api.md) · [docs/websocket-events.md](docs/websocket-events.md)

---

## Local setup

**Requirements:** Docker and Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

On first run, seed demo data:

```bash
docker compose exec backend python manage.py seed_demo
```

Open the app (default `.env.example` values):

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api |
| Django Admin | http://localhost:8000/admin |
| Health check | http://localhost:8000/api/health/ |

**Compose services**

| Service | Description | Port |
|---------|-------------|------|
| `postgres` | PostgreSQL 16 | 5432 |
| `redis` | Redis 7 | 6379 |
| `backend` | Django ASGI via Daphne | 8000 |
| `frontend` | Vite dev server | 5173 |

The backend container runs migrations on startup, then starts Daphne.

### Demo data

Seed command creates:

- 3 model accounts (Aurora, Luna, Stella)
- 3 chatters (`chatter1`–`chatter3`)
- 1 teamlead (`lead`)
- 1 admin user (`admin`)
- 8 conversations with message history, waiting/overdue variants, and PPV examples

```bash
# Inside Docker
docker compose exec backend python manage.py seed_demo

# Local backend (without Docker)
cd backend && python manage.py seed_demo
```

Local test accounts (same passwords as the live demo):

| Role | Username | Password |
|------|----------|----------|
| Teamlead | `lead` | `password123` |
| Chatter | `chatter1` | `password123` |
| Chatter | `chatter2` | `password123` |
| Chatter | `chatter3` | `password123` |
| Admin | `admin` | `password123` |

The admin account can manage users and create invite links via `/api/admin/` and the `/admin/users` UI.

---

## Environment configuration

All runtime configuration comes from environment variables. Missing required variables fail startup with a clear error.

Copy and edit before starting:

```bash
cp .env.example .env
```

| Variable | Used by | Purpose |
|----------|---------|---------|
| `DJANGO_SECRET_KEY` | Backend | Django secret key |
| `DJANGO_DEBUG` | Backend | Debug mode (`1` / `0`) |
| `DJANGO_ALLOWED_HOSTS` | Backend | Comma-separated hostnames |
| `DATABASE_URL` | Backend | PostgreSQL connection URL |
| `REDIS_URL` | Backend | Redis connection URL |
| `RESPONSE_SLA_SECONDS` | Backend | SLA threshold for overdue fans |
| `PRESENCE_HEARTBEAT_INTERVAL_SECONDS` | Backend | Presence heartbeat interval |
| `PRESENCE_GRACE_SECONDS` | Backend | Presence TTL grace period |
| `MONITOR_REFRESH_SECONDS` | Backend | Monitor snapshot refresh interval |
| `CORS_ALLOWED_ORIGINS` | Backend | Comma-separated browser origins |
| `FRONTEND_BASE_URL` | Backend | Base URL for invite links |
| `DEMO_ACTIVITY_ENABLED` | Backend | In-process demo fan messages (`0` / `1`) |
| `VITE_API_BASE_URL` | Frontend | REST API base URL |
| `VITE_WS_BASE_URL` | Frontend | WebSocket base URL (`auto` for same-origin production) |
| `POSTGRES_DB` | Postgres | Database name |
| `POSTGRES_USER` | Postgres | Database user |
| `POSTGRES_PASSWORD` | Postgres | Database password |

Docker Compose loads the root `.env` via `env_file`. Vite reads env from the repo root (`frontend/vite.config.ts` `envDir`).

For manual backend dev against Docker Postgres/Redis on the host:

```
DATABASE_URL=postgres://crm:crm@localhost:5432/crm
REDIS_URL=redis://127.0.0.1:6379/0
```

---

## Testing

### Integration smoke test

Requires a running stack and a configured `.env` with **absolute** API/WS URLs (e.g. `http://localhost:8000/api`, not `/api`):

```bash
pip install requests websocket-client python-dotenv
python scripts/integration_smoke_test.py
```

With the project virtualenv:

```bash
backend/.venv/Scripts/pip install requests websocket-client python-dotenv
backend/.venv/Scripts/python scripts/integration_smoke_test.py
```

Covers health check, auth, pagination, read state, monitor snapshot, fan simulation, and WebSocket chat/monitor flows.

### Backend API smoke tests

```bash
cd backend
python scripts/lead_api_smoke_test.py
python scripts/admin_user_invite_smoke_test.py
```

These run against Django directly and do not require a running HTTP server.

### REST API (curl)

After seeding demo data:

```bash
# Obtain token
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"chatter1","password":"password123"}'

# Current user (replace TOKEN)
curl -s http://localhost:8000/api/me/ \
  -H "Authorization: Bearer TOKEN"

# Chatter conversations
curl -s http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer TOKEN"

# Teamlead monitor snapshot
curl -s http://localhost:8000/api/monitor/snapshot/ \
  -H "Authorization: Bearer LEAD_TOKEN"

# Simulate fan message (developer testing only)
curl -s -X POST http://localhost:8000/api/dev/simulate-fan-message/ \
  -H "Authorization: Bearer LEAD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":1,"text":"Hello from fan"}'
```

### WebSocket (wscat)

```bash
# 1. Get JWT token
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"chatter1","password":"password123"}'

# 2. Connect (npm install -g wscat)
wscat -c "ws://localhost:8000/ws/chat/?token=ACCESS_TOKEN"

# 3. Subscribe to a dialog
{"type":"dialog.subscribe","conversation_id":1}

# 4. Send a message
{"type":"message.send","conversation_id":1,"message_type":"TEXT","text":"Hello from WS"}
```

Full event reference: [docs/websocket-events.md](docs/websocket-events.md)

### Demo activity (optional)

Enable automatic incoming fan messages during a demo:

```bash
# In .env
DEMO_ACTIVITY_ENABLED=1
```

Restart the backend. A lightweight in-process thread periodically creates fan messages using the same `create_fan_message` service as real traffic.

Manual one-shot (works even when `DEMO_ACTIVITY_ENABLED=0`):

```bash
docker compose exec backend python manage.py run_demo_activity_once
```

---

## Deployment

The production instance is live at **[http://3.107.70.58/](http://3.107.70.58/)** — see [Live Demo](#live-demo) for access.

### Production Docker

```bash
cp .env.production.example .env
docker compose -f docker-compose.prod.yml up --build -d
```

The backend entrypoint runs `migrate`, `collectstatic`, and auto-seeds demo data on first start.

| Container | Host binding |
|-----------|--------------|
| frontend | `127.0.0.1:3000` |
| backend | `127.0.0.1:8000` |

Configure host Nginx to proxy:

| Path | Target |
|------|--------|
| `/` | `127.0.0.1:3000` |
| `/api/` | `127.0.0.1:8000` |
| `/ws/` | `127.0.0.1:8000` |
| `/admin/` | `127.0.0.1:8000` |
| `/static/` | `127.0.0.1:8000` |

See [docs/deploy-nginx.example.conf](docs/deploy-nginx.example.conf) for a complete reference config including the WebSocket `map` block.

**Checklist**

1. Copy and edit `.env` from `.env.production.example`
2. `docker compose -f docker-compose.prod.yml up --build -d`
3. Configure host Nginx (see example config above)
4. Verify health: [http://3.107.70.58/api/health/](http://3.107.70.58/api/health/)
5. Enable `DEMO_ACTIVITY_ENABLED=1` only for live demos

### Known limitations

- TLS and host Nginx are configured on the server, not in this repository
- Media uploads are not used; static files are served via WhiteNoise
- WebSocket scaling across multiple backend replicas requires sticky sessions or shared channel layer tuning

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | System design and data flow |
| [docs/api.md](docs/api.md) | REST API reference |
| [docs/websocket-events.md](docs/websocket-events.md) | WebSocket event reference |
| [docs/development-plan.md](docs/development-plan.md) | Development plan |
| [docs/deploy-nginx.example.conf](docs/deploy-nginx.example.conf) | Host Nginx reference config |
| [backend/README.md](backend/README.md) | Backend-specific notes |
| [frontend/README.md](frontend/README.md) | Frontend-specific notes |
