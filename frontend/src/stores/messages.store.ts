import { defineStore } from "pinia";
import { ref } from "vue";

import { conversationMessages } from "@/api/endpoints";
import { http } from "@/api/http";
import type { MessagesPageResponse } from "@/types/conversations";
import type { Message } from "@/types/messages";

function sortMessages(messages: Message[]): Message[] {
  return [...messages].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  );
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

  function upsertMessage(message: Message): void {
    const conversationId = message.conversation;
    const current = [...(messagesByConversationId.value[conversationId] ?? [])];

    if (message.client_message_id) {
      delete pendingByClientId.value[message.client_message_id];
    }

    const index = current.findIndex(
      (item) =>
        item.id === message.id ||
        (message.client_message_id &&
          item.client_message_id === message.client_message_id),
    );

    const normalized: Message = {
      ...message,
      local_status: message.local_status ?? "sent",
    };

    if (index >= 0) {
      current[index] = normalized;
    } else {
      current.push(normalized);
    }

    messagesByConversationId.value[conversationId] = sortMessages(current);
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
      messagesByConversationId.value[conversationId] = sortMessages(data.results);
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

    const oldestId = current[0].id;
    loadingByConversationId.value[conversationId] = true;
    errorByConversationId.value[conversationId] = null;
    try {
      const { data } = await http.get<MessagesPageResponse>(
        conversationMessages(conversationId),
        { params: { limit: 30, before_id: oldestId } },
      );
      const merged = sortMessages([...data.results, ...current]);
      const deduped = merged.filter(
        (message, index, array) => array.findIndex((item) => item.id === message.id) === index,
      );
      messagesByConversationId.value[conversationId] = deduped;
      hasMoreByConversationId.value[conversationId] = data.has_more;
    } catch {
      errorByConversationId.value[conversationId] = "Failed to load older messages";
    } finally {
      loadingByConversationId.value[conversationId] = false;
    }
  }

  async function loadMissedMessages(conversationId: number, afterId: number): Promise<void> {
    loadingByConversationId.value[conversationId] = true;
    try {
      const { data } = await http.get<MessagesPageResponse>(
        conversationMessages(conversationId),
        { params: { limit: 30, after_id: afterId } },
      );
      data.results.forEach((message) => upsertMessage(message));
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
