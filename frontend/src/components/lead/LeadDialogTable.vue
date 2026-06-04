<script setup lang="ts">
import { computed } from "vue";

import LoadingState from "@/components/common/LoadingState.vue";
import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import { useLeadStore } from "@/stores/lead.store";
import type { LeadConversation } from "@/types/lead";
import { formatRelativeTime } from "@/utils/date";
import { getInitials } from "@/utils/initials";

const leadStore = useLeadStore();

const selectedId = computed(() => leadStore.selectedConversationId);

function selectConversation(conversation: LeadConversation): void {
  leadStore.selectConversation(conversation.id);
}

function assignLabel(conversation: LeadConversation): string {
  return conversation.status === "ACTIVE" ? "Reassign" : "Assign";
}

function previewText(conversation: LeadConversation): string {
  return conversation.last_message?.text ?? "No messages yet";
}
</script>

<template>
  <section class="lead-table panel">
    <div v-if="leadStore.isLoadingConversations && !leadStore.conversations.length" class="lead-table__loading">
      <LoadingState message="Loading dialogs…" size="sm" />
    </div>

    <div v-else-if="!leadStore.conversations.length" class="lead-table__empty empty-state">
      <p class="empty-state__title">No dialogs found</p>
      <span class="empty-state__text">Try adjusting filters or refresh the list.</span>
    </div>

    <div v-else class="lead-table__scroll">
      <table class="lead-table__table">
        <thead>
          <tr>
            <th scope="col">Fan</th>
            <th scope="col">Model</th>
            <th scope="col">Assigned to</th>
            <th scope="col">Last message</th>
            <th scope="col">Waiting</th>
            <th scope="col">Overdue</th>
            <th scope="col">Updated</th>
            <th scope="col"><span class="sr-only">Action</span></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="conversation in leadStore.conversations"
            :key="conversation.id"
            class="lead-table__row"
            :class="{
              'lead-table__row--selected': conversation.id === selectedId,
              'lead-table__row--overdue': conversation.is_overdue,
            }"
            tabindex="0"
            @click="selectConversation(conversation)"
            @keydown.enter="selectConversation(conversation)"
          >
            <td data-label="Fan">
              <div class="lead-table__fan">
                <span class="avatar avatar--sm">{{ getInitials(conversation.fan.display_name) }}</span>
                <div>
                  <div class="lead-table__fan-name">{{ conversation.fan.display_name }}</div>
                  <div class="lead-table__fan-id muted">{{ conversation.fan.external_id }}</div>
                </div>
              </div>
            </td>
            <td data-label="Model">{{ conversation.model_account.name }}</td>
            <td data-label="Assigned to">{{ conversation.assigned_chatter.display_name }}</td>
            <td data-label="Last message">
              <span class="lead-table__preview">{{ previewText(conversation) }}</span>
            </td>
            <td data-label="Waiting">
              {{
                conversation.waiting_since
                  ? formatRelativeTime(conversation.waiting_since)
                  : "—"
              }}
            </td>
            <td data-label="Overdue">
              <OverdueBadge v-if="conversation.is_overdue" :count="1" />
              <span v-else class="muted">—</span>
            </td>
            <td data-label="Updated">
              {{ conversation.last_message_at ? formatRelativeTime(conversation.last_message_at) : "—" }}
            </td>
            <td data-label="Action">
              <button
                type="button"
                class="btn btn-ghost"
                @click.stop="selectConversation(conversation)"
              >
                {{ assignLabel(conversation) }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.lead-table {
  padding: 0;
  overflow: hidden;
  min-height: 0;
}

.lead-table__loading,
.lead-table__empty {
  padding: var(--space-8) var(--space-4);
}

.lead-table__scroll {
  overflow-x: auto;
}

.lead-table__table {
  width: 100%;
  border-collapse: collapse;
}

.lead-table__table th,
.lead-table__table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  text-align: left;
  vertical-align: middle;
}

.lead-table__table tbody tr:last-child td {
  border-bottom: none;
}

.lead-table__table th {
  background: var(--color-surface-raised);
  font-size: 0.6875rem;
  color: var(--color-text-soft);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.lead-table__row {
  cursor: pointer;
  transition: background var(--transition-fast);
}

.lead-table__row:hover {
  background: var(--color-surface-hover);
}

.lead-table__row--selected {
  background: var(--color-primary-soft);
  box-shadow: inset 2px 0 0 var(--color-primary);
}

.lead-table__row--overdue:not(.lead-table__row--selected) {
  box-shadow: inset 2px 0 0 var(--color-danger);
}

.lead-table__fan {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.lead-table__fan-name {
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--color-text);
}

.lead-table__fan-id {
  font-size: 0.75rem;
}

.lead-table__preview {
  display: block;
  max-width: 16rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

@media (max-width: 900px) {
  .lead-table__table thead {
    display: none;
  }

  .lead-table__table,
  .lead-table__table tbody,
  .lead-table__table tr {
    display: block;
  }

  .lead-table__row {
    padding: var(--space-3);
    border-bottom: 1px solid var(--color-border);
  }

  .lead-table__table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border: none;
  }

  .lead-table__table td::before {
    content: attr(data-label);
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-text-soft);
    flex-shrink: 0;
  }

  .lead-table__preview {
    max-width: 12rem;
    text-align: right;
  }
}
</style>
