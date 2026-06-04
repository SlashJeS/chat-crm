<script setup lang="ts">
import { computed } from "vue";

import LoadingState from "@/components/common/LoadingState.vue";
import ChatterWorkloadCard from "@/components/lead/ChatterWorkloadCard.vue";
import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import { useLeadStore } from "@/stores/lead.store";
import { formatRelativeTime } from "@/utils/date";
import { getInitials } from "@/utils/initials";

const leadStore = useLeadStore();

const conversation = computed(() => leadStore.selectedConversation);
const fanInitials = computed(() =>
  conversation.value ? getInitials(conversation.value.fan.display_name) : "",
);

async function handleAssign(chatterId: number): Promise<void> {
  if (!conversation.value) {
    return;
  }
  try {
    await leadStore.assignConversation(conversation.value.id, chatterId);
  } catch {
    // error stored in store
  }
}
</script>

<template>
  <aside class="assignment-panel panel">
    <template v-if="conversation">
      <header class="assignment-panel__header">
        <h2 class="assignment-panel__title">Assign dialog</h2>
      </header>

      <section class="assignment-panel__details">
        <div class="assignment-panel__fan">
          <span class="avatar avatar--md">{{ fanInitials }}</span>
          <div>
            <div class="assignment-panel__fan-name">{{ conversation.fan.display_name }}</div>
            <div class="assignment-panel__fan-id muted">{{ conversation.fan.external_id }}</div>
          </div>
        </div>

        <dl class="assignment-panel__meta">
          <div class="assignment-panel__meta-row">
            <dt>Model</dt>
            <dd>{{ conversation.model_account.name }}</dd>
          </div>
          <div class="assignment-panel__meta-row">
            <dt>Current assignee</dt>
            <dd>{{ conversation.assigned_chatter.display_name }}</dd>
          </div>
          <div class="assignment-panel__meta-row">
            <dt>Status</dt>
            <dd>
              <span class="badge badge-muted">{{ conversation.status }}</span>
            </dd>
          </div>
          <div class="assignment-panel__meta-row">
            <dt>Waiting</dt>
            <dd>
              <span v-if="conversation.waiting_since" class="badge badge-warning">
                {{ formatRelativeTime(conversation.waiting_since) }}
              </span>
              <span v-else class="muted">—</span>
            </dd>
          </div>
          <div class="assignment-panel__meta-row">
            <dt>Overdue</dt>
            <dd>
              <OverdueBadge v-if="conversation.is_overdue" :count="1" />
              <span v-else class="muted">—</span>
            </dd>
          </div>
        </dl>

        <p v-if="conversation.last_message" class="assignment-panel__preview muted">
          {{ conversation.last_message.text }}
        </p>
      </section>

      <section class="assignment-panel__assign">
        <h3 class="assignment-panel__section-title">Assign to chatter</h3>
        <p v-if="leadStore.assignmentError" class="assignment-panel__error" role="alert">
          {{ leadStore.assignmentError }}
        </p>

        <LoadingState
          v-if="leadStore.isLoadingWorkload && !leadStore.workload.length"
          message="Loading chatters…"
          size="sm"
        />

        <div v-else class="assignment-panel__chatters">
          <ChatterWorkloadCard
            v-for="chatter in leadStore.chattersSortedForAssignment"
            :key="chatter.id"
            :chatter="chatter"
            :is-current-assignee="chatter.id === conversation.assigned_chatter.id"
            :is-assigning="leadStore.isAssigning"
            @assign="handleAssign(chatter.id)"
          />
        </div>
      </section>
    </template>

    <div v-else class="assignment-panel__empty empty-state">
      <p class="empty-state__title">Select a dialog to assign</p>
      <span class="empty-state__text">
        Choose a fan dialog from the list to review details and assign it to an available chatter.
      </span>
    </div>
  </aside>
</template>

<style scoped>
.assignment-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0;
  overflow: hidden;
  width: 100%;
  position: sticky;
  top: calc(var(--topbar-height) + var(--space-4));
  max-height: calc(100vh - var(--topbar-height) - var(--space-8));
}

@media (max-width: 1100px) {
  .assignment-panel {
    position: static;
    max-height: none;
  }
}

.assignment-panel__header {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.assignment-panel__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text);
}

.assignment-panel__details {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.assignment-panel__fan {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.assignment-panel__fan-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--color-text);
}

.assignment-panel__fan-id {
  font-size: 0.75rem;
  margin-top: 0.1rem;
}

.assignment-panel__meta {
  margin: var(--space-3) 0 0;
  display: grid;
  gap: var(--space-2);
}

.assignment-panel__meta-row {
  display: grid;
  grid-template-columns: 7rem 1fr;
  gap: var(--space-2);
  font-size: 0.8125rem;
}

.assignment-panel__meta-row dt {
  color: var(--color-text-soft);
  font-weight: 500;
}

.assignment-panel__meta-row dd {
  margin: 0;
  color: var(--color-text);
}

.assignment-panel__preview {
  margin: var(--space-3) 0 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.assignment-panel__assign {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: var(--space-3) var(--space-4);
  overflow: hidden;
}

.assignment-panel__section-title {
  margin: 0 0 var(--space-3);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  flex-shrink: 0;
}

.assignment-panel__error {
  margin: 0 0 var(--space-3);
  color: var(--color-danger);
  font-size: 0.8125rem;
  flex-shrink: 0;
}

.assignment-panel__chatters {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.assignment-panel__empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: var(--space-5) var(--space-4);
  text-align: left;
}
</style>
