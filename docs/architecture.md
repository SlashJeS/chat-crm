# Architecture

## Overview

CRM Chatters Demo separates **REST** and **WebSocket** responsibilities:

- **REST** is used for snapshots, lists, history, authentication, and reconnect synchronization.
- **WebSocket** is used for live events only.

PostgreSQL is the **source of truth** for persistent data. Redis is used for Django Channels (pub/sub and channel layers) and for **presence TTL** (heartbeat-based online state).

## Backend

- **Django** — web framework and ORM
- **Django REST Framework (DRF)** — REST API
- **Django Channels** — WebSocket consumers and async routing

## Frontend

- **Vue 3** — UI (Composition API)
- **Pinia** — client state management

## Data flow (high level)

1. Clients load initial state via REST (conversations, messages, auth).
2. Clients subscribe to WebSocket channels for live updates (new messages, read state, presence, monitor events).
3. On reconnect, clients resync via REST and re-subscribe to WebSocket rooms.

## Configuration

Runtime settings are supplied via the repo root `.env` file (see [.env.example](../.env.example)). Backend and frontend fail fast when required variables are missing.

- **PostgreSQL** — persistent data (`DATABASE_URL`)
- **Redis** — Channels layer and presence TTL (`REDIS_URL`)
- **Frontend URLs** — `VITE_API_BASE_URL`, `VITE_WS_BASE_URL`
- **Invite links** — `FRONTEND_BASE_URL`
- **Live demo activity** — `DEMO_ACTIVITY_ENABLED` (`0` by default). When `1`, a daemon thread in the backend process periodically generates safe incoming fan messages via `create_fan_message`, triggering normal WebSocket and monitor updates. No separate worker container. Manual one-shot: `python manage.py run_demo_activity_once`.

## Deployment

- **Local dev** — `docker compose up` with Vite dev server (5173) and Daphne (8000), source bind mounts
- **Production-style** — `docker compose -f docker-compose.prod.yml up --build -d` runs postgres, redis, backend, and frontend containers; host nginx proxies to `127.0.0.1:3000` (frontend) and `127.0.0.1:8000` (backend)

See also [api.md](api.md) and [websocket-events.md](websocket-events.md).
