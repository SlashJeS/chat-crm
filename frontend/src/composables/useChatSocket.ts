import { computed, ref } from "vue";

import { ACCESS_TOKEN_KEY } from "@/api/http";
import { useAuthStore } from "@/stores/auth.store";
import { useConversationsStore } from "@/stores/conversations.store";
import { useMessagesStore } from "@/stores/messages.store";
import type { SendMessagePayload } from "@/types/messages";
import type { WsServerEvent } from "@/types/websocket";
import { createSocketClient, type SocketClient } from "@/websocket/socket";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";

let socketClient: SocketClient | null = null;
let subscribedDialogId: number | null = null;

function getSocketUrl(): string {
  const auth = useAuthStore();
  const token = auth.accessToken ?? localStorage.getItem(ACCESS_TOKEN_KEY);
  return `${WS_BASE_URL}/ws/chat/?token=${token}`;
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
      conversationsStore.applyReadState(
        event.conversation_id,
        event.read_state.unread_count,
      );
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

const isConnected = ref(false);
const lastError = ref<string | null>(null);

export function useChatSocket() {
  const auth = useAuthStore();

  function ensureClient(): SocketClient {
    if (!socketClient) {
      socketClient = createSocketClient();
      socketClient.onOpen(() => {
        isConnected.value = true;
        lastError.value = null;
      });
      socketClient.onClose(() => {
        isConnected.value = false;
      });
      socketClient.onError(() => {
        lastError.value = "WebSocket connection error";
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
    if (subscribedDialogId !== null) {
      unsubscribeDialog(subscribedDialogId);
    }
    socketClient?.disconnect();
    isConnected.value = false;
  }

  function subscribeDialog(conversationId: number): void {
    if (subscribedDialogId !== null && subscribedDialogId !== conversationId) {
      unsubscribeDialog(subscribedDialogId);
    }
    subscribedDialogId = conversationId;
    const sent = ensureClient().send({
      type: "dialog.subscribe",
      conversation_id: conversationId,
    });
    if (!sent) {
      lastError.value = "WebSocket is not connected";
    }
  }

  function unsubscribeDialog(conversationId: number): void {
    ensureClient().send({
      type: "dialog.unsubscribe",
      conversation_id: conversationId,
    });
    if (subscribedDialogId === conversationId) {
      subscribedDialogId = null;
    }
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

  function markRead(conversationId: number, lastReadMessageId?: number): void {
    const payload: Record<string, unknown> = {
      type: "dialog.mark_read",
      conversation_id: conversationId,
    };
    if (lastReadMessageId !== undefined) {
      payload.last_read_message_id = lastReadMessageId;
    }
    ensureClient().send(payload);
  }

  return {
    connect,
    disconnect,
    subscribeDialog,
    unsubscribeDialog,
    sendMessage,
    markRead,
    isConnected: computed(() => isConnected.value),
    lastError: computed(() => lastError.value),
  };
}
