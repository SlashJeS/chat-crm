# Frontend

Vue 3 frontend for CRM Chatters Demo.

## Stack

- Vue 3 (Composition API)
- Vite
- TypeScript
- Pinia
- Vue Router
- Axios
- Plain CSS design system (no UI library)

## Design system

The frontend uses a token-based design system with **dark theme as the default** and a responsive SaaS dashboard UI built with plain CSS — no UI framework.

- **Tokens:** `src/styles/tokens.css` — CSS variables for dark and light themes (`data-theme="dark"` / `data-theme="light"`)
- **Base styles:** `src/styles/base.css` — reset, typography, focus, scrollbars
- **Utilities:** `src/styles/utilities.css` — reusable classes (`btn`, `card`, `panel`, `badge`, `status-pill`, `empty-state`, etc.)
- **Theme store:** `src/stores/theme.store.ts` — persists preference in `localStorage` under `crm-theme`
- **Theme toggle:** `src/components/common/ThemeToggle.vue`
- **Logo assets:** `src/assets/brand/` — SVG mark and full logos for dark/light backgrounds
- **Favicon:** `public/favicon.svg` — logo mark used in `index.html`

Toggle light/dark from the app header or login page. If no preference is saved, dark mode is applied on startup.

### UI surfaces

| Surface | Description |
|---------|-------------|
| Login | Split hero + sign-in panel with demo accounts |
| App shell | Collapsible sidebar (nav + theme), top bar (page title + user menu) |
| Chatter Workspace | Two-column inbox: dialog list + chat panel |
| Teamlead Monitor | KPI cards, SLA config, chatter workload table |
| Lead Dialogs | Dialog list with filters, assignment panel, chatter workload |

All surfaces use shared tokens and utilities, support dark/light themes, and are responsive from mobile to desktop widths.

## Environment

Required variables are listed in the repo root [.env.example](../.env.example). Copy the root `.env` before running:

```bash
cp ../.env.example ../.env
```

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | REST API base URL (e.g. `http://localhost:8000/api` or `/api` with same-origin host proxy) |
| `VITE_WS_BASE_URL` | WebSocket base URL (e.g. `ws://localhost:8000` or `auto` for same-origin host proxy) |

Vite reads env from the **repository root** (`envDir` in `vite.config.ts`). Missing variables throw at dev/build time via `src/config/env.ts`.

**Docker:** frontend service uses `env_file: .env` — same root file as backend.

**Manual dev:** run `npm run dev` from `frontend/` after creating root `.env`. Optional override: `frontend/.env.local` (gitignored).

## Routes

| Path | View | Access |
|------|------|--------|
| `/` | Redirect to `/login` | Public |
| `/login` | LoginView | Public (guest) |
| `/chatter` | ChatterWorkspaceView | CHATTER |
| `/teamlead` | TeamleadMonitorView | TEAMLEAD, ADMIN |
| `/lead/dialogs` | LeadDialogsView | TEAMLEAD, ADMIN |

## Authentication

The frontend uses JWT authentication against the Django backend.

1. User submits username and password on `/login`.
2. The app calls `POST /api/auth/token/` and stores tokens in `localStorage`.
3. The app calls `GET /api/me/` to load the current user profile.
4. The router redirects based on role.

Test users are created by `python manage.py seed_demo`.

## Chatter workspace

The `/chatter` route provides a functional workspace:

- Dialog list sorted by `last_message_at`
- Message history with scroll-up pagination
- WebSocket live updates for `message.created` and `conversation.updated`
- Send TEXT messages through WebSocket
- Send PPV messages through WebSocket as a one-click **Send pricelist** action (unlocks a predefined price list for $9.99)
- Mark conversation read when opened

The backend dev endpoint `POST /api/dev/simulate-fan-message/` remains available for manual/API testing but is not exposed in the product UI.

### REST endpoints used

- `GET /api/conversations/`
- `GET /api/conversations/{id}/messages/`
- `POST /api/conversations/{id}/read/`

### WebSocket endpoint

```
ws://localhost:8000/ws/chat/?token=<access_token>
```

