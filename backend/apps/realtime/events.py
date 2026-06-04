class ClientEvents:
    DIALOG_SUBSCRIBE = "dialog.subscribe"
    DIALOG_UNSUBSCRIBE = "dialog.unsubscribe"
    MESSAGE_SEND = "message.send"
    DIALOG_MARK_READ = "dialog.mark_read"
    PRESENCE_HEARTBEAT = "presence.heartbeat"


class ServerEvents:
    CONNECTION_ACCEPTED = "connection.accepted"
    ERROR = "error"
    DIALOG_SUBSCRIBED = "dialog.subscribed"
    DIALOG_UNSUBSCRIBED = "dialog.unsubscribed"
    MESSAGE_SEND_ACK = "message.send.ack"
    DIALOG_MARK_READ_ACK = "dialog.mark_read.ack"
    MESSAGE_CREATED = "message.created"
    CONVERSATION_UPDATED = "conversation.updated"
    READ_STATE_UPDATED = "conversation.read_state.updated"
    PRESENCE_HEARTBEAT_ACK = "presence.heartbeat.ack"
    MONITOR_SNAPSHOT = "monitor.snapshot"


class ChannelEvents:
    MESSAGE_CREATED = "ws.message.created"
    CONVERSATION_UPDATED = "ws.conversation.updated"
    READ_STATE_UPDATED = "ws.read_state.updated"
    MONITOR_SNAPSHOT = "ws.monitor.snapshot"
