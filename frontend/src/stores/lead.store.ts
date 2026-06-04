import { defineStore } from "pinia";
import { computed, ref } from "vue";

import {
  LEAD_CHATTERS_WORKLOAD,
  LEAD_CONVERSATIONS,
  leadConversationAssign,
} from "@/api/endpoints";
import { http } from "@/api/http";
import type {
  LeadChatterWorkload,
  LeadChatterWorkloadResponse,
  LeadConversation,
  LeadConversationFilters,
  LeadConversationListResponse,
} from "@/types/lead";

const DEFAULT_FILTERS: LeadConversationFilters = {
  search: "",
  status: "",
  assigned_chatter_id: "",
  model_account_id: "",
  limit: 50,
  offset: 0,
};

function buildFilterParams(filters: LeadConversationFilters): Record<string, string | number> {
  const params: Record<string, string | number> = {};

  if (filters.search?.trim()) {
    params.search = filters.search.trim();
  }
  if (filters.status) {
    params.status = filters.status;
  }
  if (filters.assigned_chatter_id !== "" && filters.assigned_chatter_id !== undefined) {
    params.assigned_chatter_id = filters.assigned_chatter_id;
  }
  if (filters.model_account_id !== "" && filters.model_account_id !== undefined) {
    params.model_account_id = filters.model_account_id;
  }
  if (filters.limit !== undefined) {
    params.limit = filters.limit;
  }
  if (filters.offset !== undefined) {
    params.offset = filters.offset;
  }

  return params;
}

export const useLeadStore = defineStore("lead", () => {
  const conversations = ref<LeadConversation[]>([]);
  const count = ref(0);
  const workload = ref<LeadChatterWorkload[]>([]);
  const filters = ref<LeadConversationFilters>({ ...DEFAULT_FILTERS });
  const selectedConversationId = ref<number | null>(null);
  const isLoadingConversations = ref(false);
  const isLoadingWorkload = ref(false);
  const isAssigning = ref(false);
  const error = ref<string | null>(null);
  const assignmentError = ref<string | null>(null);

  const selectedConversation = computed(() =>
    conversations.value.find((c) => c.id === selectedConversationId.value) ?? null,
  );

  const chattersSortedForAssignment = computed(() =>
    [...workload.value].sort((a, b) => {
      if (a.is_online !== b.is_online) {
        return a.is_online ? -1 : 1;
      }
      if (a.overdue_conversations_count !== b.overdue_conversations_count) {
        return a.overdue_conversations_count - b.overdue_conversations_count;
      }
      if (a.waiting_conversations_count !== b.waiting_conversations_count) {
        return a.waiting_conversations_count - b.waiting_conversations_count;
      }
      if (a.active_conversations_count !== b.active_conversations_count) {
        return a.active_conversations_count - b.active_conversations_count;
      }
      return a.display_name.localeCompare(b.display_name);
    }),
  );

  const activeDialogsCount = computed(
    () => conversations.value.filter((c) => c.status === "ACTIVE").length,
  );

  const overdueDialogsCount = computed(
    () => conversations.value.filter((c) => c.is_overdue).length,
  );

  const waitingDialogsCount = computed(
    () => conversations.value.filter((c) => c.waiting_since !== null).length,
  );

  async function loadConversations(): Promise<void> {
    isLoadingConversations.value = true;
    error.value = null;
    try {
      const { data } = await http.get<LeadConversationListResponse>(LEAD_CONVERSATIONS, {
        params: buildFilterParams(filters.value),
      });
      conversations.value = data.results;
      count.value = data.count;

      if (
        selectedConversationId.value !== null &&
        !conversations.value.some((c) => c.id === selectedConversationId.value)
      ) {
        selectedConversationId.value = null;
      }
    } catch {
      error.value = "Failed to load dialogs";
      throw new Error(error.value);
    } finally {
      isLoadingConversations.value = false;
    }
  }

  async function loadWorkload(): Promise<void> {
    isLoadingWorkload.value = true;
    try {
      const { data } = await http.get<LeadChatterWorkloadResponse>(LEAD_CHATTERS_WORKLOAD);
      workload.value = data.results;
    } catch {
      error.value = "Failed to load chatter workload";
      throw new Error(error.value);
    } finally {
      isLoadingWorkload.value = false;
    }
  }

  function setFilters(partial: Partial<LeadConversationFilters>): void {
    filters.value = {
      ...filters.value,
      ...partial,
      offset: 0,
    };
  }

  function selectConversation(id: number | null): void {
    selectedConversationId.value = id;
    assignmentError.value = null;
  }

  async function assignConversation(conversationId: number, chatterId: number): Promise<void> {
    isAssigning.value = true;
    assignmentError.value = null;
    try {
      const { data } = await http.post<LeadConversation>(leadConversationAssign(conversationId), {
        chatter_id: chatterId,
      });
      const index = conversations.value.findIndex((c) => c.id === conversationId);
      if (index !== -1) {
        conversations.value[index] = data;
      }
      await loadWorkload();
    } catch {
      assignmentError.value = "Failed to assign dialog";
      throw new Error(assignmentError.value);
    } finally {
      isAssigning.value = false;
    }
  }

  function clear(): void {
    conversations.value = [];
    count.value = 0;
    workload.value = [];
    filters.value = { ...DEFAULT_FILTERS };
    selectedConversationId.value = null;
    isLoadingConversations.value = false;
    isLoadingWorkload.value = false;
    isAssigning.value = false;
    error.value = null;
    assignmentError.value = null;
  }

  return {
    conversations,
    count,
    workload,
    filters,
    selectedConversationId,
    isLoadingConversations,
    isLoadingWorkload,
    isAssigning,
    error,
    assignmentError,
    selectedConversation,
    chattersSortedForAssignment,
    activeDialogsCount,
    overdueDialogsCount,
    waitingDialogsCount,
    loadConversations,
    loadWorkload,
    setFilters,
    selectConversation,
    assignConversation,
    clear,
  };
});
