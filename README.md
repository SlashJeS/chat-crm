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

See [Demo data](#demo-data) below.

## Demo data

Seed demo users, conversations and messages:

```bash
docker compose exec backend python manage.py seed_demo
```

For local backend (without Docker container):

```bash
cd backend
python manage.py seed_demo
```

Test accounts:

- lead / password123
- chatter1 / password123
- chatter2 / password123
- chatter3 / password123
- admin / password123

## REST API smoke test

After seeding demo data, verify the API:

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

# Simulate fan message (teamlead/admin, or any user in DEBUG mode)
curl -s -X POST http://localhost:8000/api/dev/simulate-fan-message/ \
  -H "Authorization: Bearer LEAD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":1,"text":"Hello from fan"}'
```

## Realtime testing

Manual WebSocket smoke test (requires Redis running and demo data seeded):

```bash
# 1. Get JWT token
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"chatter1","password":"password123"}'

# 2. Connect with wscat (npm install -g wscat)
wscat -c "ws://localhost:8000/ws/chat/?token=ACCESS_TOKEN"

# 3. After connection.accepted, subscribe to a dialog
{"type":"dialog.subscribe","conversation_id":1}

# 4. Send a chatter message
{"type":"message.send","conversation_id":1,"message_type":"TEXT","text":"Hello from WS"}

# 5. In another terminal, simulate a fan message via REST
curl -s -X POST http://localhost:8000/api/dev/simulate-fan-message/ \
  -H "Authorization: Bearer LEAD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":1,"text":"Hello from fan via REST"}'

# The WebSocket client subscribed to dialog_1 should receive message.created.
```

See [docs/websocket-events.md](docs/websocket-events.md) for the full event reference.

### Monitor realtime test

```bash
# 1. Get lead token
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"lead","password":"password123"}'

# 2. Connect monitor WebSocket
wscat -c "ws://localhost:8000/ws/monitor/?token=LEAD_TOKEN"

# 3. Get chatter token and connect chat WebSocket in another terminal
wscat -c "ws://localhost:8000/ws/chat/?token=CHATTER_TOKEN"

# 4. Send presence heartbeat as chatter
{"type":"presence.heartbeat"}

# 5. Monitor snapshot should show chatter1 is_online=true

# 6. Wait PRESENCE_GRACE_SECONDS without heartbeat and confirm periodic snapshot marks offline

# 7. Simulate fan message via REST and confirm waiting/overdue counts update in monitor.snapshot
curl -s -X POST http://localhost:8000/api/dev/simulate-fan-message/ \
  -H "Authorization: Bearer LEAD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":1,"text":"Hello from fan"}'
```

## Deployment

_TBD._
