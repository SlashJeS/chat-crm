# CRM Chatters Demo



A mini CRM module for chatters and teamleads, built as a monorepo with realtime chat and team monitoring.



## Documentation



- [Architecture](docs/architecture.md)

- [REST API](docs/api.md)

- [WebSocket events](docs/websocket-events.md)

- [Development plan](docs/development-plan.md)



## Environment configuration



All runtime configuration comes from environment variables. **Application code does not use hidden fallbacks** — missing required variables fail startup with a clear error.



1. Copy the example file (do not commit `.env`):



```bash

cp .env.example .env

```



2. Edit `.env` if needed. See [.env.example](.env.example) for the full list of required variables.



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

| `DEMO_ACTIVITY_ENABLED` | Backend | In-process demo fan messages (`0` / `1`, default off) |

| `VITE_API_BASE_URL` | Frontend | REST API base URL |

| `VITE_WS_BASE_URL` | Frontend | WebSocket base URL |

| `POSTGRES_DB` | Postgres container | Database name |

| `POSTGRES_USER` | Postgres container | Database user |

| `POSTGRES_PASSWORD` | Postgres container | Database password |



**Docker Compose** loads the root `.env` via `env_file` for backend, frontend, and postgres substitution.



**Frontend (manual dev):** Vite reads env from the **repo root** (see `frontend/vite.config.ts` `envDir`). Use the same root `.env` — no separate frontend env file is required when developing from the monorepo root layout.



**Backend (manual dev):** Loads root `.env` then optional `backend/.env` overrides. When running the backend on the host against Docker Postgres/Redis, set `DATABASE_URL=postgres://crm:crm@localhost:5432/crm` and `REDIS_URL=redis://127.0.0.1:6379/0`.



## Local setup



1. Create `.env` from the example (see above).



2. Start all services:



```bash

docker compose up --build

```



On first run, seed demo data:



```bash

docker compose exec backend python manage.py seed_demo

```



3. Open the app (with default `.env.example` values):



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



The backend container runs migrations on startup, then starts Daphne.



## Live demo activity



Optional in-backend demo simulator. Disabled by default (`DEMO_ACTIVITY_ENABLED=0` in `.env`).



To enable automatic incoming fan messages during a demo:



```bash

# In .env

DEMO_ACTIVITY_ENABLED=1

```



Restart the backend. A lightweight daemon thread inside the backend process periodically creates safe incoming fan messages using the same `create_fan_message` service as real traffic. This updates DB state, unread counters, timers, WebSocket events, and monitor snapshots normally.



Intended for local/demo usage, not production. No separate Docker service or worker is required.



Manual one-shot (works even when `DEMO_ACTIVITY_ENABLED=0`):



```bash

docker compose exec backend python manage.py run_demo_activity_once

```



## Integration smoke test



Requires a running stack and a configured `.env`:



```bash

pip install requests websocket-client python-dotenv

python scripts/integration_smoke_test.py

```



The script reads `VITE_API_BASE_URL` and `VITE_WS_BASE_URL` from `.env`.



When using the project virtualenv:



```bash

backend/.venv/Scripts/pip install requests websocket-client python-dotenv

backend/.venv/Scripts/python scripts/integration_smoke_test.py

```



Lead operations API smoke test (local backend, no running server required):



```bash

cd backend

python scripts/lead_api_smoke_test.py

```



Admin user management and invite API smoke test:



```bash

cd backend

python scripts/admin_user_invite_smoke_test.py

```



Backend smoke scripts load the root `.env` before Django starts.



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



The **admin** account can manage users and create invite links via `/api/admin/` (see [REST API docs](docs/api.md)).



**Invite flow:** Admin creates an invite link in the Users page, sends the link to a new team member, and the invitee registers with their own password at `/invite/<token>`. Invite URLs use `FRONTEND_BASE_URL` from `.env`.



## REST API smoke test



After seeding demo data, verify the API (URLs match your `.env`; examples use default local values):



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



# Simulate fan message via REST (developer testing only — not exposed in the product UI)

curl -s -X POST http://localhost:8000/api/dev/simulate-fan-message/ \

  -H "Authorization: Bearer LEAD_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{"conversation_id":1,"text":"Hello from fan"}'



# Admin: list users

curl -s http://localhost:8000/api/admin/users/ \

  -H "Authorization: Bearer ADMIN_TOKEN"



# Admin: create invite link

curl -s -X POST http://localhost:8000/api/admin/invites/ \

  -H "Authorization: Bearer ADMIN_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{"role":"CHATTER","email":"new@example.com","expires_in_hours":72}'

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

```



See [docs/websocket-events.md](docs/websocket-events.md) for the full event reference.



## Deployment



_TBD._

