<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";

import LoadingState from "@/components/common/LoadingState.vue";
import MessageBubble from "@/components/chat/MessageBubble.vue";
import type { Message } from "@/types/messages";

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
    <div v-if="loading && hasMore" class="message-list__loading">
      Loading older messages...
    </div>

    <LoadingState
      v-if="loading && !messages.length"
      message="Loading messages..."
    />

    <div v-else-if="error" class="message-list__error">
      <p>{{ error }}</p>
      <button type="button" @click="emit('retry')">Retry</button>
    </div>

    <div v-else-if="!messages.length" class="message-list__empty">
      <p>No messages yet</p>
      <span>Send a message or simulate a fan reply to start the conversation.</span>
    </div>

    <template v-else>
      <MessageBubble
        v-for="message in messages"
        :key="message.client_message_id ?? message.id"
        :message="message"
      />
    </template>
  </div>
</template>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.message-list__loading {
  text-align: center;
  color: #64748b;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.message-list__empty {
  flex: 1;
  display: grid;
  place-content: center;
  text-align: center;
  color: #64748b;
  padding: 2rem;
}

.message-list__empty p {
  margin: 0 0 0.35rem;
  font-weight: 600;
  color: #475569;
}

.message-list__empty span {
  font-size: 0.85rem;
}

.message-list__error {
  flex: 1;
  display: grid;
  place-content: center;
  text-align: center;
  color: #c0392b;
}

.message-list__error p {
  margin: 0 0 0.75rem;
}

.message-list__error button {
  padding: 0.4rem 0.85rem;
  border: 1px solid #c0392b;
  border-radius: 0.375rem;
  background: #fff;
  color: #c0392b;
  cursor: pointer;
}
</style>
