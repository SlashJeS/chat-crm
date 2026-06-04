# WebSocket events

## Routes

### `/ws/chat/?token=<access_token>`

JWT-authenticated WebSocket for the chatter workspace.

Connect with a valid JWT access token in the query string. Session auth is not used.

Allowed roles: `CHATTER`, `TEAMLEAD`, `ADMIN`.

### `/ws/monitor/?token=<access_token>`

JWT-authenticated WebSocket for the teamlead monitor.

Allowed roles: `TEAMLEAD`, `ADMIN` only.

On connect the server sends an initial `monitor.snapshot` and then periodic `monitor.snapshot` events every `MONITOR_REFRESH_SECONDS`.

## Channel groups

### `dialog_{conversation_id}`

Subscribers receive live message and read-state events for a conversation.

### `chatter_{user_id}`

Personal group for conversation list updates for the assigned chatter.

### `teamlead_monitor`

Teamleads and admins subscribed through `/ws/monitor/` receive live `monitor.snapshot` events.

## Chat client events

Send JSON messages with a `type` field.

### `dialog.subscribe`

```json
{
  "type": "dialog.subscribe",
  "conversation_id": 1
}
```

### `dialog.unsubscribe`

```json
{
  "type": "dialog.unsubscribe",
  "conversation_id": 1
}
```

### `message.send`

Chatter only.

```json
{
  "type": "message.send",
  "conversation_id": 1,
  "message_type": "TEXT",
  "text": "Hello",
  "ppv_price": null,
  "client_message_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### `dialog.mark_read`

```json
{
  "type": "dialog.mark_read",
  "conversation_id": 1,
  "last_read_message_id": 123
}
```

### `presence.heartbeat`

Chatter only. Updates Redis presence TTL and `last_seen_at`.

```json
{
  "type": "presence.heartbeat"
}
```

## Monitor client events

### `monitor.refresh`

Request an immediate fresh snapshot.

```json
{
  "type": "monitor.refresh"
}
```

## Chat server events

### `connection.accepted`

Sent immediately after a successful chat connection.

### `dialog.subscribed`

Acknowledgement for `dialog.subscribe`.

### `dialog.unsubscribed`

Acknowledgement for `dialog.unsubscribe`.

### `message.send.ack`

Acknowledgement for `message.send`.

### `dialog.mark_read.ack`

Acknowledgement for `dialog.mark_read`.

### `presence.heartbeat.ack`

```json
{
  "type": "presence.heartbeat.ack",
  "last_seen_at": "2026-06-04T18:00:00Z"
}
```

### `message.created`

New message in a subscribed dialog.

```json
{
  "type": "message.created",
  "message": {}
}
```

### `conversation.updated`

Conversation list item update for the assigned chatter.

```json
{
  "type": "conversation.updated",
  "conversation": {}
}
```

### `conversation.read_state.updated`

Read state change for a conversation.

```json
{
  "type": "conversation.read_state.updated",
  "conversation_id": 1,
  "read_state": {}
}
```

## Monitor server events

### `monitor.snapshot`

Full monitor snapshot for teamleads.

```json
{
  "type": "monitor.snapshot",
  "snapshot": {
    "sla_seconds": 60,
    "presence_grace_seconds": 15,
    "chatters": []
  }
}
```

Sent on connect, on `monitor.refresh`, periodically every `MONITOR_REFRESH_SECONDS`, and after conversation/presence changes.

### `error`

```json
{
  "type": "error",
  "code": "unknown_event",
  "message": "Unknown event type"
}
```

## Future events

### `presence.updated`

Not implemented yet.

### `monitor.chatter_updated`

Not implemented yet. Use `monitor.snapshot` for this step.
