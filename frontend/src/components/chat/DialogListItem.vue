<script setup lang="ts">
import { computed } from "vue";

import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import type { Conversation } from "@/types/conversations";
import { formatRelativeTime } from "@/utils/date";
import { getInitials } from "@/utils/initials";

const props = defineProps<{
  conversation: Conversation;
  active: boolean;
}>();

const emit = defineEmits<{
  select: [conversationId: number];
}>();

const fanInitials = computed(() => getInitials(props.conversation.fan.display_name));
const isWaiting = computed(() => props.conversation.waiting_since !== null);
</script>

<template>
  <button
    type="button"
    class="dialog-item"
    :class="{
      'dialog-item--active': active,
      'dialog-item--overdue': conversation.is_overdue,
      'dialog-item--unread': conversation.unread_count > 0,
      'dialog-item--waiting': isWaiting && !conversation.is_overdue,
    }"
    :aria-current="active ? 'true' : undefined"
    @click="emit('select', conversation.id)"
  >
    <span class="avatar avatar--sm dialog-item__avatar">{{ fanInitials }}</span>

    <div class="dialog-item__content">
      <div class="dialog-item__header">
        <span class="dialog-item__fan">{{ conversation.fan.display_name }}</span>
        <span class="dialog-item__time">{{ formatRelativeTime(conversation.last_message_at) }}</span>
      </div>
      <div class="dialog-item__model">{{ conversation.model_account.name }}</div>
      <div class="dialog-item__preview">
        {{ conversation.last_message?.text ?? "No messages yet" }}
      </div>
      <div v-if="conversation.is_overdue || isWaiting || conversation.unread_count > 0" class="dialog-item__meta">
        <OverdueBadge v-if="conversation.is_overdue" :count="1" />
        <span v-else-if="isWaiting" class="badge badge-warning">Waiting</span>
        <span v-if="conversation.unread_count > 0" class="dialog-item__unread">
          {{ conversation.unread_count }}
        </span>
      </div>
    </div>
  </button>
</template>

<style scoped>
.dialog-item {
  width: 100%;
  display: flex;
  gap: var(--space-3);
  text-align: left;
  padding: var(--space-3);
  border: none;
  border-bottom: 1px solid var(--color-border);
  border-left: 2px solid transparent;
  background: transparent;
  cursor: pointer;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast);
}

.dialog-item:hover {
  background: var(--color-surface-hover);
}

.dialog-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.dialog-item--active {
  background: var(--color-primary-soft);
  border-left-color: var(--color-primary);
}

.dialog-item--overdue:not(.dialog-item--active) {
  border-left-color: var(--color-danger);
}

.dialog-item--waiting:not(.dialog-item--active):not(.dialog-item--overdue) {
  border-left-color: var(--color-warning);
}

.dialog-item--unread .dialog-item__fan {
  font-weight: 600;
}

.dialog-item__avatar {
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.dialog-item__content {
  min-width: 0;
  flex: 1;
}

.dialog-item__header {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  align-items: baseline;
}

.dialog-item__fan {
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.875rem;
}

.dialog-item__time {
  color: var(--color-text-soft);
  font-size: 0.6875rem;
  flex-shrink: 0;
}

.dialog-item__model {
  color: var(--color-text-muted);
  font-size: 0.75rem;
  margin-top: 0.1rem;
}

.dialog-item__preview {
  margin-top: var(--space-1);
  color: var(--color-text-muted);
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dialog-item__meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.dialog-item__unread {
  margin-left: auto;
  min-width: 1.25rem;
  padding: 0.08rem 0.4rem;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-size: 0.625rem;
  font-weight: 600;
  text-align: center;
}
</style>