Client events: `dialog.subscribe`, `dialog.unsubscribe`, `message.send`, `dialog.mark_read`, `presence.heartbeat`

Server events: `message.created`, `conversation.updated`, `conversation.read_state.updated`

## Teamlead monitor

The `/teamlead` route provides a live monitor dashboard:

- Initial load via REST snapshot
- Live updates via monitor WebSocket
- Summary cards for online chatters, active/waiting/overdue counts, SLA
- Table with per-chatter status and warning row highlighting

### REST endpoint used

- `GET /api/monitor/snapshot/`

### WebSocket endpoint

```
ws://localhost:8000/ws/monitor/?token=<access_token>
```

Client events: `monitor.refresh`

Server events: `monitor.snapshot`, `error`

## Lead dialogs

The `/lead/dialogs` route provides assignment management for teamleads and admins:

- List all fan dialogs with filters (search, status, assigned chatter)
- Summary cards for total dialogs, waiting, overdue, and online chatters
- Select a dialog to view details in the assignment panel
- Compare chatter workload before assigning
- Assign or reassign dialogs to any chatter

Refresh reloads both the dialog list and workload data. Assignment updates the local row and reloads workload counts.

### REST endpoints used

- `GET /api/lead/conversations/`
- `GET /api/lead/conversations/{id}/`
- `POST /api/lead/conversations/{id}/assign/`
- `GET /api/lead/chatters/workload/`

## Reconnect and resync behavior

WebSocket connections are live events only. After a disconnect, the frontend reconnects automatically and uses REST to recover missed state.

### WebSocket auto reconnect

Both chat and monitor sockets use a shared `SocketClient` with:

- connection states: `idle`, `connecting`, `connected`, `disconnected`, `reconnecting`, `closed`
- exponential backoff from 500ms to 5000ms with optional jitter
- manual `disconnect()` stops reconnect attempts
- unexpected close triggers reconnect when `autoReconnect` is enabled

### REST resync after reconnect

**Chat socket**

1. Refresh conversation list via `GET /api/conversations/`
2. If an active conversation is selected:
   - read latest local server message id
   - load missed messages via `GET /api/conversations/{id}/messages/?after_id=<id>`
   - resubscribe to the active dialog
   - mark conversation read when needed

**Monitor socket**

1. Reload monitor snapshot via `GET /api/monitor/snapshot/`
2. Send `monitor.refresh` over WebSocket

There is no polling. Periodic monitor snapshots from the backend continue while connected.

### Message dedupe

- Incoming server messages are deduplicated by `message.id`
- Pending outgoing messages are matched to confirmed server messages by `client_message_id`
- Pending messages are not duplicated when the server confirms them

### Heartbeat for presence

While the chat socket is connected, the frontend sends:

```json
{ "type": "presence.heartbeat" }
```

every 5 seconds (default interval). Heartbeat stops on disconnect or unmount and resumes after reconnect.

### Manual test

1. Login as `lead / password123` and open `/teamlead`.
2. Login as `chatter1 / password123` in another browser and open `/chatter`.
3. Monitor should show `chatter1` as online.
4. Simulate a fan message via the REST dev endpoint (see root README) or wait for real fan traffic.
5. Monitor waiting/overdue counts should update via WebSocket.

## Development

```bash
cp ../.env.example ../.env
npm install
npm run dev
```

Other scripts:

- `npm run build`
- `npm run preview`
- `npm run type-check`

## Environment reference

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | REST API base URL (`/api` when host reverse proxy forwards to backend) |
| `VITE_WS_BASE_URL` | Yes | WebSocket base URL (`auto` derives `ws(s)://` from browser host) |

## Production build

Production compose builds and runs the frontend container automatically:

```bash
cp ../.env.production.example ../.env
docker compose -f docker-compose.prod.yml up --build -d
```

Build args `VITE_API_BASE_URL` and `VITE_WS_BASE_URL` come from `.env`. For same-origin host nginx use `/api` and `auto`.

Local compose uses the `dev` target (Vite dev server on port 5173).
