<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";

import LoadingState from "@/components/common/LoadingState.vue";
import MessageBubble from "@/components/chat/MessageBubble.vue";
import type { Message } from "@/types/messages";
import { formatMessageDateLabel } from "@/utils/date";

const props = defineProps<{
  messages: Message[];
  hasMore: boolean;
  loading: boolean;
  error?: string | null;
}>();

const emit = defineEmits<{
  loadOlder: [];
  retry: [];
}>();

const containerRef = ref<HTMLElement | null>(null);
const shouldStickToBottom = ref(true);

function isNearTop(): boolean {
  const container = containerRef.value;
  if (!container) {
    return false;
  }
  return container.scrollTop < 80;
}

function isNearBottom(): boolean {
  const container = containerRef.value;
  if (!container) {
    return true;
  }
  return container.scrollHeight - container.scrollTop - container.clientHeight < 80;
}

async function scrollToBottom(): Promise<void> {
  await nextTick();
  const container = containerRef.value;
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function onScroll(): void {
  if (isNearTop() && props.hasMore && !props.loading) {
    emit("loadOlder");
  }
  shouldStickToBottom.value = isNearBottom();
}

function shouldShowDateSeparator(message: Message, index: number): boolean {
  const label = formatMessageDateLabel(message.created_at);
  if (!label) {
    return false;
  }
  if (index === 0) {
    return true;
  }
  const previous = props.messages[index - 1];
  if (!previous) {
    return true;
  }
  return (
    new Date(message.created_at).toDateString() !== new Date(previous.created_at).toDateString()
  );
}

watch(
  () => props.messages.length,
  async () => {
    if (shouldStickToBottom.value) {
      await scrollToBottom();
    }
  },
);

onMounted(async () => {
  await scrollToBottom();
});
</script>

<template>
  <div ref="containerRef" class="message-list" @scroll="onScroll">
    <div v-if="loading && hasMore" class="message-list__load-older">
      <span class="message-list__load-older-spinner" aria-hidden="true" />
      Loading older messages…
    </div>

    <LoadingState
      v-if="loading && !messages.length"
      message="Loading messages…"
      size="sm"
    />

    <div v-else-if="error" class="message-list__error">
      <p>{{ error }}</p>
      <button type="button" class="btn btn-danger" @click="emit('retry')">Retry</button>
    </div>

    <div v-else-if="!messages.length" class="message-list__empty empty-state">
      <p class="empty-state__title">No messages yet</p>
      <span class="empty-state__text">Send a message to start the dialog.</span>
    </div>

    <template v-else>
      <template v-for="(message, index) in messages" :key="message.client_message_id ?? message.id">
        <div
          v-if="shouldShowDateSeparator(message, index)"
          class="message-list__date"
          role="separator"
        >
          <span>{{ formatMessageDateLabel(message.created_at) }}</span>
        </div>
        <MessageBubble :message="message" />
      </template>
    </template>
  </div>
</template>

<style scoped>
.message-list {
  flex: 1 1 auto;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  background: var(--color-bg-soft);
  min-height: 0;
}

.message-list__load-older {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-2);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.8rem;
  align-self: center;
}

.message-list__load-older-spinner {
  width: 0.85rem;
  height: 0.85rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 999px;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.message-list__date {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: var(--space-3) 0;
}

.message-list__date span {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-soft);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.message-list__empty {
  flex: 1;
  display: grid;
  place-content: center;
  padding: var(--space-8);
}

.message-list__error {
  flex: 1;
  display: grid;
  place-content: center;
  text-align: center;
  color: var(--color-danger);
  gap: var(--space-3);
}

.message-list__error p {
  margin: 0;
}
</style>
