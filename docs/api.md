# REST API

## Auth

### POST /api/auth/token/

Obtain JWT access and refresh tokens.

**Request body:**

```json
{
  "username": "chatter1",
  "password": "password123"
}
```

**Response:**

```json
{
  "access": "<jwt-access-token>",
  "refresh": "<jwt-refresh-token>"
}
```

### POST /api/auth/token/refresh/

Refresh JWT access token.

**Request body:**

```json
{
  "refresh": "<jwt-refresh-token>"
}
```

## Current user

### GET /api/me/

Returns the authenticated user profile.

**Headers:** `Authorization: Bearer <access-token>`

**Response:**

```json
{
  "id": 1,
  "username": "chatter1",
  "email": "chatter1@example.com",
  "role": "CHATTER",
  "display_name": "Chatter One"
}
```

## Health

### GET /api/health/

Public health check.

**Response:**

```json
{
  "status": "ok"
}
```

## Conversations

### GET /api/conversations/

List active conversations for the current user.

- **CHATTER** — assigned conversations only
- **TEAMLEAD / ADMIN** — all active conversations

**Headers:** `Authorization: Bearer <access-token>`

### GET /api/conversations/{id}/

Conversation detail.

### GET /api/conversations/{id}/messages/

Paginated message history.

**Query params:**

| Param | Description |
|-------|-------------|
| `limit` | Default 30, max 100 |
| `before_id` | Load older messages with `id < before_id` |
| `after_id` | Load newer messages with `id > after_id` |

**Response:**

```json
{
  "results": [],
  "has_more": true,
  "next_before_id": 123
}
```

### POST /api/conversations/{id}/read/

Mark conversation as read.

**Request body:**

```json
{
  "last_read_message_id": 123
}
```

If omitted, uses the conversation `last_message`.

## Teamlead monitor

### GET /api/monitor/snapshot/

Monitor snapshot for teamleads and admins.

**Headers:** `Authorization: Bearer <access-token>`

**Response:**

```json
{
  "sla_seconds": 60,
  "presence_grace_seconds": 15,
  "chatters": [
    {
      "id": 2,
      "username": "chatter1",
      "display_name": "Chatter One",
      "role": "CHATTER",
      "is_online": false,
      "active_conversations_count": 3,
      "waiting_conversations_count": 2,
      "overdue_conversations_count": 2,
      "last_seen_at": null
    }
  ]
}
```

## Lead operations

Lead endpoints for managing fan dialog assignments. Access: **TEAMLEAD** or **ADMIN** only.

### GET /api/lead/conversations/

List all fan dialogs with assignment and status metadata.

**Headers:** `Authorization: Bearer <access-token>`

**Query params:**

| Param | Description |
|-------|-------------|
| `status` | Optional: `ACTIVE` or `CLOSED` |
| `assigned_chatter_id` | Filter by assigned chatter user id |
| `model_account_id` | Filter by model account id |
| `search` | Search fan `display_name` or `external_id` |
| `limit` | Default 50, max 100 |
| `offset` | Default 0 |

**Response:**

```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "fan": {"id": 1, "external_id": "fan_001", "display_name": "Fan Alex", "avatar_url": ""},
      "model_account": {"id": 1, "name": "Model Aurora", "avatar_url": ""},
      "assigned_chatter": {"id": 2, "username": "chatter1", "display_name": "Chatter One"},
      "status": "ACTIVE",
      "last_message": null,
      "last_message_at": "2026-01-01T12:00:00Z",
      "unread_count": 0,
      "waiting_since": null,
      "last_fan_message_at": null,
      "last_chatter_message_at": null,
      "is_overdue": false,
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-01T12:00:00Z",
      "unread_count_for_assigned_chatter": 0
    }
  ]
}
```

### GET /api/lead/conversations/{id}/

Lead dialog detail. Same shape as list items.

### POST /api/lead/conversations/{id}/assign/

Assign or reassign an active conversation to a chatter.

**Request body:**

```json
{
  "chatter_id": 3
}
```

**Validation:**

- `chatter_id` must exist and belong to a user with role `CHATTER`
- Conversation must be `ACTIVE`

**Response:** Updated lead conversation object.

Realtime: publishes `conversation.updated` to old and new chatter groups and refreshes the monitor snapshot after commit.

### GET /api/lead/chatters/workload/

Chatter workload summary for assignment decisions.

**Headers:** `Authorization: Bearer <access-token>`

**Response:**

```json
{
  "results": [
    {
      "id": 2,
      "username": "chatter1",
      "display_name": "Chatter One",
      "is_online": false,
      "active_conversations_count": 3,
      "waiting_conversations_count": 2,
      "overdue_conversations_count": 2,
      "last_seen_at": null
    }
  ]
}
```

## Dev fan message simulation

### POST /api/dev/simulate-fan-message/

Simulate an incoming fan message (REST only, no WebSocket).

