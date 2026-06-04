import { defineStore } from "pinia";
import { ref } from "vue";

import { conversationMessages } from "@/api/endpoints";
import { http } from "@/api/http";
import type { MessagesPageResponse } from "@/types/conversations";
import type { Message } from "@/types/messages";

function sortMessages(messages: Message[]): Message[] {
  return [...messages].sort((a, b) => {
    if (a.id > 0 && b.id > 0 && a.id !== b.id) {
      return a.id - b.id;
    }
    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
  });
}

function dedupeMessages(messages: Message[]): Message[] {
  const byId = new Map<number, Message>();
  const pending: Message[] = [];

  for (const message of messages) {
    if (message.id > 0) {
      byId.set(message.id, message);
      continue;
    }
    pending.push(message);
  }

  const merged = [...byId.values()];
  for (const message of pending) {
    const exists = merged.some(
      (item) =>
        item.client_message_id &&
        message.client_message_id &&
        item.client_message_id === message.client_message_id,
    );
    if (!exists) {
      merged.push(message);
    }
  }

  return sortMessages(merged);
}

export const useMessagesStore = defineStore("messages", () => {
  const messagesByConversationId = ref<Record<number, Message[]>>({});
  const hasMoreByConversationId = ref<Record<number, boolean>>({});
  const loadingByConversationId = ref<Record<number, boolean>>({});
  const errorByConversationId = ref<Record<number, string | null>>({});
  const pendingByClientId = ref<Record<string, Message>>({});

  function getMessages(conversationId: number): Message[] {
    return messagesByConversationId.value[conversationId] ?? [];
  }

  function getLatestMessageId(conversationId: number): number | null {
    const serverMessages = getMessages(conversationId).filter((message) => message.id > 0);
    if (!serverMessages.length) {
      return null;
    }
    return serverMessages[serverMessages.length - 1].id;
  }

  function upsertMessage(message: Message): void {
    const conversationId = message.conversation;
    const current = [...(messagesByConversationId.value[conversationId] ?? [])];

    if (message.client_message_id) {
      delete pendingByClientId.value[message.client_message_id];
    }

    const normalized: Message = {
      ...message,
      local_status:
        message.local_status ??
        (message.id > 0 ? "sent" : message.local_status),
    };

    const withoutDuplicate = current.filter((item) => {
      if (normalized.id > 0 && item.id === normalized.id) {
        return false;
      }
      if (
        normalized.client_message_id &&
        item.client_message_id === normalized.client_message_id &&
        item.id !== normalized.id
      ) {
        return false;
      }
      return true;
    });

    withoutDuplicate.push(normalized);
    messagesByConversationId.value[conversationId] = dedupeMessages(withoutDuplicate);
  }

  function addPendingMessage(_conversationId: number, message: Message): void {
    if (message.client_message_id) {
      pendingByClientId.value[message.client_message_id] = message;
    }
    upsertMessage(message);
  }

  function markPendingSent(clientMessageId: string, messageId: number): void {
    const pending = pendingByClientId.value[clientMessageId];
    if (!pending) {
      return;
    }
    upsertMessage({
      ...pending,
      id: messageId,
      local_status: "sent",
    });
  }

  function markPendingFailed(clientMessageId: string): void {
    const pending = pendingByClientId.value[clientMessageId];
    if (!pending) {
      return;
    }
    upsertMessage({
      ...pending,
      local_status: "failed",
    });
  }

  async function loadInitialMessages(conversationId: number): Promise<void> {
    loadingByConversationId.value[conversationId] = true;
    errorByConversationId.value[conversationId] = null;
    try {
      const { data } = await http.get<MessagesPageResponse>(
        conversationMessages(conversationId),
        { params: { limit: 30 } },
      );
      const pending = getMessages(conversationId).filter((message) => message.id < 0);
      messagesByConversationId.value[conversationId] = dedupeMessages([
        ...data.results,
        ...pending,
      ]);
      hasMoreByConversationId.value[conversationId] = data.has_more;
    } catch {
      errorByConversationId.value[conversationId] = "Failed to load messages";
      throw new Error(errorByConversationId.value[conversationId]!);
    } finally {
      loadingByConversationId.value[conversationId] = false;
    }
  }

  async function loadOlderMessages(conversationId: number): Promise<void> {
    const current = getMessages(conversationId);
    if (!current.length || !hasMoreByConversationId.value[conversationId]) {
      return;
    }

    const oldestId = current.find((message) => message.id > 0)?.id;
    if (!oldestId) {
      return;
    }

    loadingByConversationId.value[conversationId] = true;
    errorByConversationId.value[conversationId] = null;
    try {
      const { data } = await http.get<MessagesPageResponse>(
        conversationMessages(conversationId),
        { params: { limit: 30, before_id: oldestId } },
      );
      messagesByConversationId.value[conversationId] = dedupeMessages([
        ...data.results,
        ...current,
      ]);
      hasMoreByConversationId.value[conversationId] = data.has_more;
    } catch {
      errorByConversationId.value[conversationId] = "Failed to load older messages";
    } finally {
      loadingByConversationId.value[conversationId] = false;
    }
  }

  async function loadMissedMessages(conversationId: number, afterId: number): Promise<void> {
    loadingByConversationId.value[conversationId] = true;
    errorByConversationId.value[conversationId] = null;
    try {
      const { data } = await http.get<MessagesPageResponse>(
        conversationMessages(conversationId),
        { params: { limit: 100, after_id: afterId } },
      );
      data.results.forEach((message) => upsertMessage(message));
    } catch {
      errorByConversationId.value[conversationId] = "Failed to sync missed messages";
    } finally {
      loadingByConversationId.value[conversationId] = false;
    }
  }

  function clearConversation(conversationId: number): void {
    delete messagesByConversationId.value[conversationId];
    delete hasMoreByConversationId.value[conversationId];
    delete loadingByConversationId.value[conversationId];
    delete errorByConversationId.value[conversationId];
  }

  function clear(): void {
    messagesByConversationId.value = {};
    hasMoreByConversationId.value = {};
    loadingByConversationId.value = {};
    errorByConversationId.value = {};
    pendingByClientId.value = {};
  }

  return {
    messagesByConversationId,
    hasMoreByConversationId,
    loadingByConversationId,
    errorByConversationId,
    pendingByClientId,
    getMessages,
    getLatestMessageId,
    loadInitialMessages,
    loadOlderMessages,
    loadMissedMessages,
    upsertMessage,
    addPendingMessage,
    markPendingSent,
    markPendingFailed,
    clearConversation,
    clear,
  };
});
