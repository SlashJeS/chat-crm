<script setup lang="ts">
import { computed } from "vue";

import type { LeadChatterWorkload } from "@/types/lead";
import { getInitials } from "@/utils/initials";

const props = defineProps<{
  chatter: LeadChatterWorkload;
  isCurrentAssignee?: boolean;
  isAssigning?: boolean;
}>();

const emit = defineEmits<{
  assign: [];
}>();

const initials = computed(() => getInitials(props.chatter.display_name));
const isDisabled = computed(
  () => props.isCurrentAssignee || props.isAssigning,
);
</script>

<template>
  <article
    class="workload-card"
    :class="{ 'workload-card--current': isCurrentAssignee }"
  >
    <div class="workload-card__main">
      <span class="avatar avatar--md workload-card__avatar">{{ initials }}</span>
      <div class="workload-card__info">
        <div class="workload-card__name-row">
          <span class="workload-card__name">{{ chatter.display_name }}</span>
          <span
            class="status-pill workload-card__presence"
            :class="chatter.is_online ? 'status-pill--success' : ''"
          >
            <span
              class="status-dot"
              :class="{ 'status-dot--success': chatter.is_online }"
              aria-hidden="true"
            />
            {{ chatter.is_online ? "Online" : "Offline" }}
          </span>
        </div>
        <span class="workload-card__username muted">@{{ chatter.username }}</span>
        <div class="workload-card__metrics">
          <span class="workload-card__metric">
            <strong>{{ chatter.active_conversations_count }}</strong> active
          </span>
          <span class="workload-card__metric">
            <strong>{{ chatter.waiting_conversations_count }}</strong> waiting
          </span>
          <span
            class="workload-card__metric"
            :class="{ 'workload-card__metric--danger': chatter.overdue_conversations_count > 0 }"
          >
            <strong>{{ chatter.overdue_conversations_count }}</strong> overdue
          </span>
        </div>
      </div>
    </div>

    <div class="workload-card__action">
      <span v-if="isCurrentAssignee" class="badge badge-muted">Current assignee</span>
      <button
        v-else
        type="button"
        class="btn btn-secondary"
        :disabled="isDisabled"
        @click="emit('assign')"
      >
        {{ isAssigning ? "Assigning…" : "Assign" }}
      </button>
    </div>
  </article>
</template>

<style scoped>
.workload-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.workload-card--current {
  border-color: color-mix(in srgb, var(--color-primary) 30%, var(--color-border));
  background: var(--color-primary-soft);
}

.workload-card__main {
  display: flex;
  gap: var(--space-3);
  min-width: 0;
  flex: 1;
}

.workload-card__avatar {
  flex-shrink: 0;
}

.workload-card__info {
  min-width: 0;
}

.workload-card__name-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.workload-card__name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text);
}

.workload-card__presence {
  font-size: 0.6875rem;
}

.workload-card__username {
  display: block;
  font-size: 0.75rem;
  margin-top: 0.1rem;
}

.workload-card__metrics {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.workload-card__metric {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.workload-card__metric strong {
  color: var(--color-text);
  font-weight: 600;
}

.workload-card__metric--danger strong {
  color: var(--color-danger);
}

.workload-card__action {
  flex-shrink: 0;
}
</style>
