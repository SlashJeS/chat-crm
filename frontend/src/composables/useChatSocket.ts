import { computed, ref } from "vue";

import { ACCESS_TOKEN_KEY } from "@/api/http";
import { useAuthStore } from "@/stores/auth.store";
import { useConversationsStore } from "@/stores/conversations.store";
import { useMessagesStore } from "@/stores/messages.store";
import type { SendMessagePayload } from "@/types/messages";
import type { WsServerEvent } from "@/types/websocket";
import {
  connectionStateLabel,
  createSocketClient,
  type ConnectionState,
  type SocketClient,
} from "@/websocket/socket";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";
const HEARTBEAT_INTERVAL_MS = 5000;

let socketClient: SocketClient | null = null;
let subscribedDialogId: number | null = null;
let heartbeatTimer: ReturnType<typeof setInterval> | null = null;

const connectionState = ref<ConnectionState>("idle");
const reconnectAttempt = ref(0);
const lastError = ref<string | null>(null);

function getSocketUrl(): string {
  const auth = useAuthStore();
  const token = auth.accessToken ?? localStorage.getItem(ACCESS_TOKEN_KEY);
  return `${WS_BASE_URL}/ws/chat/?token=${token}`;
}

function stopHeartbeat(): void {
  if (heartbeatTimer !== null) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }
}

function startHeartbeat(client: SocketClient): void {
  stopHeartbeat();
  heartbeatTimer = setInterval(() => {
    client.send({ type: "presence.heartbeat" });
  }, HEARTBEAT_INTERVAL_MS);
}

function handleServerEvent(event: WsServerEvent): void {
  const conversationsStore = useConversationsStore();
  const messagesStore = useMessagesStore();

  switch (event.type) {
    case "message.created":
      messagesStore.upsertMessage(event.message);
      break;
    case "conversation.updated":
      conversationsStore.applyConversationUpdated(event.conversation);
      break;
    case "conversation.read_state.updated":
      conversationsStore.applyReadStateUpdated(event.conversation_id, event.read_state);
      break;
    case "message.send.ack":
      if (event.client_message_id) {
        messagesStore.markPendingSent(event.client_message_id, event.message_id);
      }
      break;
    case "error":
      lastError.value = event.message;
      break;
    default:
      break;
  }
}

async function resyncAfterReconnect(): Promise<void> {
  const conversationsStore = useConversationsStore();
  const messagesStore = useMessagesStore();

  lastError.value = null;
  await conversationsStore.refreshConversations();

  const activeId = conversationsStore.activeConversationId;
  if (activeId === null) {
    return;
  }

  const latestMessageId = messagesStore.getLatestMessageId(activeId);
  if (latestMessageId !== null) {
    await messagesStore.loadMissedMessages(activeId, latestMessageId);
  } else {
    await messagesStore.loadInitialMessages(activeId);
  }

  subscribeDialog(activeId);

  const messages = messagesStore.getMessages(activeId);
  const lastMessageId = messages.filter((message) => message.id > 0).at(-1)?.id;
  if (lastMessageId) {
    await conversationsStore.markConversationRead(activeId, lastMessageId);
    markRead(activeId, lastMessageId);
  }
}

function subscribeDialog(conversationId: number): void {
  if (subscribedDialogId !== null && subscribedDialogId !== conversationId) {
    unsubscribeDialog(subscribedDialogId);
  }
  subscribedDialogId = conversationId;
  const sent = socketClient?.send({
    type: "dialog.subscribe",
    conversation_id: conversationId,
  });
  if (!sent) {
    lastError.value = "WebSocket is not connected";
  }
}

function unsubscribeDialog(conversationId: number): void {
  socketClient?.send({
    type: "dialog.unsubscribe",
    conversation_id: conversationId,
  });
  if (subscribedDialogId === conversationId) {
    subscribedDialogId = null;
  }
}

function markRead(conversationId: number, lastReadMessageId?: number): void {
  const payload: Record<string, unknown> = {
    type: "dialog.mark_read",
    conversation_id: conversationId,
  };
  if (lastReadMessageId !== undefined) {
    payload.last_read_message_id = lastReadMessageId;
  }
  socketClient?.send(payload);
}

export function useChatSocket() {
  const auth = useAuthStore();

  function ensureClient(): SocketClient {
    if (!socketClient) {
      socketClient = createSocketClient({ autoReconnect: true });

      socketClient.onStateChange((state) => {
        connectionState.value = state;
      });

      socketClient.onOpen(() => {
        lastError.value = null;
        if (socketClient) {
          startHeartbeat(socketClient);
        }
      });

      socketClient.onClose(() => {
        stopHeartbeat();
      });

      socketClient.onReconnectAttempt((attempt) => {
        reconnectAttempt.value = attempt;
        lastError.value = `Reconnecting (${attempt})...`;
      });

      socketClient.onReconnectSuccess(async () => {
        reconnectAttempt.value = 0;
        try {
          await resyncAfterReconnect();
        } catch {
          lastError.value = "Failed to resync after reconnect";
        }
      });

      socketClient.onReconnectFailed(() => {
        lastError.value = "Unable to reconnect to chat server";
      });

      socketClient.onError(() => {
        if (connectionState.value !== "reconnecting") {
          lastError.value = "WebSocket connection error";
        }
      });

      socketClient.onMessage((data) => {
        handleServerEvent(data as unknown as WsServerEvent);
      });
    }
    return socketClient;
  }

  function connect(): void {
    if (!auth.accessToken) {
      lastError.value = "Not authenticated";
      return;
    }
    ensureClient().connect(getSocketUrl());
  }

  function disconnect(): void {
    stopHeartbeat();
    if (subscribedDialogId !== null) {
      unsubscribeDialog(subscribedDialogId);
    }
    socketClient?.disconnect();
    connectionState.value = "closed";
    reconnectAttempt.value = 0;
  }

  function sendMessage(payload: SendMessagePayload): boolean {
    const sent = ensureClient().send(payload);
    if (!sent) {
      lastError.value = "WebSocket is not connected";
      if (payload.client_message_id) {
        useMessagesStore().markPendingFailed(payload.client_message_id);
      }
    }
    return sent;
  }

  async function forceResync(): Promise<void> {
    await resyncAfterReconnect();
  }

  return {
    connect,
    disconnect,
    subscribeDialog,
    unsubscribeDialog,
    sendMessage,
    markRead,
    forceResync,
    isConnected: computed(() => connectionState.value === "connected"),
    connectionState: computed(() => connectionState.value),
    connectionLabel: computed(() => connectionStateLabel(connectionState.value)),
    reconnectAttempt: computed(() => reconnectAttempt.value),
    lastError: computed(() => lastError.value),
  };
}
