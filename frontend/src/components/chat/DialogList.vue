<script setup lang="ts">
import AppIcon from "@/components/common/AppIcon.vue";
import DialogListItem from "@/components/chat/DialogListItem.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import type { Conversation } from "@/types/conversations";

defineProps<{
  conversations: Conversation[];
  activeConversationId: number | null;
  loading?: boolean;
  error?: string | null;
}>();

const emit = defineEmits<{
  select: [conversationId: number];
  retry: [];
}>();
</script>

<template>
  <div class="dialog-list">
    <header class="dialog-list__header">
      <div>
        <h2 class="dialog-list__title">Active dialogs</h2>
        <p class="dialog-list__help muted">Fans assigned to you, sorted by latest activity</p>
      </div>
      <span v-if="!loading" class="badge badge-muted">{{ conversations.length }}</span>
    </header>

    <div class="dialog-list__body">
      <div v-if="loading" class="dialog-list__skeletons" aria-label="Loading dialogs">
        <div v-for="n in 5" :key="n" class="dialog-list__skeleton">
          <div class="dialog-list__skeleton-avatar skeleton-block" />
          <div class="dialog-list__skeleton-lines">
            <div class="skeleton-block skeleton-block--line" />
            <div class="skeleton-block skeleton-block--line-short" />
          </div>
        </div>
      </div>

      <ErrorState
        v-else-if="error"
        title="Could not load dialogs"
        :message="error"
        retry-label="Retry"
        @retry="emit('retry')"
      />

      <div v-else-if="!conversations.length" class="dialog-list__empty empty-state">
        <div class="empty-state__icon" aria-hidden="true">
        <AppIcon name="inbox-empty" size="xl" />
        </div>
        <p class="empty-state__title">No active dialogs</p>
        <span class="empty-state__text">Your inbox will populate when fans are assigned to you.</span>
      </div>

      <DialogListItem
        v-for="conversation in conversations"
        v-else
        :key="conversation.id"
        :conversation="conversation"
        :active="conversation.id === activeConversationId"
        @select="emit('select', conversation.id)"
      />
    </div>
  </div>
</template>

<style scoped>
.dialog-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.dialog-list__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  flex-shrink: 0;
}

.dialog-list__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text);
}

.dialog-list__help {
  margin: var(--space-1) 0 0;
  font-size: 0.78rem;
}

.dialog-list__body {
  flex: 1 1 auto;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

.dialog-list__skeletons {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.dialog-list__skeleton {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
}

.dialog-list__skeleton-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  flex-shrink: 0;
}

.dialog-list__skeleton-lines {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  justify-content: center;
}

.skeleton-block {
  background: linear-gradient(
    90deg,
    var(--color-bg-soft) 0%,
    var(--color-surface-hover) 50%,
    var(--color-bg-soft) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

.skeleton-block--line {
  height: 0.75rem;
  width: 70%;
}

.skeleton-block--line-short {
  height: 0.65rem;
  width: 45%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.dialog-list__empty {
  padding: var(--space-8) var(--space-4);
}
</style>
