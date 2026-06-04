<script setup lang="ts">
import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import type { Conversation } from "@/types/conversations";
import { formatRelativeTime } from "@/utils/date";

defineProps<{
  conversation: Conversation;
  active: boolean;
}>();

const emit = defineEmits<{
  select: [conversationId: number];
}>();
</script>

<template>
  <button
    type="button"
    class="dialog-item"
    :class="{
      'dialog-item--active': active,
      'dialog-item--overdue': conversation.is_overdue,
      'dialog-item--unread': conversation.unread_count > 0,
    }"
    @click="emit('select', conversation.id)"
  >
    <div class="dialog-item__header">
      <span class="dialog-item__fan">{{ conversation.fan.display_name }}</span>
      <span class="dialog-item__time">{{ formatRelativeTime(conversation.last_message_at) }}</span>
    </div>
    <div class="dialog-item__model">{{ conversation.model_account.name }}</div>
    <div class="dialog-item__preview">
      {{ conversation.last_message?.text ?? "No messages yet" }}
    </div>
    <div class="dialog-item__meta">
      <OverdueBadge :count="conversation.is_overdue ? 1 : 0" />
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
  padding: 0.85rem 1rem;
  border: none;
  border-bottom: 1px solid #e2e8f0;
  border-left: 3px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: background 0.15s ease;
}

.dialog-item:hover {
  background: #f1f5f9;
}

.dialog-item--active {
  background: #eff6ff;
  border-left-color: #2563eb;
}

.dialog-item--overdue:not(.dialog-item--active) {
  background: #fffafb;
}

.dialog-item--unread .dialog-item__fan {
  font-weight: 700;
}

.dialog-item__header {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: baseline;
}

.dialog-item__fan {
  font-weight: 600;
  color: #0f172a;
}

.dialog-item__time {
  color: #94a3b8;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.dialog-item__model {
  color: #64748b;
  font-size: 0.8rem;
  margin-top: 0.15rem;
}

.dialog-item__preview {
  margin-top: 0.35rem;
  color: #475569;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dialog-item__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.4rem;
}

.dialog-item__unread {
  margin-left: auto;
  min-width: 1.35rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: #2563eb;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  text-align: center;
}
</style>
