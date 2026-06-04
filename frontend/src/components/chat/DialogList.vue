<script setup lang="ts">
import DialogListItem from "@/components/chat/DialogListItem.vue";
import type { Conversation } from "@/types/conversations";

defineProps<{
  conversations: Conversation[];
  activeConversationId: number | null;
}>();

const emit = defineEmits<{
  select: [conversationId: number];
}>();
</script>

<template>
  <div class="dialog-list">
    <h2 class="dialog-list__title">Conversations</h2>
    <div v-if="!conversations.length" class="dialog-list__empty">
      <p>No conversations assigned</p>
      <span>Your inbox will appear here once conversations are available.</span>
    </div>
    <DialogListItem
      v-for="conversation in conversations"
      :key="conversation.id"
      :conversation="conversation"
      :active="conversation.id === activeConversationId"
      @select="emit('select', conversation.id)"
    />
  </div>
</template>

<style scoped>
.dialog-list {
  height: 100%;
  overflow-y: auto;
  background: #fafafa;
}

.dialog-list__title {
  margin: 0;
  padding: 0.85rem 1rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #334155;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.dialog-list__empty {
  padding: 2rem 1rem;
  text-align: center;
  color: #64748b;
}

.dialog-list__empty p {
  margin: 0 0 0.35rem;
  font-weight: 600;
  color: #475569;
}

.dialog-list__empty span {
  font-size: 0.85rem;
}
</style>
