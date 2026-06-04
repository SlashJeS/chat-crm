# Frontend

Vue 3 frontend for CRM Chatters Demo.

## Stack

- Vue 3 (Composition API)
- Vite
- TypeScript
- Pinia
- Vue Router
- Axios

## Routes

| Path | View | Access |
|------|------|--------|
| `/` | Redirect to `/login` | Public |
| `/login` | LoginView | Public (guest) |
| `/chatter` | ChatterWorkspaceView | CHATTER |
| `/teamlead` | TeamleadMonitorView | TEAMLEAD, ADMIN |

## Authentication

The frontend uses JWT authentication against the Django backend.

1. User submits username and password on `/login`.
2. The app calls `POST /api/auth/token/` and stores tokens in `localStorage`.
3. The app calls `GET /api/me/` to load the current user profile.
4. The router redirects based on role.

Test users are created by `python manage.py seed_demo`.

## Chatter workspace

The `/chatter` route provides a functional workspace:

- Conversation list sorted by `last_message_at`
- Message history with scroll-up pagination
- WebSocket live updates for `message.created` and `conversation.updated`
- Send TEXT and PPV messages through WebSocket
- Mark conversation read when opened
- Simulate fan message button for local testing

### REST endpoints used

- `GET /api/conversations/`
- `GET /api/conversations/{id}/messages/`
- `POST /api/conversations/{id}/read/`
- `POST /api/dev/simulate-fan-message/`

### WebSocket endpoint

```
ws://localhost:8000/ws/chat/?token=<access_token>
```

Client events: `dialog.subscribe`, `dialog.unsubscribe`, `message.send`, `dialog.mark_read`

Server events: `message.created`, `conversation.updated`, `conversation.read_state.updated`

### Local testing

1. Start backend, Redis, Postgres and seed demo data.
2. Login as `chatter1 / password123`.
3. Open `/chatter`.
4. Select a conversation, send messages, send PPV, simulate fan message.

## Development

```bash
npm install
npm run dev
```

Other scripts:

- `npm run build`
- `npm run preview`
- `npm run type-check`

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | REST API base URL |
| `VITE_WS_BASE_URL` | `ws://localhost:8000` | WebSocket base URL |
