import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { MONITOR_SNAPSHOT } from "@/api/endpoints";
import { http } from "@/api/http";
import type { MonitorChatter, MonitorSnapshot } from "@/types/monitor";

export const useMonitorStore = defineStore("monitor", () => {
  const snapshot = ref<MonitorSnapshot | null>(null);
  const chattersById = ref<Record<number, MonitorChatter>>({});
  const chatterIds = ref<number[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const lastUpdatedAt = ref<string | null>(null);

  const chatters = computed(() =>
    chatterIds.value
      .map((id) => chattersById.value[id])
      .filter((chatter): chatter is MonitorChatter => Boolean(chatter))
      .sort((a, b) => {
        if (a.is_online !== b.is_online) {
          return a.is_online ? -1 : 1;
        }
        if (a.overdue_conversations_count !== b.overdue_conversations_count) {
          return b.overdue_conversations_count - a.overdue_conversations_count;
        }
        if (a.waiting_conversations_count !== b.waiting_conversations_count) {
          return b.waiting_conversations_count - a.waiting_conversations_count;
        }
        if (a.active_conversations_count !== b.active_conversations_count) {
          return b.active_conversations_count - a.active_conversations_count;
        }
        return a.display_name.localeCompare(b.display_name);
      }),
  );

  const totalActiveConversations = computed(() =>
    chatters.value.reduce((sum, chatter) => sum + chatter.active_conversations_count, 0),
  );

  const totalWaitingConversations = computed(() =>
    chatters.value.reduce((sum, chatter) => sum + chatter.waiting_conversations_count, 0),
  );

  const totalOverdueConversations = computed(() =>
    chatters.value.reduce((sum, chatter) => sum + chatter.overdue_conversations_count, 0),
  );

  const onlineChattersCount = computed(() =>
    chatters.value.filter((chatter) => chatter.is_online).length,
  );

  function applySnapshot(nextSnapshot: MonitorSnapshot): void {
    snapshot.value = nextSnapshot;
    chattersById.value = {};
    chatterIds.value = [];
    nextSnapshot.chatters.forEach((chatter) => {
      chattersById.value[chatter.id] = chatter;
      chatterIds.value.push(chatter.id);
    });
    lastUpdatedAt.value = new Date().toISOString();
    error.value = null;
  }

  async function loadSnapshot(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await http.get<MonitorSnapshot>(MONITOR_SNAPSHOT);
      applySnapshot(data);
    } catch {
      error.value = "Failed to load monitor snapshot";
      throw new Error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  function clear(): void {
    snapshot.value = null;
    chattersById.value = {};
    chatterIds.value = [];
    isLoading.value = false;
    error.value = null;
    lastUpdatedAt.value = null;
  }

  return {
    snapshot,
    chattersById,
    chatterIds,
    isLoading,
    error,
    lastUpdatedAt,
    chatters,
    totalActiveConversations,
    totalWaitingConversations,
    totalOverdueConversations,
    onlineChattersCount,
    loadSnapshot,
    applySnapshot,
    clear,
  };
});
