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
| `/teamlead` | TeamleadMonitorView | TEAMLEAD |

## Placeholder auth

Real backend authentication is not wired yet. The login page provides two temporary buttons:

- **Login as Chatter** — sets a placeholder token and role, then redirects to `/chatter`
- **Login as Teamlead** — sets a placeholder token and role, then redirects to `/teamlead`

The router guard redirects unauthenticated users to `/login` and sends each role to its allowed route.

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
