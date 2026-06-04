<script setup lang="ts">
import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import type { Conversation } from "@/types/conversations";

defineProps<{
  conversation: Conversation;
  active: boolean;
}>();

const emit = defineEmits<{
  select: [conversationId: number];
}>();

function formatTime(value: string | null): string {
  if (!value) {
    return "";
  }
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
</script>

<template>
  <button
    type="button"
    class="dialog-item"
    :class="{ 'dialog-item--active': active }"
    @click="emit('select', conversation.id)"
  >
    <div class="dialog-item__header">
      <span class="dialog-item__fan">{{ conversation.fan.display_name }}</span>
      <span class="dialog-item__time">{{ formatTime(conversation.last_message_at) }}</span>
    </div>
    <div class="dialog-item__model">{{ conversation.model_account.name }}</div>
    <div class="dialog-item__preview">
      {{ conversation.last_message?.text ?? "No messages yet" }}
    </div>
    <div class="dialog-item__meta">
      <OverdueBadge :overdue="conversation.is_overdue" />
      <span v-if="conversation.unread_count > 0" class="dialog-item__unread">
        {{ conversation.unread_count }}
      </span>
    </div>
  </button>
</template>

<style scoped>
.dialog-item {
  width: 100%;
  text-align: left;
  padding: 0.75rem 1rem;
  border: none;
  border-bottom: 1px solid #eee;
  background: transparent;
  cursor: pointer;
}

.dialog-item:hover,
.dialog-item--active {
  background: #eef4ff;
}

.dialog-item__header {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.dialog-item__fan {
  font-weight: 600;
}

.dialog-item__time {
  color: #666;
  font-size: 0.8rem;
}

.dialog-item__model {
  color: #666;
  font-size: 0.85rem;
  margin-top: 0.15rem;
}

.dialog-item__preview {
  margin-top: 0.35rem;
  color: #333;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dialog-item__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
}

.dialog-item__unread {
  margin-left: auto;
  min-width: 1.25rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: #2563eb;
  color: #fff;
  font-size: 0.75rem;
  text-align: center;
}
</style>
