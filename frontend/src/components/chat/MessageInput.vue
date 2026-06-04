<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  disabled?: boolean;
  socketError?: string | null;
}>();

const emit = defineEmits<{
  send: [text: string];
}>();

const text = ref("");
const localError = ref<string | null>(null);

const canSend = computed(() => !props.disabled && text.value.trim().length > 0);

function handleSubmit(): void {
  const value = text.value.trim();
  if (!value || props.disabled) {
    return;
  }
  localError.value = null;
  emit("send", value);
  text.value = "";
}

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSubmit();
  }
}

function setError(message: string): void {
  localError.value = message;
}

defineExpose({ setError });
</script>

<template>
  <form class="message-input" @submit.prevent="handleSubmit">
    <label class="sr-only" for="message-input-field">Message</label>
    <textarea
      id="message-input-field"
      v-model="text"
      class="textarea message-input__textarea"
      rows="2"
      placeholder="Type a message…"
      :disabled="disabled"
      @keydown="handleKeydown"
    />
    <div class="message-input__footer">
      <div class="message-input__hints">
        <p v-if="localError || socketError" class="message-input__error" role="alert">
          {{ localError || socketError }}
        </p>
        <p v-else-if="disabled" class="message-input__hint message-input__hint--warning">
          <span class="status-dot status-dot--danger" aria-hidden="true" />
          Realtime disconnected — messaging unavailable
        </p>
        <p v-else class="message-input__hint muted">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
      <button
        type="submit"
        class="btn btn-primary message-input__send"
        :disabled="!canSend"
        aria-label="Send message"
      >
        <svg
          class="message-input__send-icon"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
        </svg>
        Send
      </button>
    </div>
  </form>
</template>

<style scoped>
.message-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  flex-shrink: 0;
}

.message-input__textarea {
  min-height: 3.25rem;
  max-height: 8rem;
}

.message-input__footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-3);
}

.message-input__hints {
  min-width: 0;
  flex: 1;
}

.message-input__send {
  flex-shrink: 0;
}

.message-input__send-icon {
  width: 1rem;
  height: 1rem;
}

.message-input__error {
  margin: 0;
  color: var(--color-danger);
  font-size: 0.82rem;
}

.message-input__hint {
  margin: 0;
  font-size: 0.78rem;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.message-input__hint--warning {
  color: var(--color-danger);
  font-weight: 600;
}
</style>
