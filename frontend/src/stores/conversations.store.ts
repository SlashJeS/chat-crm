import { defineStore } from "pinia";
import { ref } from "vue";

import type { Conversation } from "@/types/conversations";

export const useConversationsStore = defineStore("conversations", () => {
  const conversations = ref<Conversation[]>([]);
  const selectedConversationId = ref<number | null>(null);

  return {
    conversations,
    selectedConversationId,
  };
});
