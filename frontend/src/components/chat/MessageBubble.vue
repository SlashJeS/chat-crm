<script setup lang="ts">
import type { Message } from "@/types/messages";
import { formatDateTime, formatRelativeTime } from "@/utils/date";

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
      <span class="message-bubble__sender">
        {{ message.sender_type === "FAN" ? "Fan" : "You" }}
      </span>
      <span
        class="message-bubble__time"
        :title="formatDateTime(message.created_at)"
      >
        {{ formatRelativeTime(message.created_at) }}
      </span>
      <span v-if="message.message_type === 'PPV'" class="message-bubble__ppv">
        PPV ${{ message.ppv_price }}
      </span>
      <span v-if="message.local_status === 'pending'" class="message-bubble__status">Sending...</span>
      <span v-if="message.local_status === 'failed'" class="message-bubble__status message-bubble__status--failed">
        Failed to send
      </span>
    </div>
    <div class="message-bubble__text">{{ message.text }}</div>
  </div>
</template>

<style scoped>
.message-bubble {
  max-width: 78%;
  padding: 0.65rem 0.85rem;
  border-radius: 0.85rem;
  margin-bottom: 0.65rem;
}

.message-bubble--fan {
  align-self: flex-start;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.message-bubble--chatter {
  align-self: flex-end;
  background: #dbeafe;
  border: 1px solid #bfdbfe;
}

.message-bubble--pending {
  opacity: 0.75;
}

.message-bubble--failed {
  background: #fdecea;
  border-color: #f5c2c0;
}

.message-bubble__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.6rem;
  font-size: 0.72rem;
  color: #64748b;
  margin-bottom: 0.3rem;
}

.message-bubble__sender {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.message-bubble__time {
  color: #94a3b8;
}

.message-bubble__ppv {
  color: #7c3aed;
  font-weight: 600;
}

.message-bubble__status {
  color: #64748b;
  font-style: italic;
}

.message-bubble__status--failed {
  color: #c0392b;
  font-weight: 600;
  font-style: normal;
}

.message-bubble__text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.45;
  font-size: 0.95rem;
}
</style>
