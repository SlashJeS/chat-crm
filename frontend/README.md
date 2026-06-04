# Frontend

Vue 3 frontend for CRM Chatters Demo.

## Stack

- Vue 3 (Composition API)
- Vite
- TypeScript
- Pinia
- Vue Router
- Axios

## Planned routes

| Path | View | Access |
|------|------|--------|
| `/` | Redirect to `/login` | Public |
| `/login` | LoginView | Public (guest) |
| `/chatter` | ChatterWorkspaceView | CHATTER |
| `/teamlead` | TeamleadMonitorView | TEAMLEAD, ADMIN |

## Authentication

The frontend uses JWT authentication against the Django backend.

1. User submits username and password on `/login`.
2. The app calls `POST /api/auth/token/` and stores `access` and `refresh` tokens in `localStorage`.
3. The app calls `GET /api/me/` to load the current user profile (including `role` and `display_name`).
4. The router redirects based on role:
   - `CHATTER` → `/chatter`
   - `TEAMLEAD` or `ADMIN` → `/teamlead`
5. On navigation, if a token exists but the user is not loaded, `restoreSession()` calls `/api/me/` again.
6. On logout, tokens and user state are cleared.

Test users will be created in a later step by the `seed_demo` management command.

## Development

```bash
npm install
npm run dev
```

Other scripts:

- `npm run build` — type-check and production build
- `npm run preview` — preview production build
- `npm run type-check` — run TypeScript checks only

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | REST API base URL |
| `VITE_WS_BASE_URL` | — | WebSocket base URL (future) |
