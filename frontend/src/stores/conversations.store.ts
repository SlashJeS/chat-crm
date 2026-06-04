import { defineStore } from "pinia";
import { computed, ref } from "vue";

import {
  CONVERSATIONS,
  conversationRead,
} from "@/api/endpoints";
import { http } from "@/api/http";
import type { Conversation, ConversationReadState } from "@/types/conversations";

export const useConversationsStore = defineStore("conversations", () => {
  const conversationsById = ref<Record<number, Conversation>>({});
  const conversationIds = ref<number[]>([]);
  const activeConversationId = ref<number | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const conversations = computed(() =>
    conversationIds.value
      .map((id) => conversationsById.value[id])
      .filter((conversation): conversation is Conversation => Boolean(conversation))
      .sort((a, b) => {
        const aTime = a.last_message_at ?? "";
        const bTime = b.last_message_at ?? "";
        return bTime.localeCompare(aTime);
      }),
  );

  const activeConversation = computed(() => {
    if (activeConversationId.value === null) {
      return null;
    }
    return conversationsById.value[activeConversationId.value] ?? null;
  });

  function upsertConversation(conversation: Conversation): void {
    conversationsById.value[conversation.id] = conversation;
    if (!conversationIds.value.includes(conversation.id)) {
      conversationIds.value.push(conversation.id);
    }
  }

  function applyConversationUpdated(conversation: Conversation): void {
    upsertConversation(conversation);
  }

  async function loadConversations(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await http.get<Conversation[]>(CONVERSATIONS);
      conversationsById.value = {};
      conversationIds.value = [];
      data.forEach((conversation) => upsertConversation(conversation));
    } catch {
      error.value = "Failed to load conversations";
      throw new Error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function refreshConversations(): Promise<void> {
    const activeId = activeConversationId.value;
    error.value = null;
    try {
      const { data } = await http.get<Conversation[]>(CONVERSATIONS);
      conversationsById.value = {};
      conversationIds.value = [];
      data.forEach((conversation) => upsertConversation(conversation));
      activeConversationId.value = activeId;
    } catch {
      error.value = "Failed to refresh conversations";
      throw new Error(error.value);
    }
  }

  function setActiveConversation(id: number | null): void {
    activeConversationId.value = id;
  }

  async function markConversationRead(
    conversationId: number,
    lastReadMessageId?: number,
  ): Promise<void> {
    const body = lastReadMessageId
      ? { last_read_message_id: lastReadMessageId }
      : {};

    await http.post(conversationRead(conversationId), body);

    const conversation = conversationsById.value[conversationId];
    if (conversation) {
      conversationsById.value[conversationId] = {
        ...conversation,
        unread_count: 0,
      };
    }
  }

  function applyReadState(conversationId: number, unreadCount: number): void {
    const conversation = conversationsById.value[conversationId];
    if (conversation) {
      conversationsById.value[conversationId] = {
        ...conversation,
        unread_count: unreadCount,
      };
    }
  }

  function applyReadStateUpdated(
    conversationId: number,
    readState: ConversationReadState,
  ): void {
    applyReadState(conversationId, readState.unread_count);
  }

  function clear(): void {
    conversationsById.value = {};
    conversationIds.value = [];
    activeConversationId.value = null;
    isLoading.value = false;
    error.value = null;
  }

  return {
    conversationsById,
    conversationIds,
    activeConversationId,
    isLoading,
    error,
    conversations,
    activeConversation,
    loadConversations,
    refreshConversations,
    setActiveConversation,
    upsertConversation,
    applyConversationUpdated,
    markConversationRead,
    applyReadState,
    applyReadStateUpdated,
    clear,
  };
});
