<script setup lang="ts">
import type { Message } from "@/types/messages";

defineProps<{
  message: Message;
}>();
</script>

<template>
  <div
    class="message-bubble"
    :class="{
      'message-bubble--fan': message.sender_type === 'FAN',
      'message-bubble--chatter': message.sender_type === 'CHATTER',
      'message-bubble--pending': message.local_status === 'pending',
      'message-bubble--failed': message.local_status === 'failed',
    }"
  >
    <div class="message-bubble__meta">
      <span>{{ message.sender_type }}</span>
      <span v-if="message.message_type === 'PPV'" class="message-bubble__ppv">
        PPV ${{ message.ppv_price }}
      </span>
      <span v-if="message.local_status === 'pending'" class="message-bubble__status">Sending...</span>
      <span v-if="message.local_status === 'failed'" class="message-bubble__status">Failed</span>
    </div>
    <div class="message-bubble__text">{{ message.text }}</div>
  </div>
</template>

<style scoped>
.message-bubble {
  max-width: 75%;
  padding: 0.6rem 0.8rem;
  border-radius: 0.75rem;
  margin-bottom: 0.5rem;
}

.message-bubble--fan {
  align-self: flex-start;
  background: #f1f3f5;
}

.message-bubble--chatter {
  align-self: flex-end;
  background: #dbeafe;
}

.message-bubble--pending {
  opacity: 0.7;
}

.message-bubble--failed {
  background: #fdecea;
}

.message-bubble__meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.message-bubble__ppv {
  color: #7c3aed;
  font-weight: 600;
}

.message-bubble__status {
  color: #666;
  font-style: italic;
}

.message-bubble__text {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
