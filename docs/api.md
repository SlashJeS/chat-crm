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
