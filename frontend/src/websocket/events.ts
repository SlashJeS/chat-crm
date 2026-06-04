export const websocketEventTypes = {
  messageCreated: "message.created",
  conversationUpdated: "conversation.updated",
  conversationReadStateUpdated: "conversation.read_state.updated",
  presenceUpdated: "presence.updated",
  monitorSnapshot: "monitor.snapshot",
  monitorChatterUpdated: "monitor.chatter_updated",
} as const;
