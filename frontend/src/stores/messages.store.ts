import { defineStore } from "pinia";
import { ref } from "vue";

import type { Message } from "@/types/messages";

export const useMessagesStore = defineStore("messages", () => {
  const messages = ref<Message[]>([]);

  return {
    messages,
  };
});