**Access:** TEAMLEAD, ADMIN, or any authenticated user when `DEBUG=True`.

**Request body:**

```json
{
  "conversation_id": 1,
  "text": "Hello from fan"
}
```

**Response:** Created message object (201).

## Admin user management

Admin endpoints for managing users and invite links. Access: **ADMIN** only.

### Invite flow

1. Admin creates an invite link via `POST /api/admin/invites/` (role + optional email + expiry).
2. Admin copies `invite_url` and sends it to the new team member. The URL is built from `FRONTEND_BASE_URL` in backend env (e.g. `http://localhost:5173/invite/<token>`).
3. The invitee opens the link and registers with their own username, display name, email (if not preset), and password.
4. Backend validates the token, creates the user with the invite role, and marks the invite accepted.
5. The invitee signs in at `/login` with the password they chose during registration.

No passwords are generated or returned by the invite APIs.

### GET /api/admin/users/

List all users.

**Headers:** `Authorization: Bearer <admin-access-token>`

**Query params:**

| Param | Description |
|-------|-------------|
| `search` | Search username, email, or display name |
| `role` | Filter by `CHATTER`, `TEAMLEAD`, or `ADMIN` |
| `is_active` | Filter by active status: `true` or `false` |
| `limit` | Default 50, max 100 |
| `offset` | Default 0 |

**Response:**

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_active": true,
      "is_staff": true,
      "date_joined": "2026-01-01T10:00:00Z",
      "last_login": null,
      "role": "ADMIN",
      "display_name": "Admin User",
      "last_seen_at": null,
      "profile_created_at": "2026-01-01T10:00:00Z"
    }
  ]
}
```

### GET /api/admin/users/{id}/

User detail. Same shape as list items.

### PATCH /api/admin/users/{id}/update/

Update user fields.

**Request body (all optional):**

```json
{
  "role": "TEAMLEAD",
  "display_name": "Updated Name",
  "is_active": true,
  "email": "user@example.com"
}
```

**Validation:**

- Username cannot be changed
- Admin cannot deactivate themselves
- Admin cannot remove their own `ADMIN` role

### POST /api/admin/users/{id}/deactivate/

Set `is_active=false`. Admin cannot deactivate themselves.

### POST /api/admin/users/{id}/activate/

Set `is_active=true`.

## Admin invites

### GET /api/admin/invites/

List invite links.

**Query params:**

| Param | Description |
|-------|-------------|
| `role` | Filter by invite role |
| `status` | `active`, `accepted`, `revoked`, or `expired` |
| `search` | Search invite email |
| `limit` | Default 50, max 100 |
| `offset` | Default 0 |

**Response:**

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "token": "550e8400-e29b-41d4-a716-446655440000",
      "email": "new@example.com",
      "role": "CHATTER",
      "invited_by": {"id": 5, "username": "admin", "email": "admin@example.com"},
      "accepted_by": null,
      "is_revoked": false,
      "expires_at": "2026-01-04T10:00:00Z",
      "accepted_at": null,
      "created_at": "2026-01-01T10:00:00Z",
      "is_expired": false,
      "is_accepted": false,
      "is_active_invite": true,
      "invite_url": "http://localhost:5173/invite/550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

### POST /api/admin/invites/

Create an invite link.

**Request body:**

```json
{
  "email": "new@example.com",
  "role": "CHATTER",
  "expires_in_hours": 72
}
```

**Validation:**

- `role` must be `CHATTER` or `TEAMLEAD` (ADMIN invites are rejected)
- `expires_in_hours` between 1 and 720 (default 72)

### POST /api/admin/invites/{id}/revoke/

Revoke an invite. Accepted invites cannot be revoked.

## Public invites

### GET /api/invites/{token}/

Public invite lookup (no auth required).

**Response:**

```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "email": "new@example.com",
  "role": "CHATTER",
  "expires_at": "2026-01-04T10:00:00Z",
  "is_active_invite": true,
  "status": "active"
}
```

Returns `200` with `status` of `active`, `accepted`, `revoked`, or `expired` even when the invite is no longer usable.

### POST /api/invites/{token}/accept/

Accept an invite and create a user account (no auth required).

**Request body:**

```json
{
  "username": "newchatter",
  "display_name": "New Chatter",
  "email": "new@example.com",
  "password": "user-chosen-password",
  "password_confirm": "user-chosen-password"
}
```

**Validation:**

- Invite must be active (not expired, revoked, or already accepted)
- Username must be unique
- `password` and `password_confirm` must match
- If invite has a preset email, input email must match (or omit email to use invite email)
- If invite has no preset email, email is required from the registrant
- Password must pass Django password validation
- Role is taken from the invite, not from the request body

**Response (201):**

```json
{
  "message": "Invite accepted successfully"
}
```

Does not issue JWT tokens or return passwords. The registration flow should redirect to login.
