<script setup lang="ts">
import type { Message } from "@/types/messages";
import { formatDateTime, formatRelativeTime } from "@/utils/date";

defineProps<{
  message: Message;
}>();

function senderLabel(message: Message): string {
  if (message.sender_type === "FAN") {
    return "Fan";
  }
  if (message.sender_type === "SYSTEM") {
    return "System";
  }
  return "You";
}
</script>

<template>
  <div
    class="message-bubble"
    :class="{
      'message-bubble--fan': message.sender_type === 'FAN',
      'message-bubble--chatter': message.sender_type === 'CHATTER',
      'message-bubble--system': message.sender_type === 'SYSTEM',
      'message-bubble--ppv': message.message_type === 'PPV',
      'message-bubble--pending': message.local_status === 'pending',
      'message-bubble--failed': message.local_status === 'failed',
    }"
  >
    <div class="message-bubble__meta">
      <span class="message-bubble__sender">{{ senderLabel(message) }}</span>
      <span class="message-bubble__time" :title="formatDateTime(message.created_at)">
        {{ formatRelativeTime(message.created_at) }}
      </span>
      <span v-if="message.message_type === 'PPV'" class="message-bubble__ppv-chip">
        <span class="message-bubble__ppv-label">PPV</span>
        <span class="message-bubble__ppv-price">${{ message.ppv_price }}</span>
      </span>
      <span v-if="message.local_status === 'pending'" class="message-bubble__status">
        Sending…
      </span>
      <span
        v-if="message.local_status === 'failed'"
        class="message-bubble__status message-bubble__status--failed"
        role="alert"
      >
        Failed to send
      </span>
    </div>
    <div class="message-bubble__text">{{ message.text }}</div>
  </div>
</template>

<style scoped>
.message-bubble {
  max-width: min(78%, 32rem);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.message-bubble--fan {
  align-self: flex-start;
  border-bottom-left-radius: var(--radius-sm);
  background: var(--color-surface-raised);
}

.message-bubble--chatter {
  align-self: flex-end;
  border-bottom-right-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-primary-soft) 60%, var(--color-surface));
  border-color: color-mix(in srgb, var(--color-primary) 20%, var(--color-border));
}

.message-bubble--system {
  align-self: center;
  max-width: 90%;
  text-align: center;
  background: transparent;
  border-style: dashed;
  color: var(--color-text-muted);
}

.message-bubble--ppv {
  border-color: color-mix(in srgb, var(--color-primary) 25%, var(--color-border));
}

.message-bubble--pending {
  opacity: 0.7;
}

.message-bubble--failed {
  background: var(--color-danger-soft);
  border-color: color-mix(in srgb, var(--color-danger) 25%, var(--color-border));
}

.message-bubble__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.6875rem;
  color: var(--color-text-soft);
  margin-bottom: var(--space-1);
}

.message-bubble__sender {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-muted);
}

.message-bubble__ppv-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 0.05rem 0.35rem;
  border-radius: var(--radius-sm);
  background: var(--color-primary-soft);
  border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
  font-size: 0.625rem;
}

.message-bubble__ppv-label {
  font-weight: 600;
  color: var(--color-primary);
}

.message-bubble__ppv-price {
  font-weight: 600;
  color: var(--color-text-muted);
}

.message-bubble__status {
  color: var(--color-text-soft);
  font-style: italic;
}

.message-bubble__status--failed {
  color: var(--color-danger);
  font-weight: 500;
  font-style: normal;
}

.message-bubble__text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
  font-size: 0.875rem;
  color: var(--color-text);
}
</style>
