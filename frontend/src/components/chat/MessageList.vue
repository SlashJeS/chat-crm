<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";

import MessageBubble from "@/components/chat/MessageBubble.vue";
import type { Message } from "@/types/messages";

const props = defineProps<{
  messages: Message[];
  hasMore: boolean;
  loading: boolean;
}>();

const emit = defineEmits<{
  loadOlder: [];
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
    <div v-if="loading && hasMore" class="message-list__loading">Loading older messages...</div>
    <MessageBubble v-for="message in messages" :key="message.client_message_id ?? message.id" :message="message" />
  </div>
</template>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.message-list__loading {
  text-align: center;
  color: #666;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}
</style>
