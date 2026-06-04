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
    <div v-if="!conversations.length" class="dialog-list__empty">No conversations</div>
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
  border-right: 1px solid #ddd;
  background: #fafafa;
}

.dialog-list__title {
  margin: 0;
  padding: 1rem;
  font-size: 1rem;
  border-bottom: 1px solid #eee;
}

.dialog-list__empty {
  padding: 1rem;
  color: #666;
}
</style>
